"""JSON schema for structured PR description output.

This schema is used two ways:
  1. As the Bedrock Converse `toolSpec` that constrains what Claude returns.
  2. As a validator downstream — if the schema changes, both producers and
     consumers fail fast instead of diverging silently.

Downstream CI (the enforcement layer) validates against this same schema, so
a single file is the source of truth.
"""

from __future__ import annotations

PR_DESCRIPTION_SCHEMA: dict = {
    "type": "object",
    "required": ["summary", "motivation", "cited_adrs", "files_changed", "risks", "test_plan"],
    "additionalProperties": False,
    "properties": {
        "summary": {
            "type": "string",
            "description": "One or two sentences describing what this PR does. Active voice. No marketing language.",
        },
        "motivation": {
            "type": "string",
            "description": "Why this change is being made, grounded in the cited ADRs. 2-4 sentences.",
        },
        "cited_adrs": {
            "type": "array",
            "description": "ADR ids this change relies on or is constrained by. Must reference ADRs present in the input context.",
            "items": {
                "type": "object",
                "required": ["adr_id", "relationship", "note"],
                "additionalProperties": False,
                "properties": {
                    "adr_id": {"type": "string", "pattern": "^ADR-\\d+$"},
                    "relationship": {
                        "type": "string",
                        "enum": ["respects", "extends", "overrides", "informed-by"],
                        "description": "How this change relates to the ADR. 'overrides' requires justification in the note.",
                    },
                    "note": {
                        "type": "string",
                        "description": "One sentence explaining the relationship concretely.",
                    },
                },
            },
            "minItems": 1,
        },
        "files_changed": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Paths of files the PR modifies, as they appear in the diff.",
            "minItems": 1,
        },
        "risks": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Concrete risks a reviewer should check. Empty list only if the change is genuinely risk-free (rare).",
        },
        "test_plan": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Bulleted steps a reviewer can take to verify the change works.",
            "minItems": 1,
        },
    },
}


TOOL_SPEC: dict = {
    "toolSpec": {
        "name": "submit_pr_description",
        "description": "Submit a structured PR description that cites the ADRs the change relies on.",
        "inputSchema": {"json": PR_DESCRIPTION_SCHEMA},
    }
}
