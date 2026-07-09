#!/usr/bin/env python3
"""Render creators.json into index.html for GitHub Pages.

Emails are base64-encoded in the markup and revealed on click. That stops
casual scrapers and search indexing, not a determined reader.

Each creator card has a stable anchor (#c-<handle>) so the sheet can deep-link
a row straight to its own email copy. Subject and body are editable and
autosave to the reader's localStorage; there is no backend.
"""
import base64
import html
import json
import pathlib

HERE = pathlib.Path(__file__).parent
data = json.loads((HERE / "creators.json").read_text())
BASE = "https://thepmfguy.github.io/masonry-creator-outreach/"

CSS = """
:root{--bg:#fbfbfa;--fg:#1c1b1a;--muted:#6f6c68;--line:#e3e1dd;--card:#fff;--accent:#3d5afe;--warn-bg:#fff5e6;--warn-fg:#7a4f00;--warn-line:#f0d9ae;--hi:#fff9e6}
@media (prefers-color-scheme:dark){:root{--bg:#131312;--fg:#eceae7;--muted:#9a9791;--line:#2e2d2b;--card:#1b1b1a;--accent:#8fa2ff;--warn-bg:#2b2214;--warn-fg:#f0c987;--warn-line:#4a3a1c;--hi:#26220f}}
:root[data-theme=dark]{--bg:#131312;--fg:#eceae7;--muted:#9a9791;--line:#2e2d2b;--card:#1b1b1a;--accent:#8fa2ff;--warn-bg:#2b2214;--warn-fg:#f0c987;--warn-line:#4a3a1c;--hi:#26220f}
:root[data-theme=light]{--bg:#fbfbfa;--fg:#1c1b1a;--muted:#6f6c68;--line:#e3e1dd;--card:#fff;--accent:#3d5afe;--warn-bg:#fff5e6;--warn-fg:#7a4f00;--warn-line:#f0d9ae;--hi:#fff9e6}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--fg);font:16px/1.6 ui-sans-serif,-apple-system,"Segoe UI",Inter,sans-serif;-webkit-font-smoothing:antialiased}
.wrap{max-width:820px;margin:0 auto;padding:48px 20px 96px}
h1{font-size:1.7rem;letter-spacing:-.02em;margin:0 0 6px}
.sub{color:var(--muted);margin:0 0 28px}
.note{background:var(--warn-bg);color:var(--warn-fg);border:1px solid var(--warn-line);border-radius:10px;padding:12px 16px;margin:0 0 32px;font-size:.9rem}
.card{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:22px;margin:0 0 22px;scroll-margin-top:20px}
.card:target{border-color:var(--accent);box-shadow:0 0 0 3px color-mix(in srgb,var(--accent) 18%,transparent)}
.top{display:flex;flex-wrap:wrap;gap:10px;align-items:baseline;justify-content:space-between;margin-bottom:4px}
.handle{font-size:1.15rem;font-weight:650;letter-spacing:-.01em}
.handle a{color:inherit;text-decoration:none;border-bottom:1px solid var(--line)}
.handle a:hover{border-color:var(--accent)}
.badges{display:flex;gap:6px;flex-wrap:wrap}
.badge{font-size:.72rem;text-transform:uppercase;letter-spacing:.07em;padding:3px 9px;border-radius:99px;border:1px solid var(--line);color:var(--muted);white-space:nowrap}
.badge.sent{background:var(--warn-bg);color:var(--warn-fg);border-color:var(--warn-line)}
.badge.edited{border-color:var(--accent);color:var(--accent);display:none}
.card.is-edited .badge.edited{display:inline-block}
.meta{color:var(--muted);font-size:.85rem;margin-bottom:14px}
.hook{font-size:.9rem;color:var(--muted);border-left:2px solid var(--line);padding-left:12px;margin:0 0 18px}
.field{margin-bottom:14px}
.label{font-size:.72rem;text-transform:uppercase;letter-spacing:.07em;color:var(--muted);display:flex;align-items:center;gap:8px;margin-bottom:6px}
.label .sp{flex:1}
.val{font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-size:.86rem;background:var(--bg);border:1px solid var(--line);border-radius:8px;padding:10px 12px;overflow-x:auto}
textarea{display:block;width:100%;resize:none;overflow:hidden;font:inherit;font-size:.94rem;line-height:1.65;color:var(--fg);background:var(--bg);border:1px solid var(--line);border-radius:8px;padding:10px 12px}
textarea:focus{outline:none;border-color:var(--accent)}
textarea.subj{font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-size:.86rem}
button{font:inherit;font-size:.72rem;letter-spacing:.04em;text-transform:uppercase;background:none;border:1px solid var(--line);color:var(--muted);border-radius:6px;padding:2px 9px;cursor:pointer}
button:hover{border-color:var(--accent);color:var(--accent)}
button.done{border-color:var(--accent);color:var(--accent)}
.stale{display:none;background:var(--warn-bg);color:var(--warn-fg);border:1px solid var(--warn-line);border-radius:8px;padding:8px 12px;font-size:.82rem;margin-bottom:14px}
.card.is-stale .stale{display:block}
footer{color:var(--muted);font-size:.82rem;border-top:1px solid var(--line);padding-top:20px;margin-top:44px}
code{font-size:.85em}
"""

