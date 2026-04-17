"""Ask Claude the same question twice: once with injected ADRs, once without.

Produces a side-by-side comparison that makes the value of context
engineering tangible. The 'without' run uses only a generic system prompt;
the 'with' run uses the same generic prompt plus the retrieved ADRs wrapped
in XML tags.

    python with_vs_without.py --retrieved retrieved.json --question "..."

Expects retrieved.json from ../02-retrieval/query.py --json.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

import boto3

from build_prompt import (
    SYSTEM_PROMPT as CE_SYSTEM_PROMPT,
    build_context,
    build_user_message,
    call_bedrock,
)

DEFAULT_MODEL_ID = os.environ.get(
    "BEDROCK_MODEL_ID", "us.anthropic.claude-sonnet-4-5-20250929-v1:0"
)
DEFAULT_REGION = os.environ.get("AWS_REGION", "us-east-1")

GENERIC_SYSTEM_PROMPT = """You are a helpful architecture assistant for a PetClinic
engineering team. Answer the user's question as clearly as you can."""

RULE = "\n" + ("─" * 72) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--retrieved", type=Path, required=True)
    parser.add_argument("--question", required=True)
    parser.add_argument("--token-budget", type=int, default=8000)
    parser.add_argument("--model", default=DEFAULT_MODEL_ID)
    parser.add_argument("--region", default=DEFAULT_REGION)
    args = parser.parse_args()

    retrieved = json.loads(args.retrieved.read_text(encoding="utf-8"))
    context, included = build_context(retrieved, args.token_budget)

    without = call_bedrock(
        GENERIC_SYSTEM_PROMPT, args.question, args.model, args.region
    )
    with_ctx = call_bedrock(
        CE_SYSTEM_PROMPT, build_user_message(args.question, context), args.model, args.region
    )

    print(f'Question: "{args.question}"')
    print(RULE + "WITHOUT context engineering (generic prompt)" + RULE)
    print(without["text"])
    print(RULE + f"WITH context engineering ({len(included)} ADRs injected)" + RULE)
    print(with_ctx["text"])
    print(RULE + "ADRs injected" + RULE)
    for a in included:
        print(f"  {a['adr_id']:<8}  score={a['score']:.4f}  {a['title']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
