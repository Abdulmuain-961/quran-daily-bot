"""Daily Quran bot — posts 2 pages of the Mushaf + 1 hadith as an Instagram carousel.

Runs every day from GitHub Actions (.github/workflows/daily-post.yml).
It remembers where it stopped in state.json, so it continues from the next pages every day
and starts a new khatma (complete reading) automatically after page 604.

Needs 2 secrets (GitHub repo -> Settings -> Secrets and variables -> Actions):
    IG_ACCESS_TOKEN   Meta System User token (never expires)
    IG_USER_ID        the Instagram Business Account ID (a long number)
and 1 variable (same page, "Variables" tab) — the on/off switch:
    POSTING_ENABLED   must be exactly  true  or the bot never publishes

Local test without posting:
    python bot.py --dry-run
"""
import argparse, datetime, json, os, pathlib, sys, time, urllib.error, urllib.parse, urllib.request

ROOT = pathlib.Path(__file__).resolve().parent
STATE_FILE = ROOT / "state.json"
CONFIG = json.load(open(ROOT / "config.json", encoding="utf-8"))
PAGES = json.load(open(ROOT / "data" / "pages.json", encoding="utf-8"))
HADITHS = json.load(open(ROOT / "data" / "hadiths.json", encoding="utf-8"))

UAE = datetime.timezone(datetime.timedelta(hours=4))
AR_DIGITS = str.maketrans("0123456789", "٠١٢٣٤٥٦٧٨٩")
BOOK_NAME = {"bukhari": "البخاري", "muslim": "مسلم"}


# ---------------------------------------------------------------- state
def load_state():
    if STATE_FILE.exists():
        return json.load(open(STATE_FILE, encoding="utf-8"))
    return {"next_page": CONFIG.get("start_page", 1), "next_hadith": 0, "khatma": 1,
            "day": 0, "last_post_date": None, "history": []}

def save_state(state):
    state["history"] = state["history"][-60:]          # keep the file small
    json.dump(state, open(STATE_FILE, "w", encoding="utf-8"), ensure_ascii=False, indent=2)


# ---------------------------------------------------------------- caption
def ar(n):
    return str(n).translate(AR_DIGITS)

def surah_text(p1, p2):
    names = []
    for p in (p1, p2):
        for s in PAGES[p - 1]["surahs"]:
            if s not in names:
                names.append(s)
    return "سورة " + " - ".join(names) if len(names) <= 3 else f"من سورة {names[0]} إلى سورة {names[-1]}"

def hadith_text(h):
    if h.get("agreed"):
        ref = f"متفق عليه (البخاري {ar(h['number'])})" if h["book"] == "bukhari" else "متفق عليه"
    elif h["book"] == "bukhari":
        ref = f"رواه البخاري ({ar(h['number'])})"
    else:
        ref = "رواه مسلم"
    said = "قالت" if h["narrator"].endswith("عنها") else "قال"
    return f"عن {h['narrator']} {said}: قال رسول الله ﷺ:\n«{h['text']}»\n[{ref}]"

def build_caption(p1, p2, hadith, state):
    juz = sorted({PAGES[p1 - 1]["juz"], PAGES[p2 - 1]["juz"]})
    juz_txt = "الجزء " + " - ".join(ar(j) for j in juz)
    lines = [
        CONFIG["title"],
        f"{surah_text(p1, p2)} • {juz_txt} • الصفحتان {ar(p1)} - {ar(p2)}",
        f"الختمة رقم {ar(state['khatma'])} • اليوم {ar(state['day'] + 1)}",
        "",
        "۞ حديث اليوم ۞",
        hadith_text(hadith),
        "",
        CONFIG.get("footer", "").strip(),
        "",
        " ".join(CONFIG["hashtags"]),
    ]
    caption = "\n".join(l for l in lines if l is not None).strip()
    caption = "\n".join(caption.split("\n\n\n"))
    return caption[:2200]                                # Instagram caption limit


# ---------------------------------------------------------------- Instagram Graph API
def graph(method, path, **params):
    version = os.environ.get("GRAPH_API_VERSION", "").strip()
    base = f"https://graph.facebook.com/{version + '/' if version else ''}"
    params["access_token"] = os.environ["IG_ACCESS_TOKEN"]
    data = urllib.parse.urlencode(params).encode()
    url = base + path
    if method == "GET":
        req = urllib.request.Request(url + "?" + data.decode())
    else:
        req = urllib.request.Request(url, data=data, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=90) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        body = e.read().decode(errors="replace")
        raise RuntimeError(f"Instagram API error on {path}: {e.code} {body}") from None

def wait_ready(container_id, what):
    for _ in range(30):                                  # up to ~5 minutes
        status = graph("GET", container_id, fields="status_code,status").get("status_code")
        if status == "FINISHED":
            return
        if status in ("ERROR", "EXPIRED"):
            raise RuntimeError(f"{what} failed with status {status}")
        time.sleep(10)
    raise RuntimeError(f"{what} was not ready after 5 minutes")

