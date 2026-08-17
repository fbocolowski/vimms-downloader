#!/usr/bin/env python3
"""Extract all zip/7z in out/ into out/. Deletes archives unless --no-delete."""

from __future__ import annotations

import sys

from scripts.common import extract_archive, list_archives


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    delete = True

    if "--no-delete" in args:
        delete = False
        args.remove("--no-delete")

    if args:
        print("Usage: extract.py [--no-delete]", file=sys.stderr)
        return 1

    archives = list_archives()
    if not archives:
        print("No archives in out/")
        return 1

    failed = 0
    for i, archive in enumerate(archives, 1):
        print(f"\n[{i}/{len(archives)}] {archive.name}")
        if not extract_archive(archive, delete=delete):
            failed += 1

    print(f"\nDone. {len(archives) - failed}/{len(archives)} ok, {failed} failed.")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
