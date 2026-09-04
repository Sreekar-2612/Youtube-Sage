"""Embeddings, vector stores, and retrievers."""

import hashlib
import os
import re
from typing import List

from langchain_core.embeddings import Embeddings
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

from src.config import EMBEDDING_MODEL, TOP_K

_embeddings = None


class LightweightEmbeddings(Embeddings):
    """Small deterministic embeddings that do not require a PyTorch model."""

    dimensions = 384

    def _embed(self, text: str) -> List[float]:
        vector = [0.0] * self.dimensions
        tokens = re.findall(r"[a-z0-9]+", text.lower())
        for token in tokens:
            index = int.from_bytes(hashlib.sha256(token.encode()).digest()[:4], "big") % self.dimensions
            vector[index] += 1.0

        magnitude = sum(value * value for value in vector) ** 0.5
        return [value / magnitude for value in vector] if magnitude else vector

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return [self._embed(text) for text in texts]

    def embed_query(self, text: str) -> List[float]:
        return self._embed(text)


def get_embeddings():
    # Render's small instances cannot reliably hold the PyTorch model in memory.
    global _embeddings
    if _embeddings is None:
        use_sentence_transformer = os.getenv("USE_SENTENCE_TRANSFORMER", "false").lower() == "true"
        _embeddings = (
            HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
            if use_sentence_transformer
            else LightweightEmbeddings()
        )
    return _embeddings

def build_vectorstore(chunks : List[Document]) -> FAISS:
    embeddings = get_embeddings()
    return FAISS.from_documents(chunks,embeddings)

def get_retriever(vectorstore : FAISS):
    return vectorstore.as_retriever(
        search_type = "similarity",
        search_kwargs = {"k":TOP_K}
    )
