"""Generate an ADR from a git diff using Claude on Amazon Bedrock.

Usage:
    git diff HEAD~1 HEAD | python generate_adr_from_diff.py --title "Short title"
    python generate_adr_from_diff.py --diff-file my.patch --title "Short title"

This is the pattern for bootstrapping a corpus from a codebase that has none.
See: https://www.outcomeops.ai/blogs/ai-generated-adrs-from-zero-documentation-to-queryable-architecture
"""

from __future__ import annotations

import argparse
import datetime as _dt
import os
import sys
from pathlib import Path

import boto3

DEFAULT_MODEL_ID = os.environ.get(
    "BEDROCK_MODEL_ID", "us.anthropic.claude-sonnet-4-5-20250929-v1:0"
)
DEFAULT_REGION = os.environ.get("AWS_REGION", "us-east-1")

SYSTEM_PROMPT = """You are an architecture documentation assistant. You read code diffs and produce
Architectural Decision Records (ADRs) in the Michael Nygard format.

An ADR you produce must follow this exact structure:

# ADR-NNN: <title>

Status: Proposed
Date: <today>

## Context
<2-4 paragraphs describing the forces at play — technical, organizational, or
business constraints that made this decision necessary. Reference specific
files, functions, or patterns from the diff.>

## Decision
<1-2 paragraphs stating what was decided, in active voice. Be specific about
the chosen approach.>

## Consequences
<Bulleted list of consequences, both positive and negative. Include what
becomes easier, what becomes harder, and what future decisions this
constrains.>

Rules:
- Infer the decision from the diff; do not guess about things the diff does not show
- If the diff is trivial (formatting, typo), say so and produce a minimal ADR
- Never invent file paths, class names, or dependencies not present in the diff
- Keep the whole ADR under 500 words
"""


def build_user_message(diff: str, title: str | None) -> str:
    title_hint = f"\nProposed title: {title}\n" if title else ""
    today = _dt.date.today().isoformat()
    return f"""Produce an ADR for the following git diff. Use {today} as the Date.{title_hint}

<diff>
{diff}
</diff>
"""


def generate_adr(diff: str, title: str | None, model_id: str, region: str) -> str:
    client = boto3.client("bedrock-runtime", region_name=region)
    response = client.converse(
        modelId=model_id,
        system=[{"text": SYSTEM_PROMPT}],
        messages=[{"role": "user", "content": [{"text": build_user_message(diff, title)}]}],
        inferenceConfig={"maxTokens": 2048, "temperature": 0.2},
    )
    return response["output"]["message"]["content"][0]["text"]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--title", help="Proposed ADR title (hint to the model)")
    parser.add_argument("--diff-file", type=Path, help="Read diff from file instead of stdin")
    parser.add_argument("--out", type=Path, help="Write the ADR to this file instead of stdout")
    parser.add_argument("--model", default=DEFAULT_MODEL_ID, help="Bedrock model id")
    parser.add_argument("--region", default=DEFAULT_REGION, help="AWS region")
    args = parser.parse_args()

    if args.diff_file:
        diff = args.diff_file.read_text(encoding="utf-8")
    elif not sys.stdin.isatty():
        diff = sys.stdin.read()
    else:
        print("error: provide a diff via stdin or --diff-file", file=sys.stderr)
        return 1

    if not diff.strip():
        print("error: empty diff", file=sys.stderr)
        return 1

    adr = generate_adr(diff, args.title, args.model, args.region)

    if args.out:
        args.out.write_text(adr, encoding="utf-8")
        print(f"wrote {args.out}", file=sys.stderr)
    else:
        sys.stdout.write(adr)
        if not adr.endswith("\n"):
            sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
