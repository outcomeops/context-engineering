"""Embed a JSONL corpus with Bedrock Titan and persist to a local FAISS index.

Reads the corpus.jsonl produced by ../01-corpus/ingest_adrs.py. For each ADR,
writes one embedding for the whole document plus one per section (context,
decision, consequences). All vectors share a single flat FAISS index; the
metadata sidecar records which ADR and section each row maps back to.

    python embed_corpus.py --corpus ../01-corpus/corpus.jsonl

Outputs:
    index.faiss       — FAISS IndexFlatIP (cosine, vectors L2-normalized)
    metadata.jsonl    — per-row metadata, same order as the index
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

import boto3
import faiss
import numpy as np

DEFAULT_EMBED_MODEL = os.environ.get("BEDROCK_EMBED_MODEL_ID", "amazon.titan-embed-text-v2:0")
DEFAULT_REGION = os.environ.get("AWS_REGION", "us-east-1")
EMBED_DIM = 1024


def embed_text(client, text: str, model_id: str) -> np.ndarray:
    response = client.invoke_model(
        modelId=model_id,
        body=json.dumps({"inputText": text, "dimensions": EMBED_DIM, "normalize": True}),
    )
    payload = json.loads(response["body"].read())
    return np.asarray(payload["embedding"], dtype=np.float32)


def rows_for_adr(adr: dict) -> list[dict]:
    rows = [{
        "adr_id": adr["id"],
        "title": adr["title"],
        "status": adr["status"],
        "date": adr.get("date"),
        "path": adr["path"],
        "chunk": "full",
        "text": adr["raw"],
    }]
    for section_name, body in (adr.get("sections") or {}).items():
        if not body.strip():
            continue
        rows.append({
            "adr_id": adr["id"],
            "title": adr["title"],
            "status": adr["status"],
            "date": adr.get("date"),
            "path": adr["path"],
            "chunk": section_name,
            "text": body,
        })
    return rows


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--corpus", type=Path, default=Path("../01-corpus/corpus.jsonl"))
    parser.add_argument("--index", type=Path, default=Path("index.faiss"))
    parser.add_argument("--metadata", type=Path, default=Path("metadata.jsonl"))
    parser.add_argument("--model", default=DEFAULT_EMBED_MODEL)
    parser.add_argument("--region", default=DEFAULT_REGION)
    args = parser.parse_args()

    if not args.corpus.exists():
        print(f"error: {args.corpus} not found — run ../01-corpus/ingest_adrs.py first", file=sys.stderr)
        return 1

    client = boto3.client("bedrock-runtime", region_name=args.region)
    index = faiss.IndexFlatIP(EMBED_DIM)
    vectors: list[np.ndarray] = []
    metadata: list[dict] = []

    with args.corpus.open(encoding="utf-8") as f:
        for line in f:
            adr = json.loads(line)
            for row in rows_for_adr(adr):
                vector = embed_text(client, row["text"], args.model)
                vectors.append(vector)
                metadata.append({k: v for k, v in row.items() if k != "text"})
                print(f"  {row['adr_id']:<8}  {row['chunk']:<14}  {row['title']}")

    matrix = np.vstack(vectors)
    index.add(matrix)
    faiss.write_index(index, str(args.index))

    with args.metadata.open("w", encoding="utf-8") as f:
        for row in metadata:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

    print(f"\nIndexed {len(vectors)} chunks from {len(set(m['adr_id'] for m in metadata))} ADRs")
    print(f"  index:    {args.index}")
    print(f"  metadata: {args.metadata}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
