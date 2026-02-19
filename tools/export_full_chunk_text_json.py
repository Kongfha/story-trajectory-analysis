#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

import pandas as pd


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Export per-book JSONL files with full chunk text reconstructed from "
            "raw text and saved chunk boundaries."
        )
    )
    parser.add_argument(
        "--metadata",
        type=Path,
        default=Path("data/metadata.csv"),
        help="Path to metadata CSV.",
    )
    parser.add_argument(
        "--processed-root",
        type=Path,
        default=Path("data/processed"),
        help="Root directory that contains per-book processed folders.",
    )
    parser.add_argument(
        "--output-name",
        type=str,
        default="chunks_full_text.jsonl",
        help="Output filename to write under each processed_dir.",
    )
    parser.add_argument(
        "--book-id",
        type=int,
        nargs="*",
        default=None,
        help="Optional book id filter (one or many).",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing output files.",
    )
    return parser.parse_args()


def resolve_raw_path(row: pd.Series, repo_root: Path) -> Path:
    raw_path = str(row.get("raw_path", "")).strip()
    if raw_path:
        p = Path(raw_path)
        if not p.is_absolute():
            p = (repo_root / p).resolve()
        if p.exists():
            return p

    raw_filename = str(row.get("raw_filename", "")).strip()
    if raw_filename:
        p = (repo_root / "data" / "raw" / raw_filename).resolve()
        if p.exists():
            return p

    raise FileNotFoundError(
        f"Unable to resolve raw text path for book_id={row.get('id')}, "
        f"processed_dir={row.get('processed_dir')}"
    )


def load_jsonl(path: Path) -> list[dict]:
    rows: list[dict] = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))
    return rows


def build_full_text_rows(words: list[str], chunks: list[dict]) -> list[dict]:
    out: list[dict] = []
    for c in chunks:
        start = int(c["start_word"])
        end = int(c["end_word"])
        full_text = " ".join(words[start:end])
        out.append(
            {
                "chunk_index": int(c["chunk_index"]),
                "start_word": start,
                "end_word": end,
                "text": full_text,
            }
        )
    return out


def main() -> int:
    args = parse_args()
    repo_root = Path(".").resolve()

    metadata = pd.read_csv(args.metadata)
    if args.book_id:
        wanted = set(args.book_id)
        metadata = metadata[metadata["id"].astype(int).isin(wanted)].copy()

    if metadata.empty:
        print("No rows selected from metadata; nothing to do.")
        return 0

    processed = 0
    skipped = 0

    for _, row in metadata.iterrows():
        book_id = int(row["id"])
        processed_dir = str(row["processed_dir"])
        book_dir = args.processed_root / processed_dir
        chunks_path = book_dir / "chunks.jsonl"
        output_path = book_dir / args.output_name

        if not chunks_path.exists():
            print(f"[SKIP] {book_id} {processed_dir}: missing {chunks_path}")
            skipped += 1
            continue

        if output_path.exists() and not args.overwrite:
            print(f"[SKIP] {book_id} {processed_dir}: exists {output_path}")
            skipped += 1
            continue

        raw_path = resolve_raw_path(row=row, repo_root=repo_root)
        raw_text = raw_path.read_text(encoding="utf-8", errors="ignore")
        words = re.findall(r"\S+", raw_text)

        chunks = load_jsonl(chunks_path)
        full_rows = build_full_text_rows(words=words, chunks=chunks)

        output_path.parent.mkdir(parents=True, exist_ok=True)
        with output_path.open("w", encoding="utf-8") as f:
            for r in full_rows:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")

        print(
            f"[OK] {book_id} {processed_dir}: wrote {output_path} "
            f"({len(full_rows)} chunks)"
        )
        processed += 1

    print(
        f"Done. processed={processed}, skipped={skipped}, "
        f"output_name={args.output_name}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
