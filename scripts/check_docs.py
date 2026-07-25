#!/usr/bin/env python3
"""Dependency-free checks for the specification repository."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]
MARKDOWN_LINK = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")
WIKI_LINK = re.compile(r"\[\[([^\]|#]+)")


def check_local_links() -> list[str]:
    errors: list[str] = []
    for document in ROOT.rglob("*.md"):
        text = document.read_text(encoding="utf-8")
        for raw_target in MARKDOWN_LINK.findall(text):
            target = raw_target.strip().split()[0].strip("<>")
            if target.startswith(("http://", "https://", "mailto:", "#")):
                continue
            path_part = unquote(target.split("#", 1)[0])
            if not path_part:
                continue
            resolved = (document.parent / path_part).resolve()
            if not resolved.exists():
                errors.append(f"{document.relative_to(ROOT)}: missing link target {target}")

        for raw_target in WIKI_LINK.findall(text):
            candidate = ROOT / raw_target
            if candidate.suffix != ".md":
                candidate = candidate.with_suffix(".md")
            if not candidate.exists():
                errors.append(
                    f"{document.relative_to(ROOT)}: missing wiki-link target {raw_target}"
                )
    return errors


def check_research_references() -> list[str]:
    document = ROOT / "docs" / "research.md"
    text = document.read_text(encoding="utf-8")
    defined = {int(value) for value in re.findall(r"\*\*\[R(\d+)\]\*\*", text)}
    cited = {int(value) for value in re.findall(r"\[R(\d+)\]", text)}
    errors: list[str] = []
    if defined != cited:
        if cited - defined:
            errors.append(f"undefined research citations: {sorted(cited - defined)}")
        if defined - cited:
            errors.append(f"uncited research sources: {sorted(defined - cited)}")
    if not defined:
        errors.append("no research references found")
    return errors


def check_required_files() -> list[str]:
    required = [
        "README.md",
        "LICENSE",
        "docs/specification.md",
        "docs/architecture.md",
        "docs/correctness-contracts.md",
        "docs/research.md",
        "docs/review.md",
        "examples/layered-experiment.yaml",
    ]
    return [f"missing required file: {path}" for path in required if not (ROOT / path).exists()]


def check_json_examples() -> list[str]:
    errors: list[str] = []
    for document in ROOT.rglob("*.md"):
        text = document.read_text(encoding="utf-8")
        for index, block in enumerate(re.findall(r"```json\n(.*?)\n```", text, re.DOTALL), 1):
            try:
                json.loads(block)
            except json.JSONDecodeError as exc:
                errors.append(
                    f"{document.relative_to(ROOT)}: JSON block {index}: {exc.msg}"
                )
    return errors


def check_requirement_ids() -> list[str]:
    text = (ROOT / "docs" / "specification.md").read_text(encoding="utf-8")
    ids = re.findall(r"\| (FR-\d+|QR-\d+|SEC-\d+) \|", text)
    duplicates = sorted({requirement_id for requirement_id in ids if ids.count(requirement_id) > 1})
    return [f"duplicate requirement IDs: {duplicates}"] if duplicates else []


def main() -> int:
    errors = (
        check_required_files()
        + check_local_links()
        + check_research_references()
        + check_json_examples()
        + check_requirement_ids()
    )
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print("Documentation checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
