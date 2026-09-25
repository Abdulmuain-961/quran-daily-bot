"""Make the review file for the hafiz: all 604 page images exactly as they will be posted,
two pages per sheet (like an open Mushaf), each with its page number and fingerprint.
Usage:  python tools/make_review_pdf.py  ->  review/quran_pages_review.pdf"""
import pathlib, sys
from PIL import Image, ImageDraw, ImageFont
ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
from fingerprint import jpeg_fingerprint
FONT = ImageFont.truetype(str(ROOT / "assets" / "Amiri-Regular.ttf"), 26, layout_engine=ImageFont.Layout.RAQM)
AR = str.maketrans("0123456789", "٠١٢٣٤٥٦٧٨٩")
PW, PH = 760, 950           # about the resolution of the official scan

def tile(n):
    path = ROOT / "images" / f"page_{n:03d}.jpg"
    fp = jpeg_fingerprint(path.read_bytes())[:12]
    im = Image.open(path).resize((PW, PH), Image.LANCZOS)
    t = Image.new("RGB", (PW, PH + 60), "white"); t.paste(im, (0, 0))
    d = ImageDraw.Draw(t)
    d.text((PW // 2, PH + 30), f"الصفحة {n}".translate(AR) + f"   ·   {fp}   ·   تمت المراجعة [   ]",
           font=FONT, fill=(60, 60, 60), anchor="mm", direction="rtl")
    return t

sheets = []
for right in range(1, 605, 2):
    s = Image.new("RGB", (PW * 2 + 40, PH + 60), "white")
    s.paste(tile(right + 1), (0, 0))        # left side = even page
    s.paste(tile(right), (PW + 40, 0))      # right side = odd page (Arabic reading order)
    sheets.append(s)
out = ROOT / "review" / "quran_pages_review.pdf"
out.parent.mkdir(exist_ok=True)
sheets[0].save(out, save_all=True, append_images=sheets[1:], resolution=150, quality=75)
print("saved", out, len(sheets), "sheets")
