import os
import sys
import json
import hashlib
from pathlib import Path
from typing import Dict, List

from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_text_splitters import (
    MarkdownHeaderTextSplitter,
    RecursiveCharacterTextSplitter,
)
from langchain_core.documents import Document

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DB_DIR = BASE_DIR / "db"
STATE_FILE = DB_DIR / "ingestion_state.json"

# Folders to parse for the Vector DB
INGEST_DIRS = ["github", "raw", "linkedin", "static"]


def get_file_hash(filepath: Path) -> str:
    with open(filepath, "r", encoding="utf-8") as f:
        return hashlib.md5(f.read().encode("utf-8")).hexdigest()


def load_state() -> Dict[str, Dict]:
    if not STATE_FILE.exists():
        return {}

    try:
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            raw_state = json.load(f)

        if isinstance(raw_state, dict) and "files" in raw_state and isinstance(raw_state["files"], dict):
            normalized = {}
            for rel_path, entry in raw_state["files"].items():
                if isinstance(entry, dict):
                    normalized[rel_path] = {
                        "hash": entry.get("hash", ""),
                        "chunk_ids": entry.get("chunk_ids", []),
                    }
            return normalized

        normalized = {}
        if isinstance(raw_state, dict):
            for rel_path, value in raw_state.items():
                if isinstance(value, str):
                    normalized[rel_path] = {
                        "hash": value,
                        "chunk_ids": [],
                    }
                elif isinstance(value, dict):
                    normalized[rel_path] = {
                        "hash": value.get("hash", ""),
                        "chunk_ids": value.get("chunk_ids", []),
                    }
        return normalized
    except Exception as e:
        print(f"[LOAD STATE ERROR] {e}")
        return {}


def save_state(state: Dict[str, Dict]) -> None:
    DB_DIR.mkdir(parents=True, exist_ok=True)
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump({"files": state}, f, indent=2)


def run_ingestion(force: bool = False):
    print("=" * 60)
    print("ArunCore Vector Knowledge Ingestion Pipeline (ChromaDB)")
    print("=" * 60)

    state = load_state()
    current_files: List[Path] = []

    for folder in INGEST_DIRS:
        target_dir = DATA_DIR / folder
        if target_dir.exists():
            for p in target_dir.rglob("*.md"):
                current_files.append(p)

    if not current_files:
        print("[WARNING] No markdown files found in data/ directories.")
        return

    openai_key = os.getenv("OPENAI_API_KEY")
    if not openai_key:
        print("[ERROR] OPENAI_API_KEY environment variable is missing.")
        sys.exit(1)

    embeddings = OpenAIEmbeddings(
        model="text-embedding-3-small",
        api_key=openai_key,
    )
    vector_store = Chroma(
        persist_directory=str(DB_DIR),
        embedding_function=embeddings,
    )

    headers_to_split_on = [
        ("#", "Header 1"),
        ("##", "Header 2"),
        ("###", "Header 3"),
    ]
    markdown_splitter = MarkdownHeaderTextSplitter(
        headers_to_split_on=headers_to_split_on,
        strip_headers=False,
    )
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=150,
    )

    processed_count = 0

    for file_path in current_files:
        rel_path = str(file_path.relative_to(BASE_DIR))
        current_hash = get_file_hash(file_path)

        stored_hash = state.get(rel_path, {}).get("hash", "")
        old_chunk_ids = state.get(rel_path, {}).get("chunk_ids", [])

        if not force and stored_hash == current_hash:
            print(f"[SKIP] {rel_path} (unchanged)")
            continue

        print(f"[INGESTING] {rel_path}...")

        if old_chunk_ids:
            try:
                vector_store.delete(ids=old_chunk_ids)
            except Exception as e:
                print(f"  └─ Warning deleting old chunk IDs: {e}")

        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        md_header_splits = markdown_splitter.split_text(content)
        splits = text_splitter.split_documents(md_header_splits)

        documents_to_add: List[Document] = []
        new_chunk_ids: List[str] = []

        folder_category = rel_path.split(os.sep)[1] if len(rel_path.split(os.sep)) > 1 else "general"

        for idx, split in enumerate(splits):
            chunk_id = f"{folder_category}_{file_path.stem}_chunk_{idx}_{current_hash[:6]}"
            new_chunk_ids.append(chunk_id)

            meta = split.metadata or {}
            meta["source"] = rel_path
            meta["category"] = folder_category
            meta["chunk_id"] = chunk_id

            doc = Document(
                page_content=split.page_content,
                metadata=meta,
            )
            documents_to_add.append(doc)

        if documents_to_add:
            vector_store.add_documents(documents_to_add, ids=new_chunk_ids)

        state[rel_path] = {
            "hash": current_hash,
            "chunk_ids": new_chunk_ids,
        }
        processed_count += 1

    save_state(state)
    print("=" * 60)
    print(f"[SUCCESS] Ingestion completed. Processed {processed_count} updated files into ChromaDB.")
    print("=" * 60)


if __name__ == "__main__":
    force_run = "--force" in sys.argv
    run_ingestion(force=force_run)
