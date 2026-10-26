#!/usr/bin/env python3
"""Fetch RSS headlines and write a small same-origin JSON file for the BrightSign page.

Uses only Python's standard library. Feed publishers can change URLs and policies:
verify suitability and licensing for public installations.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import html
import json
from pathlib import Path
import re
import sys
from urllib.error import URLError
from urllib.request import Request, urlopen
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_OUTPUT = ROOT / 'site' / 'headlines.json'
SOURCES = [
    ('BBC WORLD', 'https://feeds.bbci.co.uk/news/world/rss.xml'),
    ('NPR WORLD', 'https://feeds.npr.org/1004/rss.xml'),
]
MAX_HEADLINES = 24
MAX_TITLE_LENGTH = 180


def sanitize(value: str) -> str:
    value = re.sub(r'<[^>]*>', '', value)
    value = html.unescape(value)
    return re.sub(r'\s+', ' ', value).strip()[:MAX_TITLE_LENGTH]


def parse_rss(data: bytes, source: str) -> list[dict[str, str]]:
    root = ET.fromstring(data)
    # RSS: channel/item/title; Atom: entry/title.
    nodes = root.findall('.//channel/item')
    if not nodes:
        nodes = root.findall('.//{http://www.w3.org/2005/Atom}entry')
    results = []
    for item in nodes:
        title = item.findtext('title') or item.findtext('{http://www.w3.org/2005/Atom}title') or ''
        title = sanitize(title)
        if len(title) < 12:
            continue
        results.append({'title': title, 'source': source})
    return results


def read_url(url: str, timeout: int = 20) -> bytes:
    request = Request(url, headers={'User-Agent': 'NewsProjectionBot/1.0 (RSS reader; projection artwork)'})
    with urlopen(request, timeout=timeout) as response:
        data = response.read(2_000_000 + 1)
    if len(data) > 2_000_000:
        raise ValueError('RSS feed exceeds size limit')
    return data


def gather(source_map: list[tuple[str, str]] = SOURCES) -> list[dict[str, str]]:
    candidates: list[dict[str, str]] = []
    successes = 0
    for source, url in source_map:
        try:
            parsed = parse_rss(read_url(url), source)
            if not parsed:
                raise ValueError('No usable headlines')
            successes += 1
            candidates.extend(parsed)
            print(f'{source}: {len(parsed)} headlines', file=sys.stderr)
        except (URLError, ValueError, TimeoutError, ET.ParseError, OSError) as exc:
            print(f'WARNING: {source} failed: {exc}', file=sys.stderr)
    if successes == 0:
        raise RuntimeError('Every news feed failed; keeping existing JSON unchanged')
    # Interleave publishers so an upstream feed does not dominate the display.
    grouped: dict[str, list[dict[str, str]]] = {s: [] for s, _ in source_map}
    for item in candidates:
        grouped[item['source']].append(item)
    unique: set[str] = set()
    chosen: list[dict[str, str]] = []
    while len(chosen) < MAX_HEADLINES and any(grouped.values()):
        for key in grouped:
            if not grouped[key]:
                continue
            item = grouped[key].pop(0)
            fingerprint = re.sub(r'\W+', '', item['title'].casefold())
            if fingerprint not in unique:
                chosen.append(item)
                unique.add(fingerprint)
            if len(chosen) == MAX_HEADLINES:
                break
    if len(chosen) < 3:
        raise RuntimeError('Not enough usable headlines; keeping previous JSON unchanged')
    return chosen


def write_json(path: Path, items: list[dict[str, str]]) -> None:
    payload = {
        'demo': False,
        'updated_at': datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z'),
        'headlines': items,
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + '.tmp')
    temporary.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    temporary.replace(path)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--output', type=Path, default=DEFAULT_OUTPUT)
    ap.add_argument('--fixture', type=Path, help='Offline test with a local RSS XML file')
    args = ap.parse_args()
    try:
        items = parse_rss(args.fixture.read_bytes(), 'TEST RSS') if args.fixture else gather()
        if len(items) < 1: raise RuntimeError('No headlines in input')
        write_json(args.output, items[:MAX_HEADLINES])
        print(f'Wrote {len(items[:MAX_HEADLINES])} headlines to {args.output}')
        return 0
    except Exception as exc:
        print(f'ERROR: {exc} (left prior JSON intact)', file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