JS = r"""
var NS='masonry-outreach:v1:';
function h(s){var x=5381,i;for(i=0;i<s.length;i++){x=((x<<5)+x+s.charCodeAt(i))|0}return String(x)}
function grow(t){t.style.height='auto';t.style.height=t.scrollHeight+'px'}
function flash(b,msg){var o=b.textContent;b.textContent=msg;b.classList.add('done');setTimeout(function(){b.textContent=o;b.classList.remove('done')},1400)}

document.querySelectorAll('textarea[data-field]').forEach(function(t){
  var card=t.closest('.card'), key=NS+card.dataset.handle+':'+t.dataset.field;
  var orig=t.defaultValue, saved=null;
  try{saved=JSON.parse(localStorage.getItem(key))}catch(e){}
  if(saved && saved.text!==orig){
    t.value=saved.text;
    card.classList.add('is-edited');
    if(saved.origHash!==h(orig)) card.classList.add('is-stale');
  }
  grow(t);
  var timer;
  t.addEventListener('input',function(){
    grow(t); clearTimeout(timer);
    timer=setTimeout(function(){
      if(t.value===orig){localStorage.removeItem(key);card.classList.remove('is-edited','is-stale')}
      else{localStorage.setItem(key,JSON.stringify({text:t.value,origHash:h(orig)}));card.classList.add('is-edited')}
    },400);
  });
});

document.addEventListener('click',function(e){
  var b=e.target.closest('button'); if(!b) return;
  var card=b.closest('.card');

  if(b.dataset.reveal!==undefined){var s=b.previousElementSibling;s.textContent=atob(s.dataset.e);b.remove();return}

  if(b.dataset.reset!==undefined){
    card.querySelectorAll('textarea[data-field]').forEach(function(t){
      t.value=t.defaultValue; grow(t); localStorage.removeItem(NS+card.dataset.handle+':'+t.dataset.field);
    });
    card.classList.remove('is-edited','is-stale'); flash(b,'Reset'); return;
  }

  if(b.dataset.link!==undefined){navigator.clipboard.writeText(b.dataset.link).then(function(){flash(b,'Copied')});return}

  var src=document.getElementById(b.dataset.copy); if(!src) return;
  var text=src.dataset.e?atob(src.dataset.e):('value' in src?src.value:src.textContent);
  navigator.clipboard.writeText(text).then(function(){flash(b,'Copied')});
});
"""


