#!/usr/bin/env python3
"""Download vault URLs from links.txt into out/."""

from __future__ import annotations

import sys
from urllib.parse import urlparse

from tqdm import tqdm

from scripts.common import (
    OUT,
    LINKS,
    build_download_url,
    create_session,
    get_media,
    load_urls,
    parse_filename,
)


def download_one(session, media: dict) -> bool:
    url = build_download_url(media)
    print(f"Downloading: {url}")
    headers = {"Referer": media["referer"]}

    try:
        with session.get(url, headers=headers, stream=True, timeout=120) as response:
            if response.status_code not in (200, 304):
                print(f"Error: HTTP {response.status_code}")
                return False

            total = int(response.headers.get("content-length", 0))
            name = parse_filename(
                response.headers.get("content-disposition"), media["id"]
            )
            path = OUT / name

            if path.exists() and total and path.stat().st_size == total:
                print(f"Already complete: {name}")
                return True

            with tqdm(total=total or None, unit="B", unit_scale=True, desc=name) as bar:
                with open(path, "wb") as file:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            file.write(chunk)
                            bar.update(len(chunk))

            print(f"Saved: {path}")
            return True
    except Exception as exc:
        print(f"Error: {exc}")
        return False


def main() -> int:
    if not LINKS.is_file():
        print(f"Missing {LINKS.name}", file=sys.stderr)
        return 1

    urls = load_urls()
    if not urls:
        print(f"No URLs in {LINKS.name}", file=sys.stderr)
        return 1

    OUT.mkdir(parents=True, exist_ok=True)
    session = create_session()
    failed = 0

    for i, url in enumerate(urls, 1):
        print(f"\n[{i}/{len(urls)}] {url}")
        parsed = urlparse(url)
        if parsed.scheme not in ("http", "https") or not parsed.netloc:
            print("Invalid URL")
            failed += 1
            continue

        media = get_media(session, url)
        if not media:
            failed += 1
            continue

        if not download_one(session, media):
            failed += 1

    print(f"\nDone. {len(urls) - failed}/{len(urls)} ok, {failed} failed.")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
