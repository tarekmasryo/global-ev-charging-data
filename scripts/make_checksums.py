from __future__ import annotations

import argparse
import hashlib
from pathlib import Path

DATA_DIR = Path("data")
OUT_FILE = Path("checksums.sha256")


def sha256_csv_normalized(path: Path, chunk_size: int = 1024 * 1024) -> str:
    """
    Compute SHA256 while normalizing line endings to LF.
    This makes checksums stable across Windows (CRLF) and Linux (LF) checkouts.
    """
    h = hashlib.sha256()
    prev_cr = False
    with path.open("rb") as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break

            if prev_cr:
                chunk = b"\r" + chunk
                prev_cr = False

            if chunk.endswith(b"\r"):
                chunk = chunk[:-1]
                prev_cr = True

            chunk = chunk.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
            h.update(chunk)

    if prev_cr:
        h.update(b"\n")

    return h.hexdigest()


def iter_data_files(data_dir: Path) -> list[Path]:
    files = [p.resolve() for p in data_dir.glob("*.csv") if p.is_file()]
    return sorted(files, key=lambda p: p.as_posix())


def write_checksums(out_file: Path, root: Path, data_dir: Path) -> int:
    files = iter_data_files(data_dir)
    lines: list[str] = []
    for p in files:
        rel = p.relative_to(root).as_posix()
        lines.append(f"{sha256_csv_normalized(p)}  {rel}")

    out_file.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {out_file.as_posix()} with {len(lines)} entries")
    return 0


def check_checksums(out_file: Path, root: Path, data_dir: Path) -> int:
    if not out_file.exists():
        print("checksums.sha256 not found. Generate with: python scripts/make_checksums.py")
        return 1

    expected: dict[str, str] = {}
    for line in out_file.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        parts = line.split()
        if len(parts) < 2:
            continue
        expected[parts[1]] = parts[0]

    mismatched: list[str] = []
    missing: list[str] = []
    current_files = iter_data_files(data_dir)

    for p in current_files:
        rel = p.relative_to(root).as_posix()
        cur = sha256_csv_normalized(p)
        exp = expected.get(rel)
        if exp is None:
            missing.append(rel)
        elif exp != cur:
            mismatched.append(rel)

    extra = sorted(set(expected.keys()) - {p.relative_to(root).as_posix() for p in current_files})

    if mismatched or missing or extra:
        if mismatched:
            print(f"Mismatched checksums for {len(mismatched)} files (example: {mismatched[:1]})")
        if missing:
            print(f"Missing checksums for {len(missing)} files (example: {missing[:1]})")
        if extra:
            print(f"Extra entries in checksums.sha256 (example: {extra[:1]})")
        print("checksums.sha256 does not match current data files.")
        print("Re-generate with: python scripts/make_checksums.py")
        return 1

    print("checksums.sha256 matches current data files")
    return 0


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--data-dir",
        type=Path,
        default=DATA_DIR,
        help="Directory containing CSV data files.",
    )
    ap.add_argument(
        "--out",
        type=Path,
        default=OUT_FILE,
        help="Output checksum file.",
    )
    ap.add_argument(
        "--check",
        action="store_true",
        help="Verify checksums.sha256 instead of writing it.",
    )
    return ap.parse_args()


def main() -> int:
    args = parse_args()
    root = Path(".").resolve()
    data_dir = args.data_dir.resolve()

    if args.check:
        return check_checksums(args.out, root, data_dir)

    return write_checksums(args.out, root, data_dir)


if __name__ == "__main__":
    raise SystemExit(main())
