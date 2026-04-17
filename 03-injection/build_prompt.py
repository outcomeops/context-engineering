"""Assemble a structured prompt from retrieved ADRs and call Claude on Bedrock.

Consumes the JSON output of ../02-retrieval/query.py --json. Loads each cited
ADR's full text from disk (the retrieval step returns metadata, not bodies),
drops the lowest-score ADRs if the token budget would be exceeded, and wraps
everything in XML tags that Claude treats as structural rather than prose.

Typical flow:

    python ../02-retrieval/query.py --json "Why are we using H2 in dev?" > retrieved.json
    python build_prompt.py --retrieved retrieved.json --question "Why are we using H2 in dev?"

Dry run (print the assembled prompt without calling Bedrock):

    python build_prompt.py --retrieved retrieved.json --question "..." --dry-run
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

import boto3

DEFAULT_MODEL_ID = os.environ.get(
    "BEDROCK_MODEL_ID", "us.anthropic.claude-sonnet-4-5-20250929-v1:0"
)
DEFAULT_REGION = os.environ.get("AWS_REGION", "us-east-1")

# Claude averages ~3.5 chars per token for English technical prose. Slight
# undercount (i.e. treats text as denser) so we stay under budget.
CHARS_PER_TOKEN = 3.5

SYSTEM_PROMPT = """You are an architecture assistant for the PetClinic engineering team.

Use the ADRs provided below to answer the user's question. Cite the ADR id
(e.g., ADR-002) for every claim you rely on. If none of the ADRs cover the
question, say so explicitly rather than guessing from general knowledge.

Keep answers grounded in what the ADRs actually say. Do not invent
consequences, dates, or alternatives that are not in the provided text."""


def estimate_tokens(text: str) -> int:
    return int(len(text) / CHARS_PER_TOKEN) + 1


def load_adr_body(path: str) -> str:
    return Path(path).read_text(encoding="utf-8")


def format_adr_block(adr_id: str, body: str) -> str:
    return f'<adr id="{adr_id}">\n{body.strip()}\n</adr>'


def build_context(retrieved: list[dict], token_budget: int) -> tuple[str, list[dict]]:
    seen: set[str] = set()
    included: list[dict] = []
    blocks: list[str] = []
    tokens_used = 0

    for row in retrieved:
        if row["adr_id"] in seen:
            continue
        seen.add(row["adr_id"])
        body = load_adr_body(row["path"])
        block = format_adr_block(row["adr_id"], body)
        cost = estimate_tokens(block)
        if tokens_used + cost > token_budget:
            continue
        blocks.append(block)
        included.append({**row, "tokens": cost})
        tokens_used += cost

    context = "<adrs>\n" + "\n\n".join(blocks) + "\n</adrs>" if blocks else "<adrs></adrs>"
    return context, included


def build_user_message(question: str, context: str) -> str:
    return f"{context}\n\nQuestion: {question}"


def call_bedrock(system: str, user: str, model_id: str, region: str) -> dict:
    client = boto3.client("bedrock-runtime", region_name=region)
    response = client.converse(
        modelId=model_id,
        system=[{"text": system}],
        messages=[{"role": "user", "content": [{"text": user}]}],
        inferenceConfig={"maxTokens": 1024, "temperature": 0.2},
    )
    return {
        "text": response["output"]["message"]["content"][0]["text"],
        "usage": response.get("usage", {}),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--retrieved", type=Path, required=True, help="JSON from query.py --json")
    parser.add_argument("--question", required=True, help="The user's question")
    parser.add_argument("--token-budget", type=int, default=8000, help="Token budget for injected ADRs")
    parser.add_argument("--dry-run", action="store_true", help="Print the assembled prompt and exit")
    parser.add_argument("--model", default=DEFAULT_MODEL_ID)
    parser.add_argument("--region", default=DEFAULT_REGION)
    args = parser.parse_args()

    retrieved = json.loads(args.retrieved.read_text(encoding="utf-8"))
    context, included = build_context(retrieved, args.token_budget)
    user_message = build_user_message(args.question, context)

    if args.dry_run:
        print("=== system ===\n" + SYSTEM_PROMPT)
        print("\n=== user ===\n" + user_message)
        print(f"\n=== budget ===\ninjected: {len(included)} ADRs, {sum(a['tokens'] for a in included)} tokens (budget {args.token_budget})")
        for a in included:
            print(f"  {a['adr_id']:<8}  {a['tokens']:>5}t  score={a['score']:.4f}  {a['title']}")
        return 0

    result = call_bedrock(SYSTEM_PROMPT, user_message, args.model, args.region)
    print(result["text"])
    usage = result["usage"]
    if usage:
        print(f"\n---\ntokens: {usage.get('inputTokens')} in / {usage.get('outputTokens')} out", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
