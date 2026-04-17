"""Semantic search over the ADR corpus.

Takes a natural-language query, embeds it with Bedrock Titan, and returns
the top-K matching ADR chunks from the FAISS index built by embed_corpus.py.

    python query.py "Should I use Postgres in development?"
    python query.py --k 3 --dedupe-by-adr "why thymeleaf and not React"

By default, results are deduplicated so each ADR appears at most once
(keeping the highest-scoring chunk). Use --no-dedupe-by-adr to see all chunks.
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
from botocore.exceptions import ClientError

BEDROCK_FTU_HINT = (
    "\nBedrock AccessDeniedException. Two common causes:\n"
    "  1. First-time Anthropic Claude use in this AWS account — submit the one-time\n"
    "     First Time Use form from the Bedrock model catalog:\n"
    "       https://console.aws.amazon.com/bedrock/home#/model-catalog\n"
    "     Access is granted immediately after submission.\n"
    "  2. IAM policy missing bedrock:InvokeModel for the model in question.\n"
    "See the repo README for details.\n"
)


DEFAULT_EMBED_MODEL = os.environ.get("BEDROCK_EMBED_MODEL_ID", "amazon.titan-embed-text-v2:0")
DEFAULT_REGION = os.environ.get("AWS_REGION", "us-east-1")
EMBED_DIM = 1024


def embed_query(client, text: str, model_id: str) -> np.ndarray:
    try:
        response = client.invoke_model(
            modelId=model_id,
            body=json.dumps({"inputText": text, "dimensions": EMBED_DIM, "normalize": True}),
        )
    except ClientError as e:
        if e.response.get("Error", {}).get("Code") == "AccessDeniedException":
            print(BEDROCK_FTU_HINT, file=sys.stderr)
            sys.exit(1)
        raise
    payload = json.loads(response["body"].read())
    return np.asarray(payload["embedding"], dtype=np.float32).reshape(1, -1)


def load_metadata(path: Path) -> list[dict]:
    with path.open(encoding="utf-8") as f:
        return [json.loads(line) for line in f]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("query", help="Natural-language search query")
    parser.add_argument("--index", type=Path, default=Path("index.faiss"))
    parser.add_argument("--metadata", type=Path, default=Path("metadata.jsonl"))
    parser.add_argument("--k", type=int, default=5, help="Results to return after dedupe")
    parser.add_argument("--dedupe-by-adr", dest="dedupe", action="store_true", default=True)
    parser.add_argument("--no-dedupe-by-adr", dest="dedupe", action="store_false")
    parser.add_argument("--model", default=DEFAULT_EMBED_MODEL)
    parser.add_argument("--region", default=DEFAULT_REGION)
    parser.add_argument("--json", action="store_true", help="Emit JSON for the injection layer")
    args = parser.parse_args()

    if not args.index.exists() or not args.metadata.exists():
        print("error: index or metadata missing — run embed_corpus.py first", file=sys.stderr)
        return 1

    index = faiss.read_index(str(args.index))
    metadata = load_metadata(args.metadata)

    client = boto3.client("bedrock-runtime", region_name=args.region)
    query_vec = embed_query(client, args.query, args.model)

    pool = max(args.k * 4, 20) if args.dedupe else args.k
    scores, ids = index.search(query_vec, pool)

    results: list[dict] = []
    seen_adrs: set[str] = set()
    for score, idx in zip(scores[0].tolist(), ids[0].tolist()):
        if idx < 0:
            continue
        row = metadata[idx]
        if args.dedupe and row["adr_id"] in seen_adrs:
            continue
        seen_adrs.add(row["adr_id"])
        results.append({**row, "score": round(score, 4)})
        if len(results) >= args.k:
            break

    if args.json:
        print(json.dumps(results, indent=2, ensure_ascii=False))
    else:
        print(f'Query: "{args.query}"\n')
        for r in results:
            print(f"  {r['score']:.4f}  {r['adr_id']:<8}  {r['chunk']:<14}  {r['title']}")
            print(f"          {r['path']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
