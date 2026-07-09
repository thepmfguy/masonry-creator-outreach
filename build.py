#!/usr/bin/env python3
"""Render creators.json into index.html for GitHub Pages.

Emails are base64-encoded in the markup and revealed on click. That stops
casual scrapers and search indexing, not a determined reader.
"""
import base64
import html
import json
import pathlib

HERE = pathlib.Path(__file__).parent
data = json.loads((HERE / "creators.json").read_text())

CSS = """
:root{--bg:#fbfbfa;--fg:#1c1b1a;--muted:#6f6c68;--line:#e3e1dd;--card:#fff;--accent:#3d5afe;--warn-bg:#fff5e6;--warn-fg:#7a4f00;--warn-line:#f0d9ae}
@media (prefers-color-scheme:dark){:root{--bg:#131312;--fg:#eceae7;--muted:#9a9791;--line:#2e2d2b;--card:#1b1b1a;--accent:#8fa2ff;--warn-bg:#2b2214;--warn-fg:#f0c987;--warn-line:#4a3a1c}}
:root[data-theme=dark]{--bg:#131312;--fg:#eceae7;--muted:#9a9791;--line:#2e2d2b;--card:#1b1b1a;--accent:#8fa2ff;--warn-bg:#2b2214;--warn-fg:#f0c987;--warn-line:#4a3a1c}
:root[data-theme=light]{--bg:#fbfbfa;--fg:#1c1b1a;--muted:#6f6c68;--line:#e3e1dd;--card:#fff;--accent:#3d5afe;--warn-bg:#fff5e6;--warn-fg:#7a4f00;--warn-line:#f0d9ae}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--fg);font:16px/1.6 ui-sans-serif,-apple-system,"Segoe UI",Inter,sans-serif;-webkit-font-smoothing:antialiased}
.wrap{max-width:820px;margin:0 auto;padding:48px 20px 96px}
h1{font-size:1.7rem;letter-spacing:-.02em;margin:0 0 6px}
.sub{color:var(--muted);margin:0 0 28px}
.note{background:var(--warn-bg);color:var(--warn-fg);border:1px solid var(--warn-line);border-radius:10px;padding:12px 16px;margin:0 0 32px;font-size:.9rem}
.card{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:22px;margin:0 0 22px}
.top{display:flex;flex-wrap:wrap;gap:10px;align-items:baseline;justify-content:space-between;margin-bottom:4px}
.handle{font-size:1.15rem;font-weight:650;letter-spacing:-.01em}
.handle a{color:inherit;text-decoration:none;border-bottom:1px solid var(--line)}
.handle a:hover{border-color:var(--accent)}
.badge{font-size:.72rem;text-transform:uppercase;letter-spacing:.07em;padding:3px 9px;border-radius:99px;border:1px solid var(--line);color:var(--muted);white-space:nowrap}
.badge.sent{background:var(--warn-bg);color:var(--warn-fg);border-color:var(--warn-line)}
.meta{color:var(--muted);font-size:.85rem;margin-bottom:14px}
.hook{font-size:.9rem;color:var(--muted);border-left:2px solid var(--line);padding-left:12px;margin:0 0 18px}
.field{margin-bottom:14px}
.label{font-size:.72rem;text-transform:uppercase;letter-spacing:.07em;color:var(--muted);display:flex;align-items:center;gap:10px;margin-bottom:6px}
.val{font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-size:.86rem;background:var(--bg);border:1px solid var(--line);border-radius:8px;padding:10px 12px;overflow-x:auto}
pre.val{white-space:pre-wrap;word-break:break-word;font-family:inherit;font-size:.94rem;line-height:1.65}
button{font:inherit;font-size:.72rem;letter-spacing:.04em;text-transform:uppercase;background:none;border:1px solid var(--line);color:var(--muted);border-radius:6px;padding:2px 9px;cursor:pointer}
button:hover{border-color:var(--accent);color:var(--accent)}
button.done{border-color:var(--accent);color:var(--accent)}
footer{color:var(--muted);font-size:.82rem;border-top:1px solid var(--line);padding-top:20px;margin-top:44px}
"""

JS = """
function copy(t,b){navigator.clipboard.writeText(t).then(function(){var o=b.textContent;b.textContent='Copied';b.classList.add('done');setTimeout(function(){b.textContent=o;b.classList.remove('done')},1400)})}
document.addEventListener('click',function(e){
  var b=e.target.closest('button');if(!b)return;
  if(b.dataset.reveal!==undefined){var s=b.previousElementSibling;s.textContent=atob(s.dataset.e);b.remove();return}
  var src=document.getElementById(b.dataset.copy);
  copy(src.dataset.e?atob(src.dataset.e):src.textContent,b);
});
"""


def card(c):
    b64 = base64.b64encode(c["email"].encode()).decode()
    cid = c["handle"].replace(".", "-")
    badge = (
        '<span class="badge sent">Already contacted</span>'
        if c["contacted"]
        else '<span class="badge">Not yet contacted</span>'
    )
    return f"""
    <article class="card">
      <div class="top">
        <div class="handle"><a href="{html.escape(c['instagram'])}" target="_blank" rel="noopener noreferrer">@{html.escape(c['handle'])}</a></div>
        {badge}
      </div>
      <div class="meta">Sheet row {c['row']} &middot; {c['median_views']:,} median Instagram views &middot; keyword &ldquo;{html.escape(c['keyword'])}&rdquo;</div>
      <p class="hook">{html.escape(c['hook'])}</p>

      <div class="field">
        <div class="label">Email <button data-copy="e-{cid}">Copy</button></div>
        <div class="val"><span id="e-{cid}" data-e="{b64}">click reveal &rarr;</span> <button data-reveal>Reveal</button></div>
      </div>

      <div class="field">
        <div class="label">Subject <button data-copy="s-{cid}">Copy</button></div>
        <div class="val" id="s-{cid}">{html.escape(c['subject'])}</div>
      </div>

      <div class="field">
        <div class="label">Body <button data-copy="b-{cid}">Copy</button></div>
        <pre class="val" id="b-{cid}">{html.escape(c['body'])}</pre>
      </div>
    </article>"""


sent = sum(1 for c in data["creators"] if c["contacted"])
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
    Check the thread history before emailing them again. Emails are hidden behind a Reveal button and the
    page is set to noindex, which deters scrapers but does not make the page private. Anyone with the link can read it.
  </div>
{cards}
  <footer>
    Source of truth is the Instagram-Masonry-Outreach sheet. This page is regenerated from
    <code>creators.json</code>; edit that file and rerun <code>build.py</code> rather than editing the HTML.
  </footer>
</div>
<script>{JS}</script>
</body>
</html>
"""

(HERE / "index.html").write_text(page)
print(f"wrote index.html: {len(data['creators'])} creators, {sent} already contacted")
