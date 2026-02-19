#!/usr/bin/env python3
"""Build a helper-context package from markdown docs and final-report figures.

Outputs under outputs/helper_context/:
- project_context_stack.md
- project_context_stack.pdf
- final_report_images.zip
- context_manifest.csv
- package_integrity_checks.csv
"""

from __future__ import annotations

import csv
import subprocess
import zipfile
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = PROJECT_ROOT / "outputs" / "helper_context"
STACK_MD = OUTPUT_DIR / "project_context_stack.md"
STACK_PDF = OUTPUT_DIR / "project_context_stack.pdf"
ZIP_PATH = OUTPUT_DIR / "final_report_images.zip"
MANIFEST_CSV = OUTPUT_DIR / "context_manifest.csv"
CHECKS_CSV = OUTPUT_DIR / "package_integrity_checks.csv"
FIG_DIR = PROJECT_ROOT / "outputs" / "final_report" / "figures"

PRIORITY_ORDER = [
    Path("docs/FINAL_REPORT.md"),
    Path("docs/OTHER_EXPERIMENTS.md"),
    Path("docs/PIPELINE.md"),
    Path("docs/DATA_DICTIONARY.md"),
]


# Keep provenance explicit for downstream prompting.
def stack_block(rel_path: Path, text: str) -> str:
    return f"# Source: {rel_path.as_posix()}\n\n{text}\n\n---\n\n"



def discover_markdown_files(root: Path) -> list[Path]:
    md_files = [p for p in root.rglob("*.md") if p.is_file()]
    rels = [p.relative_to(root) for p in md_files]
    return sorted(rels, key=lambda p: p.as_posix())



def order_markdown_files(all_files: list[Path]) -> list[Path]:
    all_set = set(all_files)
    ordered: list[Path] = []

    for p in PRIORITY_ORDER:
        if p in all_set and p not in ordered:
            ordered.append(p)

    for p in sorted(all_files, key=lambda x: x.as_posix()):
        if p not in ordered:
            ordered.append(p)

    return ordered



def write_stack_and_manifest(root: Path, ordered_files: list[Path]) -> list[dict]:
    manifest_rows: list[dict] = []
    blocks: list[str] = []

    for idx, rel in enumerate(ordered_files, start=1):
        abs_path = root / rel
        text = abs_path.read_text(encoding="utf-8", errors="replace")
        blocks.append(stack_block(rel, text))
        manifest_rows.append(
            {
                "order_index": idx,
                "source_path": rel.as_posix(),
                "bytes": abs_path.stat().st_size,
                "line_count": len(text.splitlines()),
                "included": True,
            }
        )

    STACK_MD.write_text("".join(blocks), encoding="utf-8")

    with MANIFEST_CSV.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["order_index", "source_path", "bytes", "line_count", "included"],
        )
        writer.writeheader()
        writer.writerows(manifest_rows)

    return manifest_rows



def build_pdf() -> tuple[bool, str]:
    if STACK_PDF.exists():
        STACK_PDF.unlink()

    cmd = ["cupsfilter", "-m", "application/pdf", str(STACK_MD)]
    try:
        proc = subprocess.run(cmd, check=False, capture_output=True)
    except FileNotFoundError:
        return False, "cupsfilter not found"

    if proc.returncode != 0:
        err = (proc.stderr or b"").decode("utf-8", errors="replace").strip()
        return False, f"cupsfilter failed rc={proc.returncode}: {err}"

    STACK_PDF.write_bytes(proc.stdout)

    if not STACK_PDF.exists() or STACK_PDF.stat().st_size <= 0:
        return False, "pdf output missing or empty"

    return True, "ok"



