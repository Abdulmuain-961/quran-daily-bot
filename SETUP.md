# Setup guide — دليل التشغيل

Total time: about 45 minutes, once. After that the bot runs by itself every day.
المدة: حوالي ٤٥ دقيقة مرة واحدة فقط، وبعدها يعمل البوت وحده كل يوم.

You need:
- ✅ Instagram **Professional** account linked to a **Facebook Page** (done)
- A free **GitHub** account
- A **Meta Business portfolio** (business.facebook.com) that contains your Page and Instagram account

---

## Part 0 — Hafiz review (before anything else) | مراجعة الحافظ أولاً

Give `review/quran_pages_review.pdf` to a hafiz or Quran teacher you trust.
It shows all 604 pages **exactly as they will be posted**, two per sheet like an open Mushaf.
Under each page is its number and a short fingerprint code. They tick each page, and tell you
if anything is wrong. **Do not go live until every page is approved.**

أعطِ ملف `review/quran_pages_review.pdf` لحافظ أو معلم قرآن تثق به. فيه الصفحات الـ٦٠٤ كما ستُنشر تماماً.
لا تبدأ النشر قبل موافقته على كل الصفحات.

## Part 1 — Put the bot on GitHub (١٥ دقيقة)

1. Go to **github.com** → sign up (free) or sign in.
2. Top-right **+** → **New repository**
   - Name: `quran-daily-bot`
   - Choose **Public** ← important: Instagram must be able to download the page images from it.
     Your token stays secret (secrets are never visible to anyone, even in a public repo).
   - Click **Create repository**.
3. The bot includes 604 page images (about 230 MB), which is too many for the website upload.
   Use the free **GitHub Desktop** app (desktop.github.com):
   - Install it and sign in → **File → Clone repository** → choose `quran-daily-bot` → pick a folder.
   - Unzip `quran-daily-bot.zip` and copy **everything inside it** (including the hidden `.github`
     folder and the `images` folder) into that cloned folder. You don't need the `review` folder.
   - Back in GitHub Desktop: write "first upload" in *Summary* → **Commit to main** → **Push origin**.
4. Open the **Actions** tab on github.com. You should see 2 workflows:
   *Daily Quran post* and *Check token / find Instagram ID*.
   If GitHub asks, click **I understand my workflows, go ahead and enable them**.
   > If you don't see them, the `.github` folder was not uploaded (Windows sometimes hides it).
   > Click **Add file → Create new file**, type the name `.github/workflows/daily-post.yml`,
   > paste the content of that file, commit, and repeat for the other two files.
5. Check that the `images` folder on github.com shows 604 files (page_001.jpg … page_604.jpg).

## Part 2 — Get a token that never expires from Meta (٢٠ دقيقة)

A *token* is the key that lets the bot post on your account. We create it for a **System User**
(a robot user inside your Meta business), so it does **not** expire and is **not** linked to your password.

1. Go to **developers.facebook.com** → **My Apps** → **Create App**.
   - App name: `Quran Daily Bot`
   - Use case: choose the Instagram option (e.g. *"Manage messaging & content on Instagram"*),
     or **Other** → app type **Business**.
   - Connect it to your **Business portfolio** when asked.
   - If the dashboard offers to add the **Instagram** product (*API setup with Facebook login*), add it.
2. Go to **business.facebook.com** → ⚙️ **Settings** → **Users → System users** → **Add**
   - Name: `quran-bot`, role: **Admin** → Create.
3. With `quran-bot` selected click **Assign assets**:
   - **Apps** → `Quran Daily Bot` → **Full control**
   - **Pages** → your Page → **Full control**
   - **Instagram accounts** → your account → **Full control** (if this option is shown)
4. Click **Generate new token**:
   - App: `Quran Daily Bot`
   - Token expiration: **Never**
   - Permissions (tick all of these):
     `instagram_basic`, `instagram_content_publish`, `pages_show_list`,
     `pages_read_engagement`, `business_management`
   - **Generate token** → **copy it now** and keep it somewhere safe (it is shown only once).

