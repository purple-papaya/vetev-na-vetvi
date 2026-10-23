#!/usr/bin/env python3
"""Tell the search engines that use IndexNow (Bing, Seznam, Yandex and others, which share the
notices) which pages changed, so they come back for them within minutes instead of weeks.
Standard library only.

    python3 tools/indexnow.py               # pages changed by the last commit (for a merge commit: the whole branch)
    python3 tools/indexnow.py --since REF   # pages changed since REF
    python3 tools/indexnow.py --all         # every page in the sitemap
    python3 tools/indexnow.py --dry-run     # only print the addresses

It runs by itself after every deploy to GitHub Pages (.github/workflows/indexnow.yml). The key
proves the site is ours: a file of the same name with the key inside sits in the site root.
"""
import argparse
import json
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'tools'))
import seo  # noqa: E402  (page list and addresses)

KEY = 'b4ec072007d36d5db2a78fad120b85fb'
ENDPOINT = 'https://api.indexnow.org/indexnow'


def changed_since(ref):
    out = subprocess.run(['git', 'diff', '--name-only', ref, 'HEAD'], cwd=ROOT, capture_output=True, text=True, check=True)
    return set(out.stdout.split())


def main():
    ap = argparse.ArgumentParser(description='Pošle změněné stránky vyhledávačům přes IndexNow.')
    ap.add_argument('--all', action='store_true', help='poslat všechny stránky z mapy webu')
    ap.add_argument('--since', default='HEAD^1', help='porovnat s tímto commitem (výchozí: předchozí)')
    ap.add_argument('--dry-run', action='store_true', help='jen vypsat adresy, nic neposílat')
    args = ap.parse_args()

    if not (ROOT / f'{KEY}.txt').exists():
        print(f'Chybí soubor s klíčem {KEY}.txt v kořeni webu.', file=sys.stderr)
        return 1
    pages = [p for p, m in seo.PAGES.items() if m['kind'] in seo.INDEXABLE]
    if not args.all:
        try:
            changed = changed_since(args.since)
        except subprocess.CalledProcessError:
            print(f'Nejde porovnat s {args.since}, nic neposílám.')
            return 0
        pages = [p for p in pages if p in changed]
    urls = [seo.url_of(p) for p in pages]
    if not urls:
        print('Žádná stránka se nezměnila, není co posílat.')
        return 0
    print('\n'.join(urls))
    if args.dry_run:
        return 0

    body = json.dumps({'host': urllib.parse.urlparse(seo.SITE_URL).netloc, 'key': KEY,
                       'keyLocation': f'{seo.SITE_URL}{KEY}.txt', 'urlList': urls}).encode('utf-8')
    req = urllib.request.Request(ENDPOINT, data=body, headers={'Content-Type': 'application/json; charset=utf-8'})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            print(f'IndexNow odpověděl {resp.status}: přijato {len(urls)} adres.')
    except urllib.error.HTTPError as e:
        # 403: the key file is not reachable yet; 422: an address is not on this site; 429: too often
        print(f'IndexNow požadavek odmítl: {e.code} {e.reason}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
