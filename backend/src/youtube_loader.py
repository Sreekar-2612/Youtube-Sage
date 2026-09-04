"""
Document Loaders concept.

LangChain's core idea: any data source becomes a list of `Document` objects
(page_content + metadata) so downstream code never cares where the text
came from. Here we write a small CUSTOM loader (subclassing BaseLoader)
instead of relying purely on the built-in YoutubeLoader, so you can explain
in an interview exactly how a loader is implemented internally.
"""
import re
import urllib.request
import json
import logging
from typing import List
from urllib.parse import parse_qs, urlparse

from langchain_core.documents import Document
from langchain_community.document_loaders.base import BaseLoader

logger = logging.getLogger(__name__)


def extract_video_id(url_or_id: str) -> str:
    """Accepts a full YouTube URL or a bare video ID and returns the video ID."""
    value = url_or_id.strip()
    if re.fullmatch(r"[0-9A-Za-z_-]{11}", value):
        return value

    # Accept links copied from watch, shorts, live, embed, mobile, and youtu.be.
    parsed = urlparse(value if "://" in value else f"https://{value}")
    hostname = (parsed.hostname or "").lower().removeprefix("www.")
    if hostname == "youtu.be":
        candidate = parsed.path.strip("/").split("/")[0]
    elif hostname == "youtube.com" or hostname.endswith(".youtube.com"):
        query_id = parse_qs(parsed.query).get("v", [""])[0]
        path_parts = [part for part in parsed.path.split("/") if part]
        candidate = query_id
        if not candidate and len(path_parts) >= 2 and path_parts[0] in {"embed", "shorts", "live", "v"}:
            candidate = path_parts[1]
    else:
        candidate = ""

    if re.fullmatch(r"[0-9A-Za-z_-]{11}", candidate):
        return candidate
    raise ValueError("Could not extract a valid YouTube video ID from input.")


class YouTubeTranscriptLoader(BaseLoader):
    """Custom Document Loader for YouTube transcripts with cloud resilience fallbacks."""

    def __init__(self, video_url: str, languages: List[str] = None):
        self.video_id = extract_video_id(video_url)
        self.languages = languages or ["en"]

    def _fetch_from_youtube_transcript_api(self) -> tuple[str, int]:
        """Tier 1: Try youtube-transcript-api (supports both v0.x and v1.x)."""
        try:
            from youtube_transcript_api import YouTubeTranscriptApi
        except ImportError:
            raise RuntimeError("youtube-transcript-api is not installed.")

        api = YouTubeTranscriptApi()

        # Try specified languages first, then fall back to any available
        try:
            transcript = api.fetch(self.video_id, languages=self.languages)
        except Exception:
            # If specified language not found, try listing all available transcripts
            try:
                transcript_list = api.list(self.video_id)
                # v1.x: iterate to find first available
                first_transcript = next(iter(transcript_list))
                transcript = first_transcript.fetch()
            except Exception as inner_e:
                raise RuntimeError(
                    f"No transcript found for video {self.video_id}: {inner_e}"
                )

        # v1.x returns FetchedTranscript which is iterable with .text, .start, .duration
        # v0.x returns an object with .snippets or .to_raw_data()
        full_text_parts = []
        num_segments = 0

        # Handle both API versions
        if hasattr(transcript, 'to_raw_data'):
            # v0.x API
            raw = transcript.to_raw_data()
            full_text_parts = [chunk["text"] for chunk in raw]
            num_segments = len(raw)
        else:
            # v1.x API - FetchedTranscript is iterable
            for snippet in transcript:
                full_text_parts.append(snippet.text)
                num_segments += 1

        if not full_text_parts:
            raise RuntimeError(f"Transcript for {self.video_id} was empty.")

        full_text = " ".join(full_text_parts)
        return full_text, num_segments

    def _fetch_from_fallback_service(self) -> tuple[str, int]:
        """Tier 2: Fallback via cloud-resilient transcript services."""
        errors = []

        # Attempt 1: youtube-transcript.ai
        try:
            url = f"https://youtube-transcript.ai/transcript/{self.video_id}.txt"
            req = urllib.request.Request(
                url,
                headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
                    "Accept-Language": "en-US,en;q=0.9",
                },
            )
            with urllib.request.urlopen(req, timeout=15) as resp:
                raw_text = resp.read().decode("utf-8")

            lines = raw_text.splitlines()
            cleaned = []
            for line in lines:
                l = line.strip()
                if (
                    not l
                    or l.startswith("#")
                    or l.startswith("Source video:")
                    or l.startswith("Language:")
                    or l.startswith("Other available")
                    or l.startswith("To request")
                    or l.startswith("Interactive version")
                    or l.startswith("Powered by")
                    or l.startswith("--- Generated by")
                ):
                    continue
                # Remove timestamp prefixes like [00:15] or [00:15:30]
                cleaned.append(re.sub(r"^\[\d+:\d+(?::\d+)?\]\s*", "", l))

            # Deduplicate: youtube-transcript.ai returns overlapping subtitle segments
            # where the same phrase appears 2-3 times consecutively (both within and across lines).
            # Join all text, then remove repeating word sequences.
            full_text = " ".join(cleaned)
            words = full_text.split()
            deduped_words = []
            i = 0
            while i < len(words):
                found_dup = False
                for chunk_size in range(1, min(20, (len(words) - i) // 2 + 1)):
                    chunk = tuple(words[i:i + chunk_size])
                    reps = 1
                    j = i + chunk_size
                    while j + chunk_size <= len(words) and tuple(words[j:j + chunk_size]) == chunk:
                        reps += 1
                        j += chunk_size
                    if reps >= 2:
                        deduped_words.extend(chunk)
                        i = j
                        found_dup = True
                        break
                if not found_dup:
                    deduped_words.append(words[i])
                    i += 1

            if deduped_words:
                deduped_text = " ".join(deduped_words)
                return deduped_text, len(deduped_words)
            else:
                errors.append("youtube-transcript.ai returned empty content")
        except Exception as e:
            errors.append(f"youtube-transcript.ai: {e}")

        raise RuntimeError(
            f"All fallback transcript services failed for video {self.video_id}. "
            f"Errors: {' | '.join(errors)}"
        )

    def load(self) -> List[Document]:
        full_text = None
        num_segments = 0

        # Tier 1: Try standard YouTubeTranscriptApi
        try:
            logger.info(f"Fetching transcript for video {self.video_id} via API...")
            full_text, num_segments = self._fetch_from_youtube_transcript_api()
            logger.info(f"Successfully fetched transcript ({num_segments} segments) via API")
        except Exception as e:
            logger.warning(f"Primary API failed for {self.video_id}: {e}")
            # Tier 2: Fall back to cloud-resilient scraper service
            try:
                logger.info(f"Trying fallback service for video {self.video_id}...")
                full_text, num_segments = self._fetch_from_fallback_service()
                logger.info(f"Successfully fetched transcript ({num_segments} segments) via fallback")
            except Exception as fallback_err:
                logger.error(f"All transcript sources failed for {self.video_id}")
                raise RuntimeError(
                    f"Could not retrieve transcript for video {self.video_id}. "
                    f"Primary: {str(e)} | Fallback: {str(fallback_err)}"
                )

        doc = Document(
            page_content=full_text,
            metadata={
                "source": f"https://www.youtube.com/watch?v={self.video_id}",
                "video_id": self.video_id,
                "num_transcript_segments": num_segments,
            },
        )
        return [doc]
