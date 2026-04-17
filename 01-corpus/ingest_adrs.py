"""Ingest a directory of Markdown ADRs into a normalized JSONL corpus.

Parses each ADR file into:
    {
      "id": "ADR-001",
      "title": "Use Spring Boot as the application framework",
      "status": "Accepted",
      "date": "2026-01-15",
      "path": "sample-adrs/ADR-001-spring-boot-framework.md",
      "sections": {
        "context": "...",
        "decision": "...",
        "consequences": "..."
      },
      "raw": "<full markdown body>"
    }

The output JSONL is the input to the retrieval layer in ../02-retrieval/.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ADR_ID_RE = re.compile(r"(ADR-\d+)", re.IGNORECASE)
STATUS_RE = re.compile(r"^\s*(?:\*\*)?Status(?:\*\*)?\s*[:\-]\s*(.+?)\s*$", re.IGNORECASE | re.MULTILINE)
DATE_RE = re.compile(r"^\s*(?:\*\*)?Date(?:\*\*)?\s*[:\-]\s*(.+?)\s*$", re.IGNORECASE | re.MULTILINE)
H1_RE = re.compile(r"^#\s+(.+?)\s*$", re.MULTILINE)
SECTION_RE = re.compile(r"^##\s+(.+?)\s*$", re.MULTILINE)


def parse_adr(path: Path) -> dict:
    raw = path.read_text(encoding="utf-8")

    id_match = ADR_ID_RE.search(path.name) or ADR_ID_RE.search(raw)
    adr_id = id_match.group(1).upper() if id_match else path.stem

    h1 = H1_RE.search(raw)
    title = h1.group(1).strip() if h1 else path.stem
    title = ADR_ID_RE.sub("", title).strip(" :-—")

    status = (STATUS_RE.search(raw) or [None, "Unknown"])[1] if STATUS_RE.search(raw) else "Unknown"
    date = (DATE_RE.search(raw) or [None, None])[1] if DATE_RE.search(raw) else None

    return {
        "id": adr_id,
        "title": title,
        "status": status.strip() if isinstance(status, str) else status,
        "date": date.strip() if isinstance(date, str) else date,
        "path": str(path.resolve()),
        "sections": extract_sections(raw),
        "raw": raw,
    }


def extract_sections(raw: str) -> dict[str, str]:
    headers = [(m.start(), m.group(1).strip()) for m in SECTION_RE.finditer(raw)]
    sections: dict[str, str] = {}
    for i, (start, name) in enumerate(headers):
        end = headers[i + 1][0] if i + 1 < len(headers) else len(raw)
        body_start = raw.find("\n", start) + 1
        body = raw[body_start:end].strip()
        sections[name.lower()] = body
    return sections


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("directory", type=Path, help="Directory containing ADR Markdown files")
    parser.add_argument("--out", type=Path, default=Path("corpus.jsonl"), help="Output JSONL path")
    parser.add_argument("--glob", default="ADR-*.md", help="Glob pattern for ADR files")
    args = parser.parse_args()

    if not args.directory.is_dir():
        print(f"error: {args.directory} is not a directory", file=sys.stderr)
        return 1

    adrs = sorted(args.directory.glob(args.glob))
    if not adrs:
        print(f"error: no files matching {args.glob} in {args.directory}", file=sys.stderr)
        return 1

    with args.out.open("w", encoding="utf-8") as f:
        for path in adrs:
            record = parse_adr(path)
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
            print(f"  {record['id']:<8}  {record['status']:<12}  {record['title']}")

    print(f"\nWrote {len(adrs)} ADRs to {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