def zip_final_report_images() -> tuple[int, int]:
    png_files = sorted(FIG_DIR.glob("*.png"), key=lambda p: p.name)

    if ZIP_PATH.exists():
        ZIP_PATH.unlink()

    with zipfile.ZipFile(ZIP_PATH, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
        for p in png_files:
            zf.write(p, arcname=p.name)

    with zipfile.ZipFile(ZIP_PATH, mode="r") as zf:
        zip_count = len(zf.namelist())

    return len(png_files), zip_count



def run_checks(
    ordered_files: list[Path],
    manifest_rows: list[dict],
    pdf_ok: bool,
    pdf_msg: str,
    img_dir_count: int,
    zip_count: int,
) -> list[dict]:
    checks: list[dict] = []

    manifest_paths = [row["source_path"] for row in manifest_rows]
    header_count = STACK_MD.read_text(encoding="utf-8", errors="replace").count("# Source: ")

    checks.append(
        {
            "check": "source_discovery_count_matches_manifest",
            "expected": len(ordered_files),
            "actual": len(manifest_rows),
            "pass": len(ordered_files) == len(manifest_rows),
        }
    )

    first_four_expected = [p.as_posix() for p in PRIORITY_ORDER]
    first_four_actual = manifest_paths[:4]
    checks.append(
        {
            "check": "ordering_first_four",
            "expected": "|".join(first_four_expected),
            "actual": "|".join(first_four_actual),
            "pass": first_four_actual == first_four_expected,
        }
    )

    checks.append(
        {
            "check": "stack_md_exists_nonempty",
            "expected": True,
            "actual": STACK_MD.exists() and STACK_MD.stat().st_size > 0,
            "pass": STACK_MD.exists() and STACK_MD.stat().st_size > 0,
        }
    )

    checks.append(
        {
            "check": "stack_source_headers_count",
            "expected": len(manifest_rows),
            "actual": header_count,
            "pass": header_count == len(manifest_rows),
        }
    )

    checks.append(
        {
            "check": "pdf_exists_nonempty",
            "expected": True,
            "actual": STACK_PDF.exists() and STACK_PDF.stat().st_size > 0,
            "pass": STACK_PDF.exists() and STACK_PDF.stat().st_size > 0,
        }
    )

    checks.append(
        {
            "check": "pdf_generation_status",
            "expected": "ok",
            "actual": pdf_msg,
            "pass": pdf_ok,
        }
    )

    checks.append(
        {
            "check": "zip_exists",
            "expected": True,
            "actual": ZIP_PATH.exists(),
            "pass": ZIP_PATH.exists(),
        }
    )

    checks.append(
        {
            "check": "zip_image_count_matches_figure_dir",
            "expected": img_dir_count,
            "actual": zip_count,
            "pass": img_dir_count == zip_count,
        }
    )

    checks.append(
        {
            "check": "no_missing_source_files",
            "expected": True,
            "actual": all((PROJECT_ROOT / Path(p)).exists() for p in manifest_paths),
            "pass": all((PROJECT_ROOT / Path(p)).exists() for p in manifest_paths),
        }
    )

    with CHECKS_CSV.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["check", "expected", "actual", "pass"])
        writer.writeheader()
        writer.writerows(checks)

    return checks



def main() -> int:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    all_md = discover_markdown_files(PROJECT_ROOT)
    ordered = order_markdown_files(all_md)
    manifest_rows = write_stack_and_manifest(PROJECT_ROOT, ordered)

    pdf_ok, pdf_msg = build_pdf()
    img_dir_count, zip_count = zip_final_report_images()

    checks = run_checks(ordered, manifest_rows, pdf_ok, pdf_msg, img_dir_count, zip_count)
    all_pass = all(bool(row["pass"]) for row in checks)

    pdf_bytes = STACK_PDF.stat().st_size if STACK_PDF.exists() else 0

    print(f"included_markdown_files={len(manifest_rows)}")
    print(f"pdf_bytes={pdf_bytes}")
    print(f"zipped_image_count={zip_count}")
    print(f"output_dir={OUTPUT_DIR}")
    print(f"integrity_all_pass={all_pass}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
