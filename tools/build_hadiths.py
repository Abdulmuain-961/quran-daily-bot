"""Build data/hadiths.json — one short, authentic saying of the Prophet ﷺ per day.

Source: Sahih al-Bukhari, Arabic text from https://github.com/fawazahmed0/hadith-api
Only the Prophet's own words (the matn inside the quotes) are kept, plus the Companion who
narrated it and the hadith number, so the caption reads:

    قال رسول الله ﷺ:
    «...»
    رواه البخاري (1234) عن أبي هريرة رضي الله عنه

Hadith are kept only when they are ONE direct saying with no narrator remarks inside it,
no missing context, and a clearly named Companion. Numbers listed in data/hadith_exclude.txt
are skipped (use that file to remove any hadith you do not want to post), one per line
like:  bukhari 6018   or   muslim 534

Usage:  python tools/build_hadiths.py [folder containing bukhari.json and muslim.json]
(with no folder the two books are downloaded)
"""
import difflib, json, random, re, sys, urllib.request, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
BASE = "https://raw.githubusercontent.com/fawazahmed0/hadith-api/1/editions/"
BOOKS = [("bukhari", "ara-bukhari.json"), ("muslim", "ara-muslim.json")]
OUT = ROOT / "data" / "hadiths.json"
EXCLUDE = ROOT / "data" / "hadith_exclude.txt"

DIAC = re.compile(r"[ً-ْٰـ]")
def plain(s):
    return DIAC.sub("", s)

# Companion (as written after "عن" in the chain, without harakat)  ->  how it is shown in the caption
COMPANIONS = {
    "أبي هريرة": "أبي هريرة رضي الله عنه",
    "ابن عمر": "ابن عمر رضي الله عنهما",
    "عبد الله بن عمر": "عبد الله بن عمر رضي الله عنهما",
    "ابن عباس": "ابن عباس رضي الله عنهما",
    "عبد الله بن عباس": "ابن عباس رضي الله عنهما",
    "أنس": "أنس بن مالك رضي الله عنه",
    "أنس بن مالك": "أنس بن مالك رضي الله عنه",
    "عائشة": "عائشة رضي الله عنها",
    "أبي سعيد": "أبي سعيد الخدري رضي الله عنه",
    "أبي سعيد الخدري": "أبي سعيد الخدري رضي الله عنه",
    "جابر": "جابر بن عبد الله رضي الله عنهما",
    "جابر بن عبد الله": "جابر بن عبد الله رضي الله عنهما",
    "أبي موسى": "أبي موسى الأشعري رضي الله عنه",
    "أبي موسى الأشعري": "أبي موسى الأشعري رضي الله عنه",
    "ابن مسعود": "ابن مسعود رضي الله عنه",
    "عبد الله بن مسعود": "ابن مسعود رضي الله عنه",
    "عبد الله بن عمرو": "عبد الله بن عمرو رضي الله عنهما",
    "عمر": "عمر بن الخطاب رضي الله عنه",
    "عمر بن الخطاب": "عمر بن الخطاب رضي الله عنه",
    "علي": "علي بن أبي طالب رضي الله عنه",
    "عثمان": "عثمان بن عفان رضي الله عنه",
    "أبي ذر": "أبي ذر رضي الله عنه",
    "النعمان بن بشير": "النعمان بن بشير رضي الله عنهما",
    "سهل بن سعد": "سهل بن سعد رضي الله عنه",
    "سهل": "سهل بن سعد رضي الله عنه",
    "أبي مسعود": "أبي مسعود الأنصاري رضي الله عنه",
    "أبي أيوب": "أبي أيوب الأنصاري رضي الله عنه",
    "أبي بكرة": "أبي بكرة رضي الله عنه",
    "البراء": "البراء بن عازب رضي الله عنهما",
    "البراء بن عازب": "البراء بن عازب رضي الله عنهما",
    "أبي قتادة": "أبي قتادة رضي الله عنه",
    "المغيرة بن شعبة": "المغيرة بن شعبة رضي الله عنه",
    "المغيرة": "المغيرة بن شعبة رضي الله عنه",
    "حذيفة": "حذيفة بن اليمان رضي الله عنه",
    "معاذ": "معاذ بن جبل رضي الله عنه",
    "معاذ بن جبل": "معاذ بن جبل رضي الله عنه",
    "عدي بن حاتم": "عدي بن حاتم رضي الله عنه",
    "سلمان الفارسي": "سلمان الفارسي رضي الله عنه",
    "أسامة بن زيد": "أسامة بن زيد رضي الله عنهما",
    "عمران بن حصين": "عمران بن حصين رضي الله عنهما",
    "أم سلمة": "أم سلمة رضي الله عنها",
    "سعد": "سعد بن أبي وقاص رضي الله عنه",
    "سعد بن أبي وقاص": "سعد بن أبي وقاص رضي الله عنه",
    "حكيم بن حزام": "حكيم بن حزام رضي الله عنه",
    "عبادة بن الصامت": "عبادة بن الصامت رضي الله عنه",
    "الزبير بن العوام": "الزبير بن العوام رضي الله عنه",
    "المقدام بن معديكرب": "المقدام بن معديكرب رضي الله عنه",
    "أبي شريح": "أبي شريح العدوي رضي الله عنه",
    "جرير بن عبد الله": "جرير بن عبد الله رضي الله عنه",
    "جرير": "جرير بن عبد الله رضي الله عنه",
    "عبد الله بن زيد": "عبد الله بن زيد رضي الله عنه",
    "عبد الله بن مغفل": "عبد الله بن مغفل رضي الله عنه",
    "عقبة بن عامر": "عقبة بن عامر رضي الله عنه",
    "أبي الدرداء": "أبي الدرداء رضي الله عنه",
    "أبي أمامة": "أبي أمامة رضي الله عنه",
    "كعب بن مالك": "كعب بن مالك رضي الله عنه",
    "عبد الرحمن بن سمرة": "عبد الرحمن بن سمرة رضي الله عنه",
    "سمرة بن جندب": "سمرة بن جندب رضي الله عنه",
    "أبي بكر": "أبي بكر الصديق رضي الله عنه",
    "مالك بن الحويرث": "مالك بن الحويرث رضي الله عنه",
    "معاوية": "معاوية رضي الله عنه",
    "أبي برزة": "أبي برزة الأسلمي رضي الله عنه",
    "ميمونة": "ميمونة رضي الله عنها",
    "حفصة": "حفصة رضي الله عنها",
    "زيد بن خالد": "زيد بن خالد الجهني رضي الله عنه",
    "تميم الداري": "تميم الداري رضي الله عنه",
    "أبي مالك الأشعري": "أبي مالك الأشعري رضي الله عنه",
    "صهيب": "صهيب الرومي رضي الله عنه",
    "النواس بن سمعان": "النواس بن سمعان رضي الله عنه",
    "ثوبان": "ثوبان رضي الله عنه",
    "أبي بن كعب": "أبي بن كعب رضي الله عنه",
    "عبد الله بن عمرو بن العاص": "عبد الله بن عمرو رضي الله عنهما",
    "أبي هريرة، قال": "أبي هريرة رضي الله عنه",
}

