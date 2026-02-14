#!/usr/bin/env python
"""Build and push a DatasetDict from local JSONL files."""

from __future__ import annotations

import argparse
import os
from pathlib import Path

from datasets import DatasetDict, load_dataset
from huggingface_hub import create_repo


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Push train/validation/test JSONL files to a Hugging Face dataset repo."
    )
    parser.add_argument(
        "--dataset-id",
        required=True,
        help="Dataset repo id (for example: username/dataset-name).",
    )
    parser.add_argument("--train", help="Path to train JSONL file.")
    parser.add_argument("--validation", help="Path to validation JSONL file.")
    parser.add_argument("--test", help="Path to test JSONL file.")
    parser.add_argument(
        "--private",
        action="store_true",
        help="Create/update the dataset as private.",
    )
    parser.add_argument(
        "--token",
        default=os.environ.get("HF_TOKEN"),
        help="HF access token. Defaults to HF_TOKEN env var.",
    )
    return parser.parse_args()


def validate_split_path(name: str, path: str | None) -> Path | None:
    if not path:
        return None

    file_path = Path(path).expanduser().resolve()
    if not file_path.exists():
        raise FileNotFoundError(f"{name} file not found: {file_path}")
    if file_path.suffix.lower() != ".jsonl":
        raise ValueError(f"{name} file must be a .jsonl file: {file_path}")
    return file_path


def main() -> None:
    args = parse_args()

    split_paths = {
        "train": validate_split_path("train", args.train),
        "validation": validate_split_path("validation", args.validation),
        "test": validate_split_path("test", args.test),
    }
    split_paths = {k: str(v) for k, v in split_paths.items() if v is not None}

    if not split_paths:
        raise ValueError("Provide at least one split: --train, --validation, or --test.")

    if not args.token:
        raise ValueError("Set HF_TOKEN or pass --token to push a dataset.")

    try:
        create_repo(
            repo_id=args.dataset_id,
            repo_type="dataset",
            private=args.private,
            exist_ok=True,
            token=args.token,
        )
    except Exception as exc:  # pragma: no cover - network/hub failure path
        raise SystemExit(f"Failed to create/access dataset repo '{args.dataset_id}': {exc}") from exc

    split_datasets = {}
    for split_name, path in split_paths.items():
        split_datasets[split_name] = load_dataset(
            "json",
            data_files={split_name: path},
            split=split_name,
        )
        print(f"Loaded {split_name}: {len(split_datasets[split_name])} rows from {path}")

    dataset_dict = DatasetDict(split_datasets)
    try:
        dataset_dict.push_to_hub(
            repo_id=args.dataset_id,
            private=args.private,
            token=args.token,
        )
    except Exception as exc:  # pragma: no cover - network/hub failure path
        raise SystemExit(f"Failed to push dataset '{args.dataset_id}': {exc}") from exc

    print(f"Pushed dataset to: https://huggingface.co/datasets/{args.dataset_id}")


if __name__ == "__main__":
    main()
