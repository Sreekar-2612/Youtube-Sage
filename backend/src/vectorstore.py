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
    global _embeddings
    if _embeddings is None:
        force_lightweight = os.getenv("FORCE_LIGHTWEIGHT_EMBEDDINGS", "false").lower() == "true"
        if not force_lightweight:
            try:
                # Load real sentence-transformers embeddings (384-dimensional dense semantic vectors)
                _embeddings = HuggingFaceEmbeddings(
                    model_name=EMBEDDING_MODEL,
                    model_kwargs={"device": "cpu"},
                    encode_kwargs={"normalize_embeddings": True}
                )
            except Exception as e:
                import logging
                logging.getLogger(__name__).warning(f"Failed to load {EMBEDDING_MODEL}, falling back to lightweight: {e}")
                _embeddings = LightweightEmbeddings()
        else:
            _embeddings = LightweightEmbeddings()
    return _embeddings

import math
from collections import Counter
from langchain_core.retrievers import BaseRetriever
from pydantic import Field


class BM25KeywordRetriever(BaseRetriever):
    """Pure-Python BM25 keyword retriever without external binary dependencies."""
    docs: List[Document] = Field(default_factory=list)
    doc_freqs: List[Counter] = Field(default_factory=list)
    idf: dict = Field(default_factory=dict)
    doc_lens: List[int] = Field(default_factory=list)
    avgdl: float = 0.0
    k1: float = 1.5
    b: float = 0.75

    @classmethod
    def from_documents(cls, docs: List[Document], k1: float = 1.5, b: float = 0.75):
        def tokenize(text: str) -> List[str]:
            return re.findall(r"\w+", text.lower())

        doc_freqs = []
        doc_lens = []
        df = Counter()
        total_docs = len(docs)

        for d in docs:
            tokens = tokenize(d.page_content)
            doc_lens.append(len(tokens))
            freq = Counter(tokens)
            doc_freqs.append(freq)
            for word in freq:
                df[word] += 1

        avgdl = (sum(doc_lens) / total_docs) if total_docs > 0 else 1.0
        idf = {}
        for word, freq in df.items():
            idf[word] = math.log(1.0 + (total_docs - freq + 0.5) / (freq + 0.5))

        return cls(
            docs=docs,
            doc_freqs=doc_freqs,
            idf=idf,
            doc_lens=doc_lens,
            avgdl=avgdl,
            k1=k1,
            b=b,
        )

    def _get_relevant_documents(self, query: str) -> List[Document]:
        query_tokens = re.findall(r"\w+", query.lower())
        if not query_tokens or not self.docs:
            return self.docs[:TOP_K]

        scores = []
        for i, doc_freq in enumerate(self.doc_freqs):
            score = 0.0
            doc_len = self.doc_lens[i]
            for token in query_tokens:
                if token in doc_freq:
                    tf = doc_freq[token]
                    idf = self.idf.get(token, 0.1)
                    num = tf * (self.k1 + 1.0)
                    denom = tf + self.k1 * (1.0 - self.b + self.b * (doc_len / self.avgdl))
                    score += idf * (num / denom)
            scores.append((score, i))

        scores.sort(key=lambda x: x[0], reverse=True)
        return [self.docs[i] for score, i in scores if score > 0][:TOP_K]


class HybridRetriever(BaseRetriever):
    """
    Hybrid retriever combining dense FAISS semantic retrieval and BM25 keyword matching
    using Reciprocal Rank Fusion (RRF).
    """
    dense_retriever: BaseRetriever
    keyword_retriever: BM25KeywordRetriever
    top_k: int = TOP_K
    dense_weight: float = 0.6
    keyword_weight: float = 0.4

    def _get_relevant_documents(self, query: str) -> List[Document]:
        # 1. Fetch dense candidates
        dense_docs = self.dense_retriever.invoke(query)
        # 2. Fetch keyword candidates
        keyword_docs = self.keyword_retriever.invoke(query)

        # 3. Reciprocal Rank Fusion (RRF)
        rrf_scores = {}
        doc_map = {}

        for rank, doc in enumerate(dense_docs):
            key = (doc.metadata.get("start_seconds"), doc.page_content[:50])
            doc_map[key] = doc
            rrf_scores[key] = rrf_scores.get(key, 0.0) + self.dense_weight / (60.0 + rank + 1)

        for rank, doc in enumerate(keyword_docs):
            key = (doc.metadata.get("start_seconds"), doc.page_content[:50])
            doc_map[key] = doc
            rrf_scores[key] = rrf_scores.get(key, 0.0) + self.keyword_weight / (60.0 + rank + 1)

        # 4. Sort and return top K
        sorted_keys = sorted(rrf_scores.keys(), key=lambda k: rrf_scores[k], reverse=True)
        return [doc_map[k] for k in sorted_keys[:self.top_k]]


def build_vectorstore(chunks: List[Document]) -> FAISS:
    embeddings = get_embeddings()
    return FAISS.from_documents(chunks, embeddings)


def get_retriever(vectorstore: FAISS, chunks: List[Document] = None) -> BaseRetriever:
    dense_retriever = vectorstore.as_retriever(
        search_type="similarity",
        search_kwargs={"k": TOP_K * 2}
    )
    if not chunks:
        return dense_retriever

    keyword_retriever = BM25KeywordRetriever.from_documents(chunks)
    return HybridRetriever(
        dense_retriever=dense_retriever,
        keyword_retriever=keyword_retriever,
        top_k=TOP_K
    )
