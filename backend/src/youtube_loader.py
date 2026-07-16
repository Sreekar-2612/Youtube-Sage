"""
Document Loaders concept.

LangChain's core idea: any data source becomes a list of `Document` objects
(page_content + metadata) so downstream code never cares where the text
came from. Here we write a small CUSTOM loader (subclassing BaseLoader)
instead of relying purely on the built-in YoutubeLoader, so you can explain
in an interview exactly how a loader is implemented internally.
"""
import re
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
    """Custom Document Loader for YouTube transcripts."""

    def __init__(self, video_url: str, languages: List[str] = None):
        self.video_id = extract_video_id(video_url)
        self.languages = languages or ["en"]

    def load(self) -> List[Document]:
        api = YouTubeTranscriptApi()
        try:
            transcript = api.fetch(self.video_id, languages=self.languages)
            transcript_list = transcript.to_raw_data()
        except TranscriptsDisabled:
            raise RuntimeError("Transcripts are disabled for this video.")
        except Exception:
            try:
                transcripts = api.list(self.video_id)
                first_transcript = next(iter(transcripts))
                transcript_list = first_transcript.fetch().to_raw_data()
            except Exception as e:
                raise RuntimeError(f"Could not retrieve transcript for video {self.video_id}: {str(e)}")

        full_text = " ".join(chunk["text"] for chunk in transcript_list)

        # One Document per video; the text splitter downstream will chunk it.
        # We keep timestamped chunks in metadata for potential future features
        # (e.g. jump-to-timestamp), which is a nice thing to mention in an interview.
        doc = Document(
            page_content=full_text,
            metadata={
                "source": f"https://www.youtube.com/watch?v={self.video_id}",
                "video_id": self.video_id,
                "num_transcript_segments": len(transcript_list),
            },
        )
        return [doc]