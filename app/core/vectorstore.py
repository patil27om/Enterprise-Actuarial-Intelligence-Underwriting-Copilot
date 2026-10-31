import os
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

# Default persist directory
DEFAULT_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", "artifacts/chroma_db")
EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


def get_embedding_function() -> HuggingFaceEmbeddings:
    """Initializes and returns the zero-cost local HuggingFace embedding model.

    Runs 100% on CPU without requiring an API key.
    """
    return HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL_NAME,
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True},
    )


def get_vectorstore(persist_directory: str = DEFAULT_PERSIST_DIR) -> Chroma:
    """Returns a connected Chroma vector store instance targeting the local directory."""
    embedding = get_embedding_function()
    return Chroma(
        persist_directory=persist_directory,
        embedding_function=embedding,
        collection_name="underwriting_policies",
    )