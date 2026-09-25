"""Build data/pages.json — for each of the 604 Madani mushaf pages: surah name(s), juz, first/last ayah.
Source: https://github.com/fawazahmed0/quran-api (info.json). Run once: python tools/build_pages.py"""
import json, pathlib, sys, urllib.request

SRC = "https://raw.githubusercontent.com/fawazahmed0/quran-api/1/info.json"
OUT = pathlib.Path(__file__).resolve().parent.parent / "data" / "pages.json"

SURAHS = """الفاتحة البقرة آل_عمران النساء المائدة الأنعام الأعراف الأنفال التوبة يونس هود يوسف الرعد إبراهيم الحجر النحل
الإسراء الكهف مريم طه الأنبياء الحج المؤمنون النور الفرقان الشعراء النمل القصص العنكبوت الروم لقمان السجدة الأحزاب سبأ فاطر
يس الصافات ص الزمر غافر فصلت الشورى الزخرف الدخان الجاثية الأحقاف محمد الفتح الحجرات ق الذاريات الطور النجم القمر الرحمن
الواقعة الحديد المجادلة الحشر الممتحنة الصف الجمعة المنافقون التغابن الطلاق التحريم الملك القلم الحاقة المعارج نوح الجن
المزمل المدثر القيامة الإنسان المرسلات النبأ النازعات عبس التكوير الانفطار المطففين الانشقاق البروج الطارق الأعلى الغاشية
الفجر البلد الشمس الليل الضحى الشرح التين العلق القدر البينة الزلزلة العاديات القارعة التكاثر العصر الهمزة الفيل قريش
الماعون الكوثر الكافرون النصر المسد الإخلاص الفلق الناس""".split()
SURAHS = [s.replace("_", " ") for s in SURAHS]
assert len(SURAHS) == 114, len(SURAHS)

def main():
    info = json.load(open(sys.argv[1], encoding="utf-8")) if len(sys.argv) > 1 else json.load(urllib.request.urlopen(SRC))
    juz_of = {}
    for ch in info["chapters"]:
        for v in ch["verses"]:
            juz_of[(ch["chapter"], v["verse"])] = v["juz"]
    pages = []
    for ref in info["pages"]["references"]:
        s, e = ref["start"], ref["end"]
        pages.append({
            "page": ref["page"],
            "surahs": [SURAHS[i - 1] for i in range(s["chapter"], e["chapter"] + 1)],
            # juz as printed in the header of the Madinah Mushaf: juz k starts on page 20k-18
            "juz": 1 if ref["page"] < 22 else min(30, (ref["page"] - 2) // 20 + 1),
            "start": [s["chapter"], s["verse"]],
            "end": [e["chapter"], e["verse"]],
        })
    assert len(pages) == 604
    OUT.parent.mkdir(parents=True, exist_ok=True)
    json.dump(pages, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"saved {len(pages)} pages -> {OUT}")

if __name__ == "__main__":
    main()
