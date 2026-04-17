"""CI-style check: does a PR's cited ADRs actually match what the diff does?

Two layers:

  1. STATIC  — every ADR id the PR cites must exist in the corpus. This
     catches hallucinated citations and typos with no LLM call.

  2. JUDGE   — asks Claude on Bedrock to read the diff alongside each cited
     ADR and return a verdict (consistent / inconsistent / not-applicable)
     with a one-sentence rationale. A single inconsistent verdict fails the
     check.

Exit codes mirror CI conventions:
  0  all checks passed
  1  runtime error (missing inputs, etc.)
  2  one or more checks failed — the commit should be blocked

Usage:

    python check_pr_cites_adrs.py \\
        --pr ../04-output/pr.json \\
        --diff diff.patch \\
        --corpus ../01-corpus/corpus.jsonl
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

JUDGE_SYSTEM_PROMPT = """You review pull requests for consistency with architectural
decision records (ADRs). You will receive a diff and a single ADR the PR
claims to respect, extend, override, or be informed by. Return a verdict.

You MUST call the `submit_verdict` tool with exactly one of:
  - "consistent"       — the diff matches the claimed relationship
  - "inconsistent"     — the diff contradicts the ADR under the claimed relationship
  - "not-applicable"   — the ADR is not actually relevant to this diff

Special handling for overrides: if the PR claims "overrides", the verdict is
"consistent" only when the note gives a genuine justification for breaking
with the prior decision. An unjustified override is "inconsistent"."""


VERDICT_TOOL = {
    "toolSpec": {
        "name": "submit_verdict",
        "description": "Submit a consistency verdict for one cited ADR.",
        "inputSchema": {
            "json": {
                "type": "object",
                "required": ["verdict", "rationale"],
                "additionalProperties": False,
                "properties": {
                    "verdict": {
                        "type": "string",
                        "enum": ["consistent", "inconsistent", "not-applicable"],
                    },
                    "rationale": {
                        "type": "string",
                        "description": "One sentence explaining the verdict, referencing specific parts of the diff or ADR.",
                    },
                },
            }
        },
    }
}


def load_corpus(path: Path) -> dict[str, dict]:
    corpus: dict[str, dict] = {}
    with path.open(encoding="utf-8") as f:
        for line in f:
            adr = json.loads(line)
            corpus[adr["id"]] = adr
    return corpus


def static_check(pr: dict, corpus: dict[str, dict]) -> list[str]:
    problems: list[str] = []
    cited = pr.get("cited_adrs") or []
    if not cited:
        problems.append("PR cites no ADRs (cited_adrs is empty)")
    for c in cited:
        adr_id = c.get("adr_id", "")
        if adr_id not in corpus:
            problems.append(f"cited ADR {adr_id!r} does not exist in the corpus")
    return problems


def judge_one(client, diff: str, pr_citation: dict, adr: dict, model_id: str) -> dict:
    user = (
        f'<adr id="{adr["id"]}">\n{adr["raw"].strip()}\n</adr>\n\n'
        f'<pr-citation>\n'
        f'  adr_id: {pr_citation["adr_id"]}\n'
        f'  relationship: {pr_citation["relationship"]}\n'
        f'  note: {pr_citation["note"]}\n'
        f'</pr-citation>\n\n'
        f"<diff>\n{diff}\n</diff>\n\n"
        f"Return a verdict."
    )
    response = client.converse(
        modelId=model_id,
        system=[{"text": JUDGE_SYSTEM_PROMPT}],
        messages=[{"role": "user", "content": [{"text": user}]}],
        toolConfig={"tools": [VERDICT_TOOL], "toolChoice": {"tool": {"name": "submit_verdict"}}},
        inferenceConfig={"maxTokens": 512, "temperature": 0.0},
    )
    for block in response["output"]["message"]["content"]:
        if "toolUse" in block:
            return block["toolUse"]["input"]
    raise RuntimeError("judge did not return a verdict")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--pr", type=Path, required=True, help="Structured PR JSON from 04-output")
    parser.add_argument("--diff", type=Path, required=True, help="The diff the PR describes")
    parser.add_argument("--corpus", type=Path, required=True, help="ADR corpus JSONL")
    parser.add_argument("--skip-judge", action="store_true", help="Run only the static check")
    parser.add_argument("--model", default=DEFAULT_MODEL_ID)
    parser.add_argument("--region", default=DEFAULT_REGION)
    args = parser.parse_args()

    pr = json.loads(args.pr.read_text(encoding="utf-8"))
    diff = args.diff.read_text(encoding="utf-8")
    corpus = load_corpus(args.corpus)

    print(f"Checking {len(pr.get('cited_adrs', []))} cited ADR(s) against corpus of {len(corpus)}")

    static_problems = static_check(pr, corpus)
    for p in static_problems:
        print(f"  STATIC FAIL: {p}")
    if static_problems:
        return 2

    print("  STATIC PASS: all cited ADRs exist in the corpus")

    if args.skip_judge:
        return 0

    client = boto3.client("bedrock-runtime", region_name=args.region)
    failed = False
    for c in pr["cited_adrs"]:
        verdict = judge_one(client, diff, c, corpus[c["adr_id"]], args.model)
        marker = {"consistent": "PASS", "inconsistent": "FAIL", "not-applicable": "WARN"}[verdict["verdict"]]
        print(f"  JUDGE {marker}: {c['adr_id']} ({c['relationship']}) — {verdict['rationale']}")
        if verdict["verdict"] == "inconsistent":
            failed = True

    return 2 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