## Part 3 — Give the token to the bot (٥ دقائق)

1. GitHub repo → **Settings** → **Secrets and variables** → **Actions** → **New repository secret**
   - Name: `IG_ACCESS_TOKEN` → Secret: paste the token → **Add secret**
2. Actions → **Check token / find Instagram ID** → **Run workflow**. Open the run and read the log.
   You will see a line like:
   `Page: My Page  ->  Instagram @myaccount   Instagram ID: 17841400000000000`
3. Add a second secret:
   - Name: `IG_USER_ID` → Secret: that Instagram ID number
4. Run **Check token / find Instagram ID** again → it should say `IG_USER_ID OK -> @youraccount`.

## Part 4 — Test and go live (٥ دقائق)

1. Actions → **Daily Quran post** → **Run workflow** (leave *"Only show today's post"* ticked) → Run.
   Open the log: you will see today's pages and the full caption. Nothing is published.
2. **Only after the hafiz has approved every page**, turn on the switch:
   repo → **Settings** → **Secrets and variables** → **Actions** → **Variables** tab → **New repository variable**
   - Name: `POSTING_ENABLED` → Value: `true` → **Add variable**
   > Until this variable says `true`, the bot never publishes anything — not on schedule, not by hand.
   > The log just says `POSTING IS OFF - nothing was published.`
3. **Run workflow** again and **untick** *"Only show today's post"*.
   → The first post goes live on your Instagram (pages 1 & 2).
4. Done ✅ From tomorrow it posts automatically at about **6:00 AM UAE time**.
   Every post saves its progress in `state.json`, so it always continues from the right page.

---

## Changing things later

| I want to… | Do this |
|---|---|
| Change the caption title, footer or hashtags | Edit `config.json` on GitHub (pencil icon) → Commit |
| Change the time | Edit the two `cron:` lines in `.github/workflows/daily-post.yml`. Times are **UTC** = UAE time − 4 hours. Example: `"53 1 * * *"` = 01:53 UTC = 05:53 UAE |
| Start from a different page | Edit `state.json` → change `"next_page"` to an **odd** number (1, 3, 5 …) |
| Remove a hadith I don't want | Add a line like `bukhari 6018` to `data/hadith_exclude.txt`, then ask someone to re-run `python tools/build_hadiths.py` (or remove its entry from `data/hadiths.json` directly) |
| Pause the bot | Change the variable `POSTING_ENABLED` to `false` (Settings → Secrets and variables → Actions → Variables). Set it back to `true` to resume. |

## If something goes wrong

GitHub emails you when a daily run fails. Open the failed run in **Actions** and look at the red step:

| Message in the log | Fix |
|---|---|
| `STOP: images/page_N.jpg is missing` | Upload the `images` folder again with GitHub Desktop. |
| `STOP: ... is different from the approved page` | A page image was changed. Put back the original file from the zip. The bot will not post until it matches. |
| `Media download has failed` / `could not be fetched` | The repo must be **Public**. Or add a repository *variable* `IMAGE_BASE_URL` = `https://cdn.jsdelivr.net/gh/YOUR-USER/quran-daily-bot@main/images` |
| `(#10) ... permission` or `(#200)` | The token is missing `instagram_content_publish`, or the app must be switched to **Live** in developers.facebook.com (it asks for a Privacy Policy URL — you can use the link to your repo's README). Generate a new token after fixing. |
| `(#190) Invalid OAuth access token` | The token was deleted or the System User lost access. Generate a new token (Part 2, step 4) and update the `IG_ACCESS_TOKEN` secret. |
| `Unsupported get request` / `does not exist` for the user id | Wrong `IG_USER_ID`. Run **Check token / find Instagram ID** and copy the right number. |
| `Already posted today` | Not an error — the backup run saw that today's post was already published. |
| `POSTING IS OFF` | Not an error — the switch is off. Set the variable `POSTING_ENABLED` to `true` to go live. |
| `were already published ... Not posting again` | Not an error — the post went out but saving progress failed last time. The bot saw the post on Instagram and only saved progress. |
