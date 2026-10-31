import os
import sys
from pathlib import Path

# Add project root to path so modules can be imported
sys.path.append(str(Path(__file__).resolve().parent.parent))

from app.core.vectorstore import get_embedding_function
from langchain_chroma import Chroma
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

DOCS_DIR = "data/underwriting_policies"
PERSIST_DIR = "artifacts/chroma_db"


def seed_database():
    print(f"[*] Inspecting policy documents in: {DOCS_DIR}")
    if not os.path.exists(DOCS_DIR):
        raise FileNotFoundError(f"Directory {DOCS_DIR} does not exist.")

    # 1. Load markdown policy documents
    loader = DirectoryLoader(
        DOCS_DIR,
        glob="**/*.md",
        loader_cls=TextLoader,
        loader_kwargs={"encoding": "utf-8"},
    )
    documents = loader.load()
    print(f"[+] Loaded {len(documents)} raw policy document(s).")

    # 2. Split documents into semantic chunks
    # 400 characters captures individual policy clauses; 40 characters overlap prevents split sentences.
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=400,
        chunk_overlap=40,
        separators=["\n## ", "\n### ", "\n\n", "\n", " "],
    )
    chunks = text_splitter.split_documents(documents)
    print(f"[+] Generated {len(chunks)} contextual chunk(s).")

    # 3. Embed & Persist into ChromaDB locally at $0 cost
    print(
        f"[*] Initializing embeddings (sentence-transformers/all-MiniLM-L6-v2) & writing to {PERSIST_DIR}..."
    )
    embedding_fn = get_embedding_function()

    # Re-create/overwrite collection
    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embedding_fn,
        persist_directory=PERSIST_DIR,
        collection_name="underwriting_policies",
    )

    print("[SUCCESS] Policy knowledge base seeded and persisted locally.")

    # 4. Verification retrieval test
    test_query = "What is the surcharge for tobacco users?"
    results = vectorstore.similarity_search(test_query, k=1)
    print(f"\n[Validation Test Query]: '{test_query}'")
    if results:
        print(f"[Top Retrieved Chunk]:\n{results[0].page_content}")
    else:
        print("[!] No documents retrieved. Verification failed.")


if __name__ == "__main__":
    seed_database()