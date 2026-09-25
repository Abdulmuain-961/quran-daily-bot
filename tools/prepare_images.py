"""Make the 604 Instagram images from the official Madinah Mushaf PDF (King Fahd Complex).

Nothing on the page is redrawn, retyped or cropped: each page image is taken out of the PDF
exactly as it is stored there, only the empty white margin around it is trimmed, and it is
scaled to fit a white 1080x1350 (4:5) Instagram canvas.

Usage (only needed if the images ever have to be rebuilt):
    python tools/prepare_images.py path/to/standard1-quran.pdf

Requires: poppler-utils (pdfimages) and Pillow.
After running, run  python tools/make_manifest.py  and have the pages reviewed again.
"""
import hashlib, pathlib, subprocess, sys, tempfile
from PIL import Image, ImageChops

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "images"

# SHA-256 of the official PDF these images were made from (standard1-quran.pdf, 625 pages).
PDF_SHA256 = "be0091b2fac87706c240f27398e00e7848daebbd69f7ec437859f66fca15d562"
FIRST_QURAN_PAGE_IN_PDF = 4          # PDF page 4 = Mushaf page 1 (Al-Fatiha) ... PDF page 607 = page 604

W, H, MARGIN = 1080, 1350, 20

def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()

def fit(page):
    page = page.convert("RGB")
    # trim only pure-white margins (everything that is not white stays)
    diff = ImageChops.difference(page, Image.new("RGB", page.size, (255, 255, 255))).convert("L")
    box = diff.point(lambda v: 255 if v > 10 else 0).getbbox()
    page = page.crop((max(box[0] - 4, 0), max(box[1] - 4, 0),
                      min(box[2] + 4, page.width), min(box[3] + 4, page.height)))
    scale = min((W - 2 * MARGIN) / page.width, (H - 2 * MARGIN) / page.height)
    page = page.resize((round(page.width * scale), round(page.height * scale)), Image.LANCZOS)
    canvas = Image.new("RGB", (W, H), (255, 255, 255))
    canvas.paste(page, ((W - page.width) // 2, (H - page.height) // 2))
    return canvas

def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    pdf = sys.argv[1]
    got = sha256(pdf)
    if got != PDF_SHA256:
        sys.exit(f"STOP: this is not the same official PDF.\n expected {PDF_SHA256}\n got      {got}")
    OUT.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        subprocess.run(["pdfimages", "-j", "-f", str(FIRST_QURAN_PAGE_IN_PDF),
                        "-l", str(FIRST_QURAN_PAGE_IN_PDF + 603), pdf, f"{tmp}/p"], check=True)
        files = sorted(pathlib.Path(tmp).glob("p-*.jpg"))
        if len(files) != 604:
            sys.exit(f"STOP: expected 604 page images, found {len(files)}")
        for n, f in enumerate(files, 1):
            fit(Image.open(f)).save(OUT / f"page_{n:03d}.jpg", "JPEG", quality=92, optimize=True)
    print("604 images written to", OUT)

if __name__ == "__main__":
    main()
