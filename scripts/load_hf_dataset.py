#!/usr/bin/env python
"""Quick dataset loader for Hugging Face Hub datasets."""

from __future__ import annotations

import argparse
import os

from datasets import load_dataset
from huggingface_hub import HfApi


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Load and preview a dataset split from Hugging Face Hub."
    )
    parser.add_argument(
        "--dataset-id",
        default="issdandavis/scbe-aethermoore-knowledge-base",
        help="Dataset repo id on Hugging Face Hub (for example: username/dataset-name).",
    )
    parser.add_argument("--split", default="train", help="Split to load.")
    parser.add_argument(
        "--limit",
        type=int,
        default=3,
        help="How many examples to print from the split.",
    )
    parser.add_argument(
        "--streaming",
        action="store_true",
        help="Stream examples without downloading the full dataset.",
    )
    parser.add_argument(
        "--token",
        default=os.environ.get("HF_TOKEN"),
        help="HF access token. Defaults to HF_TOKEN env var.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    token = args.token

    if token:
        try:
            user = HfApi(token=token).whoami()["name"]
            print(f"Authenticated as: {user}")
        except Exception as exc:  # pragma: no cover - network/auth failure path
            print(f"Token check failed ({exc}). Retrying without token for public access.")
            token = None
    else:
        print("No HF token provided. Public datasets only.")

    try:
        ds = load_dataset(
            path=args.dataset_id,
            split=args.split,
            token=token,
            streaming=args.streaming,
        )
    except Exception as exc:  # pragma: no cover - network/hub failure path
        raise SystemExit(
            f"Failed to load dataset '{args.dataset_id}' split '{args.split}': {exc}"
        ) from exc

    if args.streaming:
        print(f"Loaded streaming split '{args.split}' from '{args.dataset_id}'.")
        for idx, row in enumerate(ds):
            print(f"[{idx}] {row}")
            if idx + 1 >= args.limit:
                break
        return

    print(f"Loaded split '{args.split}' from '{args.dataset_id}'.")
    print(f"Rows: {len(ds)}")
    print(f"Columns: {ds.column_names}")
    print(f"Features: {ds.features}")
    for idx in range(min(args.limit, len(ds))):
        print(f"[{idx}] {ds[idx]}")


if __name__ == "__main__":
    main()
