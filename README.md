# Quran Daily Bot — بوت الورد اليومي

Every morning (~6:00 AM UAE time) this bot posts **2 pages of the Mushaf** to Instagram as a carousel,
with **a different authentic hadith** (Sahih al-Bukhari / Sahih Muslim) in the caption.
2 pages a day = a complete khatma every 302 days, then it starts again automatically.

ينشر البوت كل يوم صفحتين من المصحف على إنستغرام مع حديث صحيح مختلف كل يوم،
ويختم القرآن كل ٣٠٢ يوم ثم يبدأ ختمة جديدة تلقائياً. يعمل مجاناً على GitHub بدون أي جهاز.

- **Setting it up the first time:** read [SETUP.md](SETUP.md)
- **If you are taking care of this bot (maintenance):** read [HANDOVER.md](HANDOVER.md)

## What is in this folder

| File / folder | What it does |
|---|---|
| `bot.py` | The daily poster. Reads `state.json`, posts the next 2 pages, saves progress. |
| `state.json` | Where the bot stopped (next page, next hadith, khatma number). |
| `config.json` | Caption title, footer text, hashtags, starting page. Safe to edit. |
| `data/pages.json` | Surah names + juz for all 604 pages. |
| `data/hadiths.json` | The list of 313 hadith used in the captions (one per day, in a mixed order). |
| `data/hadith_exclude.txt` | Hadith that were removed on purpose. Add a number here to remove one. |
| `images/` | The 604 page images, taken unchanged from the official King Fahd Complex PDF. |
| `data/approved_pages.sha256` | Digital fingerprint of every approved page. The bot refuses to post a page that doesn't match. |
| `review/quran_pages_review.pdf` | All 604 pages as they will be posted, for the hafiz review (not needed on GitHub). |
| `tools/` | Helper scripts (rebuild images from the PDF, fingerprints, review file, hadith list, check token). |
| `.github/workflows/` | The 2 automatic jobs: daily post and check token. |

## Sources

- Mushaf pages: the official printed **Mushaf al-Madinah an-Nabawiyyah** (Hafs), King Fahd Glorious Quran
  Printing Complex — PDF `standard1-quran.pdf` (625 pages, a waqf edition "not for sale"),
  SHA-256 `be0091b2fac87706c240f27398e00e7848daebbd69f7ec437859f66fca15d562`.
  PDF pages 4–607 = Mushaf pages 1–604. Each page image is extracted exactly as stored in the PDF;
  only the blank white margin is trimmed and the page is scaled onto a white 1080×1350 canvas.
  Every printed page number (3–604) was checked against its position.
- Page → surah / juz data: [fawazahmed0/quran-api](https://github.com/fawazahmed0/quran-api)
- Hadith text: [fawazahmed0/hadith-api](https://github.com/fawazahmed0/hadith-api) (Sahih al-Bukhari, Sahih Muslim).
  Bukhari numbers are the standard numbering (you can verify any hadith on dorar.net).
- Font: Amiri (SIL Open Font License, see `assets/OFL.txt`).
