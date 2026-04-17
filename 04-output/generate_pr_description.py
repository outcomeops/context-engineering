"""Generate a structured PR description from a diff + retrieved ADRs.

Uses Bedrock Converse tool-use to constrain Claude's output to the JSON
schema defined in schema.py. Renders the structured result as Markdown
ready to paste into a pull request.

Typical flow:

    # Retrieve the ADRs most relevant to the diff
    python ../02-retrieval/query.py --json \\
        "$(git diff --stat main..HEAD)" > retrieved.json

    # Generate the structured description
    git diff main..HEAD | python generate_pr_description.py \\
        --retrieved retrieved.json \\
        --out pr.json

    # Render it as Markdown
    python generate_pr_description.py --render pr.json
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

import boto3
from jsonschema import Draft202012Validator

from schema import PR_DESCRIPTION_SCHEMA, TOOL_SPEC

DEFAULT_MODEL_ID = os.environ.get(
    "BEDROCK_MODEL_ID", "us.anthropic.claude-sonnet-4-5-20250929-v1:0"
)
DEFAULT_REGION = os.environ.get("AWS_REGION", "us-east-1")

SYSTEM_PROMPT = """You write structured pull request descriptions for the PetClinic
engineering team. You read a code diff and the team's relevant ADRs, then
submit a PR description using the provided tool.

Rules:
- You MUST cite at least one ADR in `cited_adrs`. If the diff genuinely
  relates to none of the provided ADRs, cite the closest one with
  relationship "informed-by" and explain the gap in the note.
- Only list ADR ids that appear in the provided ADRs. Do not invent them.
- `files_changed` must reflect paths actually present in the diff.
- Use the "overrides" relationship sparingly — only when the diff deliberately
  breaks with an existing decision, and explain why in the note."""


def load_adr_block(retrieved: list[dict]) -> str:
    seen: set[str] = set()
    blocks: list[str] = []
    for row in retrieved:
        if row["adr_id"] in seen:
            continue
        seen.add(row["adr_id"])
        body = Path(row["path"]).read_text(encoding="utf-8")
        blocks.append(f'<adr id="{row["adr_id"]}">\n{body.strip()}\n</adr>')
    return "<adrs>\n" + "\n\n".join(blocks) + "\n</adrs>"


def generate(diff: str, retrieved: list[dict], model_id: str, region: str) -> dict:
    context = load_adr_block(retrieved)
    user_message = f"{context}\n\n<diff>\n{diff}\n</diff>\n\nWrite the PR description."

    client = boto3.client("bedrock-runtime", region_name=region)
    response = client.converse(
        modelId=model_id,
        system=[{"text": SYSTEM_PROMPT}],
        messages=[{"role": "user", "content": [{"text": user_message}]}],
        toolConfig={
            "tools": [TOOL_SPEC],
            "toolChoice": {"tool": {"name": "submit_pr_description"}},
        },
        inferenceConfig={"maxTokens": 2048, "temperature": 0.1},
    )

    for block in response["output"]["message"]["content"]:
        if "toolUse" in block:
            return block["toolUse"]["input"]
    raise RuntimeError("Model did not call submit_pr_description; response: " + json.dumps(response))


def validate(pr: dict) -> None:
    errors = sorted(Draft202012Validator(PR_DESCRIPTION_SCHEMA).iter_errors(pr), key=lambda e: e.path)
    if errors:
        for e in errors:
            print(f"  schema error at {list(e.path)}: {e.message}", file=sys.stderr)
        raise SystemExit(2)


def render_markdown(pr: dict) -> str:
    lines: list[str] = []
    lines.append("## Summary")
    lines.append("")
    lines.append(pr["summary"])
    lines.append("")
    lines.append("## Motivation")
    lines.append("")
    lines.append(pr["motivation"])
    lines.append("")
    lines.append("## ADRs this change relies on")
    lines.append("")
    for c in pr["cited_adrs"]:
        lines.append(f"- **{c['adr_id']}** — {c['relationship']}: {c['note']}")
    lines.append("")
    lines.append("## Files changed")
    lines.append("")
    for f in pr["files_changed"]:
        lines.append(f"- `{f}`")
    lines.append("")
    if pr["risks"]:
        lines.append("## Risks")
        lines.append("")
        for r in pr["risks"]:
            lines.append(f"- {r}")
        lines.append("")
    lines.append("## Test plan")
    lines.append("")
    for t in pr["test_plan"]:
        lines.append(f"- [ ] {t}")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--retrieved", type=Path, help="JSON from query.py --json")
    parser.add_argument("--diff-file", type=Path, help="Read diff from file instead of stdin")
    parser.add_argument("--out", type=Path, help="Write structured JSON here")
    parser.add_argument("--render", type=Path, help="Render the given JSON file as Markdown and exit")
    parser.add_argument("--model", default=DEFAULT_MODEL_ID)
    parser.add_argument("--region", default=DEFAULT_REGION)
    args = parser.parse_args()

    if args.render:
        pr = json.loads(args.render.read_text(encoding="utf-8"))
        validate(pr)
        print(render_markdown(pr))
        return 0

    if not args.retrieved:
        print("error: --retrieved is required unless --render is used", file=sys.stderr)
        return 1

    if args.diff_file:
        diff = args.diff_file.read_text(encoding="utf-8")
    elif not sys.stdin.isatty():
        diff = sys.stdin.read()
    else:
        print("error: provide a diff via stdin or --diff-file", file=sys.stderr)
        return 1

    retrieved = json.loads(args.retrieved.read_text(encoding="utf-8"))
    pr = generate(diff, retrieved, args.model, args.region)
    validate(pr)

    output = json.dumps(pr, indent=2, ensure_ascii=False)
    if args.out:
        args.out.write_text(output + "\n", encoding="utf-8")
        print(f"wrote {args.out}", file=sys.stderr)
    else:
        print(output)
    return 0


if __name__ == "__main__":
    sys.exit(main())
