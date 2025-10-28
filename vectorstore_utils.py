from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from typing import List


def create_faiss_index(texts: List[str]):
    """
    Create a FAISS index from a list of texts.
    """
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")
    vectorstore = FAISS.from_texts(texts, embeddings)
    return vectorstore


def retrive_relevant_docs(vectorstore: FAISS, query: str, k: int = 4):
    """
    Retrieve top-k relevant documents from the FAISS index.
    """
    return vectorstore.similarity_search(query, k=k)
