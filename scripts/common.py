"""Shared helpers."""

from __future__ import annotations

import os
import re
import zipfile
from pathlib import Path
from typing import Optional
from urllib.parse import urljoin

import py7zr
import requests
import urllib3
from bs4 import BeautifulSoup

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "out"
LINKS = ROOT / "links.txt"
ARCHIVE_SUFFIXES = {".zip", ".7z"}

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/136.0.0.0 Safari/537.36 Edg/136.0.0.0"
)


def create_session() -> requests.Session:
    session = requests.Session()
    session.verify = False
    session.headers.update(
        {
            "User-Agent": USER_AGENT,
            "Accept": (
                "text/html,application/xhtml+xml,application/xml;q=0.9,"
                "image/avif,image/webp,*/*;q=0.8"
            ),
            "Accept-Language": "en-US,en;q=0.9",
        }
    )
    return session


def get_media(session: requests.Session, url: str) -> Optional[dict]:
    print(f"Getting media from {url}...")
    try:
        response = session.get(url, timeout=60)
    except requests.RequestException as exc:
        print(f"Error: {exc}")
        return None

    if response.status_code != 200:
        print(f"Error: HTTP {response.status_code}")
        return None

    soup = BeautifulSoup(response.text, "html.parser")
    media_id = soup.find("input", {"name": "mediaId"})
    form = soup.find("form", {"id": "dl_form"})
    if not media_id or not form or not form.get("action"):
        print("Unable to find media download form")
        return None

    return {
        "id": media_id["value"],
        "url": form["action"],
        "referer": url,
    }


def build_download_url(media: dict) -> str:
    action = media["url"]
    if action.startswith("//"):
        base = "https:" + action
    elif action.startswith("http"):
        base = action
    else:
        base = urljoin("https://vimm.net/", action)
    return f"{base}?mediaId={media['id']}"


def parse_filename(content_disposition: Optional[str], media_id: str) -> str:
    if content_disposition:
        match = re.search(
            r'filename\*?=(?:UTF-8\'\')?"?([^";]+)"?', content_disposition
        )
        if match:
            return os.path.basename(match.group(1).strip())
    return f"{media_id}.bin"


def load_urls() -> list[str]:
    urls: list[str] = []
    with open(LINKS, encoding="utf-8") as handle:
        for raw in handle:
            line = raw.strip()
            if line and not line.startswith("#"):
                urls.append(line)
    return urls


def list_archives() -> list[Path]:
    if not OUT.is_dir():
        return []
    return sorted(
        p for p in OUT.iterdir() if p.is_file() and p.suffix.lower() in ARCHIVE_SUFFIXES
    )


def extract_archive(archive_path: Path, *, delete: bool = True) -> bool:
    try:
        OUT.mkdir(parents=True, exist_ok=True)
        suffix = archive_path.suffix.lower()

        if suffix == ".zip":
            with zipfile.ZipFile(archive_path, "r") as zf:
                zf.extractall(OUT)
            print(f"Extracted: {archive_path.name}")
        elif suffix == ".7z":
            with py7zr.SevenZipFile(archive_path, "r") as zf:
                zf.extractall(OUT)
            print(f"Extracted: {archive_path.name}")
        else:
            print(f"Unsupported: {archive_path.name}")
            return False

        if delete:
            archive_path.unlink()
            print(f"Deleted: {archive_path.name}")
        return True
    except Exception as exc:
        print(f"Error extracting {archive_path.name}: {exc}")
        return False
