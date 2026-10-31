#!/bin/bash
set -e

# Automatically seed ChromaDB if collection or directory is missing/empty
if [ ! -d "artifacts/chroma_db" ] || [ -z "$(ls -A artifacts/chroma_db 2>/dev/null)" ]; then
    echo "[*] ChromaDB vector store not detected. Seeding policy documents..."
    python scripts/seed_vectorstore.py
else
    echo "[+] ChromaDB vector store detected. Ready."
fi

# Execute the command passed into container
exec "$@"