#!/usr/bin/env python3
"""Keep the CSP <meta> in index.html in sync with its inline <script>/<style>.

  python3 scripts/csp-hash.py          # rewrite the CSP with fresh hashes
  python3 scripts/csp-hash.py --check  # exit 1 if the CSP is stale (used by CI)

Not a build step: index.html stays a hand-edited file that works from file://.
Run this after every edit to the inline <script> or <style>.
"""
import base64
import hashlib
import pathlib
import re
import sys

PAGE = pathlib.Path(__file__).resolve().parent.parent / "index.html"
META = re.compile(r'(<meta http-equiv="Content-Security-Policy" content=")([^"]*)(">)')


def sha256(text: str) -> str:
    return "'sha256-" + base64.b64encode(hashlib.sha256(text.encode("utf-8")).digest()).decode() + "'"


def build_csp(html: str) -> str:
    scripts = re.findall(r"<script>(.*?)</script>", html, re.S)
    styles = re.findall(r"<style>(.*?)</style>", html, re.S)
    if len(scripts) != 1 or len(styles) != 1:
        sys.exit("expected exactly one inline <script> and one <style>")
    return "; ".join([
        "default-src 'none'",
        "script-src " + sha256(scripts[0]),
        "style-src " + sha256(styles[0]),
        "connect-src https://formsubmit.co",
        "img-src 'none'",
        "font-src 'none'",
        "object-src 'none'",
        "base-uri 'none'",
        "form-action 'none'",
        "require-trusted-types-for 'script'",
        "trusted-types 'none'",
    ])


def main() -> None:
    html = PAGE.read_text(encoding="utf-8")
    m = META.search(html)
    if not m:
        sys.exit("CSP <meta> not found in index.html")
    want = build_csp(html)
    if "--check" in sys.argv:
        if m.group(2) != want:
            print("CSP is stale: run python3 scripts/csp-hash.py", file=sys.stderr)
            sys.exit(1)
        print("CSP hashes OK")
        return
    PAGE.write_text(html[: m.start(2)] + want + html[m.end(2):], encoding="utf-8")
    print("CSP updated")


if __name__ == "__main__":
    main()
