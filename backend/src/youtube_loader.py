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
from typing import List

from langchain_core.documents import Document
from langchain_community.document_loaders.base import BaseLoader
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound


def extract_video_id(url_or_id: str) -> str:
    """Accepts a full YouTube URL or a bare video ID and returns the video ID."""
    patterns = [
        r"(?:v=|\/)([0-9A-Za-z_-]{11}).*",
        r"^([0-9A-Za-z_-]{11})$",
    ]
    for pattern in patterns:
        match = re.search(pattern, url_or_id)
        if match:
            return match.group(1)
    raise ValueError("Could not extract a valid YouTube video ID from input.")


class YouTubeTranscriptLoader(BaseLoader):
    """Custom Document Loader for YouTube transcripts with cloud resilience fallbacks."""

    def __init__(self, video_url: str, languages: List[str] = None):
        self.video_id = extract_video_id(video_url)
        self.languages = languages or ["en"]

    def _fetch_from_youtube_transcript_api(self) -> tuple[str, int]:
        api = YouTubeTranscriptApi()
        try:
            transcript = api.fetch(self.video_id, languages=self.languages)
            transcript_list = transcript.to_raw_data()
        except TranscriptsDisabled:
            raise RuntimeError("Transcripts are disabled for this video.")
        except Exception:
            transcripts = api.list(self.video_id)
            first_transcript = next(iter(transcripts))
            transcript_list = first_transcript.fetch().to_raw_data()

        full_text = " ".join(chunk["text"] for chunk in transcript_list)
        return full_text, len(transcript_list)

    def _fetch_from_fallback_service(self) -> tuple[str, int]:
        """Fallback for cloud server environments where YouTube blocks datacenter IPs."""
        url = f"https://youtube-transcript.ai/transcript/{self.video_id}.txt"
        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
                "Accept-Language": "en-US,en;q=0.9",
            },
        )
        with urllib.request.urlopen(req, timeout=12) as resp:
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
            ):
                continue
            # Remove timestamp prefixes like [00:15]
            cleaned.append(re.sub(r"^\[\d+:\d+(?::\d+)?\]\s*", "", l))

        if not cleaned:
            raise RuntimeError(f"No transcript content found via fallback for video {self.video_id}")

        return " ".join(cleaned), len(cleaned)

    def load(self) -> List[Document]:
        full_text = None
        num_segments = 0

        # Tier 1: Try standard YouTubeTranscriptApi
        try:
            full_text, num_segments = self._fetch_from_youtube_transcript_api()
        except Exception as e:
            # Tier 2: Fall back to cloud-resilient scraper service
            try:
                full_text, num_segments = self._fetch_from_fallback_service()
            except Exception as fallback_err:
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