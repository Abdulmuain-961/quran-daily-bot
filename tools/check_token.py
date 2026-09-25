"""Check the Meta token and find the Instagram Business Account ID.

Run from GitHub:  Actions -> "Check token / find Instagram ID" -> Run workflow
(or locally:  IG_ACCESS_TOKEN=xxxx python tools/check_token.py)

It prints every Facebook Page the token can see and the Instagram account linked to it.
Copy the number shown as "Instagram ID" into the IG_USER_ID secret.
"""
import json, os, sys, urllib.error, urllib.parse, urllib.request

TOKEN = os.environ.get("IG_ACCESS_TOKEN", "").strip()
if not TOKEN:
    sys.exit("IG_ACCESS_TOKEN is empty. Add it in GitHub -> Settings -> Secrets and variables -> Actions.")

def get(path, **params):
    params["access_token"] = TOKEN
    url = "https://graph.facebook.com/" + path + "?" + urllib.parse.urlencode(params)
    try:
        with urllib.request.urlopen(url, timeout=60) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        return {"error": json.loads(e.read().decode(errors="replace")).get("error")}

me = get("me", fields="id,name")
if "error" in me:
    sys.exit(f"Token does not work: {me['error']}")
print(f"Token belongs to: {me.get('name')} ({me.get('id')})")

perms = get("me/permissions").get("data", [])
granted = sorted(p["permission"] for p in perms if p.get("status") == "granted")
print("Permissions:", ", ".join(granted) or "(could not read)")
for need in ("instagram_basic", "instagram_content_publish", "pages_show_list"):
    if granted and need not in granted:
        print(f"  !! missing permission: {need}")

pages = get("me/accounts", fields="id,name,instagram_business_account{id,username}").get("data", [])
if not pages:
    print("No Facebook Pages visible to this token. Assign the Page to the System User (see SETUP guide).")
for p in pages:
    ig = p.get("instagram_business_account")
    if ig:
        print(f"Page: {p['name']}  ->  Instagram @{ig.get('username')}   Instagram ID: {ig['id']}")
    else:
        print(f"Page: {p['name']}  ->  (no Instagram account linked)")

ig_id = os.environ.get("IG_USER_ID", "").strip()
if ig_id:
    r = get(ig_id, fields="username,media_count")
    if "error" in r:
        print(f"IG_USER_ID {ig_id} is NOT usable: {r['error']}")
    else:
        print(f"IG_USER_ID OK -> @{r.get('username')} ({r.get('media_count')} posts)")
    lim = get(f"{ig_id}/content_publishing_limit", fields="quota_usage,config")
    if "error" not in lim:
        print("Publishing limit:", lim.get("data"))
