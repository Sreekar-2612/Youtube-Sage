""" 
Embeddings + vectors stores + retrievers concept heree
"""

from typing import List
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

from src.config import EMBEDDING_MODEL, TOP_K

_embeddings = None

def get_embeddings():
    # use lazy load embedding mode once per process
    global _embeddings
    if _embeddings is None:
        _embeddings = HuggingFaceEmbeddings(model_name = EMBEDDING_MODEL)
    return _embeddings

def build_vectorstore(chunks : List[Document]) -> FAISS:
    embeddings = get_embeddings()
    return FAISS.from_documents(chunks,embeddings)

def get_retriever(vectorstore : FAISS):
    return vectorstore.as_retriever(
        search_type = "similarity",
        search_kwargs = {"k":TOP_K}
    )
