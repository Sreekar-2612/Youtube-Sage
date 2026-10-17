from typing import List, Dict, Any
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from src.config import CHUNK_SIZE, CHUNK_OVERLAP


def create_timestamped_chunks(
    doc: Document,
    window_duration: float = 75.0,
    overlap_duration: float = 15.0,
) -> List[Document]:
    """
    Groups raw subtitle segments into rolling time-window chunks.
    Preserves exact start/end time and attaches formatted [MM:SS] timestamps.
    """
    segments: List[Dict[str, Any]] = doc.metadata.get("segments", [])
    if not segments:
        return []

    chunks = []
    total = len(segments)
    i = 0

    video_id = doc.metadata.get("video_id", "")
    source = doc.metadata.get("source", "")

    while i < total:
        current_texts = []
        start_time = float(segments[i].get("start", 0.0))
        end_time = start_time

        j = i
        while j < total and (float(segments[j].get("start", 0.0)) - start_time) < window_duration:
            seg = segments[j]
            seg_text = seg.get("text", "").strip()
            if seg_text:
                current_texts.append(seg_text)
            end_time = float(seg.get("start", 0.0)) + float(seg.get("duration", 0.0))
            j += 1

        if current_texts:
            minutes = int(start_time // 60)
            seconds = int(start_time % 60)
            formatted_ts = f"{minutes:02d}:{seconds:02d}"
            
            chunk_text = " ".join(current_texts)
            # Prefix text with timestamp so LLM can cite it directly
            content_with_ts = f"[{formatted_ts}] {chunk_text}"

            chunks.append(
                Document(
                    page_content=content_with_ts,
                    metadata={
                        "source": source,
                        "video_id": video_id,
                        "start_seconds": round(start_time, 2),
                        "end_seconds": round(end_time, 2),
                        "timestamp": formatted_ts,
                    },
                )
            )

        # Advance to next window taking overlap into account
        next_target = start_time + max(5.0, window_duration - overlap_duration)
        prev_i = i
        while i < total and float(segments[i].get("start", 0.0)) < next_target:
            i += 1
        if i == prev_i:
            i += 1

    return chunks


def split_documents(docs: List[Document]) -> List[Document]:
    """
    Splits documents into chunks. Prioritizes timestamp-preserving chunking
    if subtitle segments are present in metadata; falls back to recursive text splitting.
    """
    all_chunks: List[Document] = []
    fallback_docs: List[Document] = []

    for doc in docs:
        if doc.metadata.get("segments"):
            time_chunks = create_timestamped_chunks(doc)
            if time_chunks:
                all_chunks.extend(time_chunks)
                continue
        fallback_docs.append(doc)

    if fallback_docs:
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP,
            separators=["\n\n", "\n", ". ", " ", ""],
        )
        all_chunks.extend(splitter.split_documents(fallback_docs))

    return all_chunks