SAYING = re.compile(
    r"(?:عن|سمعت|سمع|أن|إن)\s*[ ،,]*"
    r"(?:(?P<name>[ء-ي ]{2,25}?)[ ،,]*(?:رضى? الله عن(?:ه|ها|هما))?[ ،,]*)"
    r"(?:قال|قالت|يقول|أنه قال|أنه سمع|،)?\s*"
    r"(?:قال|أن|سمعت)?\s*(?:رسول الله|النبي|رسول الله|النبي)\s*صلى الله عليه وسلم\s*"
    r"(?:قال|يقول|أنه قال)?\s*\"(?P<matn>[^\"]+)\"\s*[.‏]*\s*$"
)
# narrator remarks, doubts or references that must NOT appear inside the Prophet's words
BAD_MATN = re.compile(r"( - |أحسبه|وفي رواية|إلى قوله|\?|\{|قال وإن|وربما قال|أو قال|قال أبو|قال شعبة|قال سفيان|يعني|شك |الراوي|بهذا|مثله|نحوه|فذكر|الحديث)")
# topics that need a teacher's explanation and read poorly as a stand-alone caption
SKIP = re.compile(r"(أعتق|عتق|عبد|مملوك|جارية|الوطء|حيض|حاضت|الحائض|جنب|الجنابة|ضراط|فساء|بول|يبول|غائط|استنجى|الخلاء|المني|محتلم|قتل|يقتل|اقتلوا|قاتل|أقاتل|الحدود|رجم|جلد|السارق|تقطع|الكلب|كلب|الخمر|الربا|ربا|الطلاق|طلق|الميراث|فرائض|لورثته|العرايا|المزابنة|المحاقلة|باع|بيع|يبيع|البيعان|المبتاع|السلم|شاة|الغنم|الإبل|بعير|الدجال|يونس|اليهود|يهود|النصارى|الأنصار|قريش|الحبشة|حبشي|غزوة|سلاح|السيف|بنبل|عورة|فرج|النساء|نساء|المرأة|امرأة|نكاح|ينكح|تنكح|الوصية|أوصى|يحلف|يمين|جبار|الركاز|المعدن|الخازن|حمار|أحرق|يحنط|تحنطوه|كفنوه|اغسلوه|الجنازة|قبورا|الكعبة|يخرب|ذبيحة|ذبيحتنا|أبر|الذهب|الحرير|صورة|صور|التصاوير|المصورون|الشعر|الكهان|السحر|الطيرة|العدوى)")

