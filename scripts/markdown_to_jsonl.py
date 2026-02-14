#!/usr/bin/env python
"""Convert exported Markdown folders into JSONL dataset splits."""

from __future__ import annotations

import argparse
import hashlib
import json
import random
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build train/validation/test JSONL files from recursive Markdown exports."
    )
    parser.add_argument(
        "--input-dir",
        required=True,
        help="Directory containing exported Markdown files (searched recursively).",
    )
    parser.add_argument(
        "--output-dir",
        default="data",
        help="Directory where split JSONL files are written.",
    )
    parser.add_argument(
        "--train-ratio",
        type=float,
        default=0.9,
        help="Train split ratio.",
    )
    parser.add_argument(
        "--validation-ratio",
        type=float,
        default=0.1,
        help="Validation split ratio.",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed for deterministic splitting.",
    )
    parser.add_argument(
        "--min-chars",
        type=int,
        default=20,
        help="Minimum cleaned text length to keep a record.",
    )
    return parser.parse_args()


def split_markdown_front_matter(text: str) -> tuple[dict[str, str], str]:
    if not text.startswith("---\n"):
        return {}, text

    end_idx = text.find("\n---\n", 4)
    if end_idx == -1:
        return {}, text

    block = text[4:end_idx]
    body = text[end_idx + 5 :]
    meta: dict[str, str] = {}

    for line in block.splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        meta[key.strip()] = value.strip()

    return meta, body


def extract_title(text: str, fallback: str) -> str:
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("# "):
            return stripped[2:].strip()
    return fallback


def determine_space(rel_path: Path) -> str:
    if len(rel_path.parts) > 1:
        return rel_path.parts[0]
    return "default"


def iter_markdown_records(input_dir: Path, min_chars: int) -> list[dict[str, object]]:
    records: list[dict[str, object]] = []
    seen_ids: set[str] = set()

    for file_path in sorted(input_dir.rglob("*.md")):
        rel_path = file_path.relative_to(input_dir)
        raw = file_path.read_text(encoding="utf-8", errors="replace")
        front_matter, body = split_markdown_front_matter(raw)
        text = body.strip()

        if len(text) < min_chars:
            continue

        record_id = hashlib.sha256(f"{rel_path}|{text}".encode("utf-8")).hexdigest()[:16]
        if record_id in seen_ids:
            continue
        seen_ids.add(record_id)

        title = extract_title(text, file_path.stem)
        records.append(
            {
                "id": record_id,
                "source": "perplexity_space_export",
                "space": determine_space(rel_path),
                "relative_path": rel_path.as_posix(),
                "title": title,
                "text": text,
                "meta": front_matter,
            }
        )

    return records


def validate_ratios(train_ratio: float, validation_ratio: float) -> None:
    test_ratio = 1.0 - train_ratio - validation_ratio
    if train_ratio <= 0 or validation_ratio < 0 or test_ratio < 0:
        raise ValueError(
            "Invalid split ratios. Require train_ratio > 0 and train_ratio + validation_ratio <= 1."
        )


def split_records(
    records: list[dict[str, object]], train_ratio: float, validation_ratio: float, seed: int
) -> dict[str, list[dict[str, object]]]:
    shuffled = list(records)
    random.Random(seed).shuffle(shuffled)

    n_total = len(shuffled)
    n_train = int(n_total * train_ratio)
    n_validation = int(n_total * validation_ratio)

    if n_total > 0 and n_train == 0:
        n_train = 1
    if n_train + n_validation > n_total:
        n_validation = max(0, n_total - n_train)

    train = shuffled[:n_train]
    validation = shuffled[n_train : n_train + n_validation]
    test = shuffled[n_train + n_validation :]
    return {"train": train, "validation": validation, "test": test}


def write_jsonl(path: Path, records: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")


def main() -> None:
    args = parse_args()
    validate_ratios(args.train_ratio, args.validation_ratio)

    input_dir = Path(args.input_dir).expanduser().resolve()
    output_dir = Path(args.output_dir).expanduser().resolve()

    if not input_dir.exists():
        raise FileNotFoundError(f"Input directory not found: {input_dir}")

    records = iter_markdown_records(input_dir=input_dir, min_chars=args.min_chars)
    if not records:
        raise SystemExit(f"No valid Markdown records found in: {input_dir}")

    splits = split_records(
        records=records,
        train_ratio=args.train_ratio,
        validation_ratio=args.validation_ratio,
        seed=args.seed,
    )

    for split_name, split_records_data in splits.items():
        if not split_records_data:
            continue
        out_file = output_dir / f"{split_name}.jsonl"
        write_jsonl(out_file, split_records_data)
        print(f"Wrote {split_name}: {len(split_records_data)} rows -> {out_file}")

    print(f"Total records processed: {len(records)}")


if __name__ == "__main__":
    main()
