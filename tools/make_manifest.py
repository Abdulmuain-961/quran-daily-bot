"""Write data/approved_pages.sha256 — the digital fingerprint of every approved page image.

Run this ONLY after a qualified reviewer (hafiz / Quran teacher) has approved all 604 images.
Before every post, bot.py checks the two images against these fingerprints and refuses to
publish if even one pixel has changed.

Usage:  python tools/make_manifest.py
"""
import pathlib, sys
ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
from fingerprint import jpeg_fingerprint
lines = []
for n in range(1, 605):
    p = ROOT / "images" / f"page_{n:03d}.jpg"
    lines.append(f"{jpeg_fingerprint(p.read_bytes())}  images/{p.name}")
(ROOT / "data" / "approved_pages.sha256").write_text("\n".join(lines) + "\n", encoding="utf-8")
print("fingerprints written for 604 pages")