def clean(t):
    t = t.replace("‏", "").replace("‎", "")
    t = t.replace(" ـ ", " ").replace("ـ", "")
    t = re.sub(r"صَ?لَّ?ى ?اللَّهُ ?عَلَيْهِ ?وَ?سَلَّمَ", "ﷺ", t)
    t = re.sub(r"\s+", " ", t).strip(" ،,.")
    t = t.replace(" .", ".").replace(" ،", "،")
    return t

def matn_from(text):
    """return (companion display name, matn with harakat) or None"""
    p = plain(text).replace("‏", "").replace("‎", "").replace("ـ", "")
    p = re.sub(r"\s+", " ", p).strip()
    m = SAYING.search(p)
    if not m or p.count('"') != 2:
        return None
    name = (m.group("name") or "").strip(" ،,")
    name = re.sub(r"^(?:عن|سمعت|سمع|أن|إن)\s+", "", name)
    comp = COMPANIONS.get(name)
    if not comp:
        return None
    if BAD_MATN.search(m.group("matn")) or SKIP.search(m.group("matn")):
        return None
    # take the matn WITH harakat from the original text (between the two quote marks)
    raw = text.replace("‏", "").replace("‎", "")
    matn = raw.split('"')[1]
    return comp, clean(matn)

def letters(s):
    return re.sub(r"[^\u0621-\u064A]", "", s.replace("أ", "ا").replace("إ", "ا").replace("آ", "ا").replace("ة", "ه").replace("ى", "ي"))

def similar(matn_plain, found):
    """return the key of an already-kept hadith with (almost) the same wording, else None"""
    a = letters(matn_plain)
    for k, item in found.items():
        b = item["_letters"]
        if abs(len(a) - len(b)) > 0.5 * max(len(a), len(b)):
            continue
        if difflib.SequenceMatcher(None, a, b, autojunk=False).ratio() > 0.6:
            return k
    return None

def load(book, fname, folder):
    if folder:
        return json.load(open(pathlib.Path(folder) / f"{book}.json", encoding="utf-8"))
    return json.load(urllib.request.urlopen(BASE + fname))

def main():
    folder = sys.argv[1] if len(sys.argv) > 1 else None
    excluded = set()
    if EXCLUDE.exists():
        for line in EXCLUDE.read_text(encoding="utf-8").splitlines():
            line = line.split("#")[0].strip()
            if line:
                excluded.add(line)          # e.g. "bukhari 6018" or "muslim 534"
    found = {}                               # key -> item
    for book, fname in BOOKS:
        data = load(book, fname, folder)
        for h in data["hadiths"]:
            t = h["text"].strip()
            num = int(h["hadithnumber"])
            if not t:
                continue
            r = matn_from(t)
            if not r:
                continue
            comp, matn = r
            n = len(plain(matn))
            if n < 35 or n > 380:
                continue
            key = re.sub(r"[^\u0621-\u064A]", "", plain(matn))[:40]
            dup = key if key in found else similar(plain(matn), found)
            if dup:
                key = dup
                found[key]["_members"].append(f"{book} {num}")
                if found[key]["book"] == "bukhari" and book == "muslim":
                    found[key]["agreed"] = True     # same hadith in both books = متفق عليه
                continue
            found[key] = {"id": f"{book} {num}", "book": book, "number": num,
                          "narrator": comp, "text": matn, "agreed": False,
                          "_letters": letters(plain(matn)), "_members": [f"{book} {num}"]}
    # drop a hadith (and all its other wordings) when any of its numbers is in the exclude list
    out = [{k: v for k, v in x.items() if not k.startswith("_")}
           for x in found.values() if not excluded.intersection(x["_members"])]
    # mix the topics so consecutive days are different (fixed seed = same order every build)
    random.Random(604).shuffle(out)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    json.dump(out, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"saved {len(out)} hadiths -> {OUT}  (agreed upon: {sum(x['agreed'] for x in out)})")

if __name__ == "__main__":
    main()
