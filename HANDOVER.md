# دليل الأمانة — لمن يتولى رعاية هذا البوت
# Handover guide — for the person who takes care of this bot

بسم الله الرحمن الرحيم

هذا البوت صدقة جارية أنشأه **عبدالمعين**. ينشر كل يوم صفحتين من المصحف مع حديث صحيح
على حسابه في إنستغرام، ويختم القرآن كل ٣٠٢ يوم ثم يبدأ من جديد.
إذا وصلك هذا الملف فأنت مؤتمن على استمراره، جزاك الله خيراً.

This bot is an ongoing charity (صدقة جارية). It needs almost no work — usually **nothing for years**.
You only step in when GitHub emails you that a run failed.

---

## ١. ما الذي يجب أن يكون معك | What you need access to

| # | الحساب / Account | لماذا / Why |
|---|---|---|
| 1 | حساب **GitHub** الذي فيه المستودع `quran-daily-bot` (أو أن تُضاف كـ Collaborator) | فيه البوت وجدول النشر |
| 2 | **Meta Business portfolio** (business.facebook.com) كمسؤول Admin | لإنشاء مفتاح (token) جديد عند الحاجة |
| 3 | حساب **إنستغرام** وصفحة **فيسبوك** المرتبطة به (كمسؤول) | حتى لا ينقطع الحساب |
| 4 | البريد الإلكتروني المرتبط بـ GitHub | لتصلك رسائل الأخطاء |

> ⚠️ **مهم جداً:** لا تطلب من إنستغرام أو فيسبوك تحويل الحساب إلى «حساب تذكاري» (Memorialized).
> الحساب التذكاري **لا يمكن النشر عليه**، فيتوقف البوت نهائياً.
> **Important:** do not request memorialization of the Instagram/Facebook account — a memorialized
> account can no longer be posted to, and the bot would stop forever.

---

## ٢. كيف أعرف أنه يعمل؟ | How do I know it's working?

- افتح الحساب على إنستغرام: يجب أن يظهر منشور جديد كل صباح.
- أو افتح GitHub → المستودع → تبويب **Actions**: كل يوم تشغيل بعلامة ✓ خضراء.
- الملف `state.json` يبيّن الصفحة القادمة (`next_page`) ورقم الختمة (`khatma`).

---

## ٣. إذا توقف البوت | If the bot stops

افتح **Actions** → افتح آخر تشغيل باللون الأحمر ✗ → اقرأ الخطوة الحمراء، ثم:

| ما يظهر في السجل / Log shows | الحل / Fix |
|---|---|
| `(#190) Invalid OAuth access token` | المفتاح لم يعد يعمل. أنشئ مفتاحاً جديداً (القسم ٤) وضعه مكان `IG_ACCESS_TOKEN`. |
| `(#10)` أو `(#200)` أو `permission` | صلاحية ناقصة. أنشئ مفتاحاً جديداً مع كل الصلاحيات المذكورة في القسم ٤. |
| `Media download has failed` | تأكد أن المستودع **Public** وأن مجلد `images` فيه ٦٠٤ صورة. |
| `STOP: ... is different from the approved page` أو `missing` | صورة صفحة تغيّرت أو حُذفت. أعد الملف الأصلي من النسخة الاحتياطية. **البوت لا ينشر أي صفحة لا تطابق البصمة المعتمدة** — هذا حماية لكتاب الله، لا تعطّلها. |
| `version ... is deprecated` أو `Unsupported` | ميتا غيّرت إصدار الواجهة. غالباً يكفي حذف المتغير `GRAPH_API_VERSION` إن وُجد (Settings → Variables). وإلا اطلب من شخص يعرف Python مراجعة `bot.py` (الدوال `graph` و `post_carousel`). |
| `actions/checkout` أو `Node` deprecated | حدّث رقم الإصدار في ملفات `.github/workflows/*.yml` (مثلاً `actions/checkout@v5` → أحدث إصدار). |
| `POSTING IS OFF` | ليس خطأ: مفتاح التشغيل مغلق. لتشغيل النشر اجعل المتغير `POSTING_ENABLED` = `true` (Settings → Secrets and variables → Actions → Variables). |
| `were already published ... Not posting again` | ليس خطأ: نُشرت الصفحتان سابقاً لكن حفظ التقدم فشل، فاكتشف البوت ذلك من إنستغرام وحفظ التقدم فقط دون نشر مكرر. |
| لا يوجد أي تشغيل منذ مدة / No runs at all | GitHub يوقف الجدولة إذا لم يحدث أي نشاط في المستودع ٦٠ يوماً. ادخل Actions → Daily Quran post → **Enable workflow**، ثم شغّله يدوياً مرة. |

بعد أي إصلاح: Actions → **Daily Quran post** → **Run workflow** مع إزالة علامة *Only show today's post* لتنشر منشور اليوم.

---

## ٤. إنشاء مفتاح جديد لا ينتهي | Make a new never-expiring token

1. business.facebook.com → ⚙️ **Settings** → **Users → System users** → اختر `quran-bot`.
2. **Generate new token** → التطبيق `Quran Daily Bot` → مدة الصلاحية **Never**.
3. اختر الصلاحيات:
   `instagram_basic`, `instagram_content_publish`, `pages_show_list`, `pages_read_engagement`, `business_management`
4. انسخ المفتاح → GitHub → المستودع → **Settings → Secrets and variables → Actions** →
   `IG_ACCESS_TOKEN` → **Update** → الصق → احفظ.
5. Actions → **Check token / find Instagram ID** → Run → تأكد أنه يقول `IG_USER_ID OK`.

(التفاصيل الكاملة مع الصور خطوة بخطوة في `SETUP.md`.)

---

## ٥. أمور يمكنك تغييرها بأمان | Safe things to change

- إيقاف النشر مؤقتاً: اجعل المتغير `POSTING_ENABLED` = `false`، وأعده `true` للاستئناف
- نص العنوان والهاشتاقات: `config.json`
- وقت النشر: السطران `cron` في `.github/workflows/daily-post.yml` (بتوقيت UTC = توقيت الإمارات − ٤ ساعات)
- حذف حديث: أضف رقمه في `data/hadith_exclude.txt` واحذف مدخله من `data/hadiths.json`
- لا تعدّل `state.json` إلا إذا أردت تغيير الصفحة القادمة (رقم فردي: ١، ٣، ٥ …)

## ٦. صفحات المصحف | The Mushaf pages

الصفحات مأخوذة كما هي من ملف المصحف الرسمي لمجمع الملك فهد (مصحف المدينة النبوية، رواية حفص)،
بدون أي تعديل على النص، وراجعها حافظ قبل التشغيل. لكل صفحة بصمة رقمية في `data/approved_pages.sha256`،
والبوت يرفض النشر إذا اختلفت الصورة ولو بنقطة. **لا تستبدل الصور بمصدر آخر** إلا بعد مراجعة حافظ جديدة
وإعادة إنشاء البصمات (`tools/make_manifest.py`).

## ٧. ملاحظة عن الأحاديث | About the hadith

كل الأحاديث من **صحيح البخاري** و**صحيح مسلم** فقط، ونُقل لفظ النبي ﷺ كما هو.
أرقام البخاري هي الترقيم المشهور، ويمكن التحقق من أي حديث على **dorar.net**.
إن وجدت خطأً في أي نص فاحذفه من القائمة (القسم ٥) — الاحتياط في حديث رسول الله ﷺ أولى.

جزاك الله خيراً، وجعله في ميزان حسناتك وحسنات صاحبه.