def post_carousel(image_urls, caption):
    ig = os.environ["IG_USER_ID"]
    children = []
    for i, url in enumerate(image_urls, 1):
        c = graph("POST", f"{ig}/media", image_url=url, is_carousel_item="true")["id"]
        wait_ready(c, f"image {i}")
        children.append(c)
    carousel = graph("POST", f"{ig}/media", media_type="CAROUSEL",
                     children=",".join(children), caption=caption)["id"]
    wait_ready(carousel, "carousel")
    return graph("POST", f"{ig}/media_publish", creation_id=carousel)["id"]

def find_existing_post(p1, p2, state):
    """If these pages were already published (e.g. the post worked but saving state.json failed),
    return that post's media id so we never publish the same pages twice."""
    marker = f"الصفحتان {ar(p1)} - {ar(p2)}"
    khatma = f"الختمة رقم {ar(state['khatma'])}"
    recent = graph("GET", f"{os.environ['IG_USER_ID']}/media", fields="id,caption", limit=5).get("data", [])
    for m in recent:
        caption = m.get("caption") or ""
        if marker in caption and khatma in caption:
            return m["id"]
    return None


# ---------------------------------------------------------------- page safety check
def load_fingerprints():
    fp = {}
    f = ROOT / "data" / "approved_pages.sha256"
    for line in f.read_text(encoding="utf-8").splitlines():
        if line.strip():
            digest, name = line.split()
            fp[name] = digest
    return fp

def verify_pages(pages):
    """Refuse to post unless each image's picture data is exactly the approved one."""
    sys.path.insert(0, str(ROOT / "tools"))
    from fingerprint import jpeg_fingerprint
    fp = load_fingerprints()
    if len(fp) != 604:
        sys.exit("STOP: approved_pages.sha256 must list all 604 pages.")
    for p in pages:
        name = f"images/page_{p:03d}.jpg"
        path = ROOT / name
        if not path.exists():
            sys.exit(f"STOP: {name} is missing.")
        if jpeg_fingerprint(path.read_bytes()) != fp.get(name):
            sys.exit(f"STOP: {name} is different from the approved page. Nothing was posted.")
    print(f"Pages {pages} match the approved fingerprints.")


# ---------------------------------------------------------------- main
def image_url(page):
    base = os.environ.get("IMAGE_BASE_URL", "").strip()
    if not base:
        repo = os.environ.get("GITHUB_REPOSITORY")      # set automatically inside GitHub Actions
        branch = os.environ.get("GITHUB_REF_NAME", "main")
        if not repo:
            base = "https://raw.githubusercontent.com/<your-user>/<your-repo>/main/images"
        else:
            base = f"https://raw.githubusercontent.com/{repo}/{branch}/images"
    return f"{base.rstrip('/')}/page_{page:03d}.jpg"

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", help="show today's post without publishing")
    ap.add_argument("--force", action="store_true", help="post even if already posted today")
    args = ap.parse_args()

    state = load_state()
    today = datetime.datetime.now(UAE).date().isoformat()
    if state.get("last_post_date") == today and not (args.force or args.dry_run):
        print(f"Already posted today ({today}). Nothing to do.")
        return

    p1 = state["next_page"]
    p2 = p1 + 1 if p1 < 604 else 1
    hadith = HADITHS[state["next_hadith"] % len(HADITHS)]
    caption = build_caption(p1, p2, hadith, state)
    urls = [image_url(p1), image_url(p2)]

    print("=" * 60)
    print(f"Date (UAE): {today}   pages: {p1}, {p2}   hadith: {hadith['book']} {hadith['number']}")
    print("\n".join(urls))
    print("-" * 60)
    print(caption)
    print("=" * 60)

    verify_pages([p1, p2])
    if args.dry_run:
        print("DRY RUN - nothing was published.")
        return
    if os.environ.get("POSTING_ENABLED", "").strip().lower() != "true":
        print("POSTING IS OFF - nothing was published.")
        print("To go live: repo Settings -> Secrets and variables -> Actions -> Variables -> POSTING_ENABLED = true")
        return

    media_id = find_existing_post(p1, p2, state)
    if media_id:
        print(f"Pages {p1}-{p2} were already published (media id {media_id}). Not posting again, only saving progress.")
    else:
        media_id = post_carousel(urls, caption)
        print(f"Published! Instagram media id: {media_id}")

    # move forward for tomorrow
    state["history"].append({"date": today, "pages": [p1, p2], "hadith": hadith.get("id"), "media_id": media_id})
    state["day"] += 1
    state["last_post_date"] = today
    state["next_hadith"] = (state["next_hadith"] + 1) % len(HADITHS)
    nxt = p2 + 1
    if nxt > 604:                                        # khatma completed -> start again
        nxt = 1
        state["khatma"] += 1
        state["day"] = 0
    state["next_page"] = nxt
    save_state(state)

if __name__ == "__main__":
    main()