def card(c):
    cid = c["handle"].replace(".", "-")
    anchor = f"c-{cid}"
    badge = (
        '<span class="badge sent">Already contacted</span>'
        if c["contacted"]
        else '<span class="badge">Not yet contacted</span>'
    )

    if not c.get("email"):
        return f"""
    <article class="card" id="{anchor}" data-handle="{html.escape(c['handle'])}">
      <div class="top">
        <div class="handle"><a href="{html.escape(c['instagram'])}" target="_blank" rel="noopener noreferrer">@{html.escape(c['handle'])}</a></div>
        <div class="badges"><span class="badge sent">No email</span></div>
      </div>
      <div class="meta">Sheet row {c['row']} &middot; {c['median_views']:,} median Instagram views &middot; keyword &ldquo;{html.escape(c['keyword'])}&rdquo;</div>
      <p class="hook">{html.escape(c['hook'])}</p>
    </article>"""

    b64 = base64.b64encode(c["email"].encode()).decode()
    return f"""
    <article class="card" id="{anchor}" data-handle="{html.escape(c['handle'])}">
      <div class="top">
        <div class="handle"><a href="{html.escape(c['instagram'])}" target="_blank" rel="noopener noreferrer">@{html.escape(c['handle'])}</a></div>
        <div class="badges">
          <span class="badge edited">Edited</span>
          {badge}
        </div>
      </div>
      <div class="meta">Sheet row {c['row']} &middot; {c['median_views']:,} median Instagram views &middot; keyword &ldquo;{html.escape(c['keyword'])}&rdquo;</div>
      <p class="hook">{html.escape(c['hook'])}</p>

      <div class="stale">The original copy for this creator was rewritten after you edited it. Your version is kept.
      Press Reset to discard your edits and take the new copy.</div>

      <div class="field">
        <div class="label">Email <span class="sp"></span>
          <button data-copy="e-{cid}">Copy</button>
          <button data-link="{BASE}#{anchor}">Copy link</button>
        </div>
        <div class="val"><span id="e-{cid}" data-e="{b64}">click reveal &rarr;</span> <button data-reveal>Reveal</button></div>
      </div>

      <div class="field">
        <div class="label">Subject <span class="sp"></span><button data-copy="s-{cid}">Copy</button></div>
        <textarea class="subj" id="s-{cid}" data-field="subject" rows="1" spellcheck="false">{html.escape(c['subject'])}</textarea>
      </div>

      <div class="field">
        <div class="label">Body <span class="sp"></span>
          <button data-copy="b-{cid}">Copy</button>
          <button data-reset>Reset</button>
        </div>
        <textarea id="b-{cid}" data-field="body" rows="12">{html.escape(c['body'])}</textarea>
      </div>
    </article>"""


sent = sum(1 for c in data["creators"] if c["contacted"])
with_email = sum(1 for c in data["creators"] if c.get("email"))
cards = "".join(card(c) for c in data["creators"])

page = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="noindex,nofollow,noarchive">
<meta name="referrer" content="no-referrer">
<title>Masonry creator outreach</title>
<style>{CSS}</style>
</head>
<body>
<div class="wrap">
  <h1>Masonry creator outreach</h1>
  <p class="sub">Personalized email copy for {data['sender']['name']} to send. Generated from the
  Instagram-Masonry-Outreach sheet on {data['generated']}.</p>

  <div class="note">
    <strong>Before you send.</strong> {sent} of these {len(data['creators'])} creators are already marked
    &ldquo;Contacted&rdquo; in column N of the sheet, from an earlier outreach round signed by Gaurav.
    Check the thread history before emailing them again.<br><br>
    <strong>Editing.</strong> Subject and body are editable. Changes save automatically to this browser only,
    so they persist on reload but are not shared with anyone else and are lost if you clear site data.
    Reset restores the original copy.<br><br>
    <strong>Privacy.</strong> Emails sit behind a Reveal button and the page is set to noindex. That deters
    scrapers and search engines. It does not make the page private: anyone with the link can read it.
  </div>
{cards}
  <footer>
    Source of truth is the Instagram-Masonry-Outreach sheet. This page is regenerated from
    <code>creators.json</code>; edit that file and rerun <code>build.py</code> rather than editing the HTML.
    Each creator has a stable anchor, <code>{BASE}#c-&lt;handle&gt;</code>, safe to link from the sheet.
  </footer>
</div>
<script>{JS}</script>
</body>
</html>
"""

# Emails must only ever reach the page base64-encoded. A stray address written into a
# hook or body would be published in the clear, which is the one thing the masking exists
# to prevent. Fail the build rather than ship it.
import re

leaked = {
    m for m in re.findall(r"[\w.+-]+@[\w-]+\.[\w.-]+", page)
    if not m.endswith("masonry.so")
}
if leaked:
    raise SystemExit(f"refusing to write index.html: plaintext email(s) in page: {sorted(leaked)}")

(HERE / "index.html").write_text(page)
print(f"wrote index.html: {len(data['creators'])} creators, {sent} already contacted\n")
print("Deep links for sheet column O:")
for c in data["creators"]:
    print(f"  row {c['row']:>4}  {BASE}#c-{c['handle'].replace('.', '-')}")
