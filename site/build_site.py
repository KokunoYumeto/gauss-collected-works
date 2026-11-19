"""Build the Gauss site (GitHub Pages, served from docs/) from what is already in this repository: README.md (the
original-language table, the authorship and sources section, kept word for word), the newest English-German release
(its reader PDFs), and site/scans.tsv (the scans the transcription follows). Rerun after every release or README change:
    python -I -B site/build_site.py        (needs the GitHub CLI `gh`, logged in, for the release list)
Writes docs/index.html. No PDF is copied; the page links to the release assets."""
import html, json, pathlib, re, subprocess

ROOT = pathlib.Path(__file__).resolve().parent.parent
REPO = "KokunoYumeto/gauss-collected-works"
readme = (ROOT / "README.md").read_text(encoding="utf-8")


def inline(md):
    """Markdown inline -> HTML: links, bold, italics; the text itself unchanged."""
    s = html.escape(md, quote=False)
    s = re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", lambda m: f'<a href="{m.group(2)}">{m.group(1)}</a>', s)
    s = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"(?<![\w*])\*([^*]+)\*(?![\w*])", r"<em>\1</em>", s)
    s = s.replace('href="docs/', f'href="https://github.com/{REPO}/blob/main/docs/')
    s = re.sub(r'href="((?:original-language|translations)[^"]*)"', rf'href="https://github.com/{REPO}/tree/main/\1"', s)
    return s


def section(title):
    m = re.search(r"^## " + re.escape(title) + r"\n(.*?)(?=^## |\Z)", readme, re.S | re.M)
    return m.group(1).strip() if m else ""


def table_rows(block):
    rows = [l for l in block.splitlines() if l.startswith("|")]
    return [[c.strip() for c in r.strip("|").split("|")] for r in rows[2:]]


orig = table_rows(section("Original-language editions"))
authorship = [p.strip() for p in section("Authorship and sources").split("\n\n") if p.strip()]
intro = readme.split("\n## ")[0].split("\n", 1)[1].strip()

rel = json.loads(subprocess.run(["gh", "release", "list", "-R", REPO, "--limit", "50", "--json", "tagName,publishedAt"],
                                capture_output=True, text=True, encoding="utf-8").stdout)
tag = sorted((r for r in rel if r["tagName"].startswith("gauss-english-german")), key=lambda r: r["publishedAt"])[-1]["tagName"]
assets = json.loads(subprocess.run(["gh", "release", "view", tag, "-R", REPO, "--json", "assets"], capture_output=True,
                                   text=True, encoding="utf-8").stdout)["assets"]
url = {a["name"]: a["url"] for a in assets}
VOLS = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X.1", "X.2", "XI.1", "XI.2", "XII"]


def tr_link(vol, lang):
    v = vol.replace(".", "")
    for n in url:
        if re.fullmatch(rf"Gauss_Werke_{v}_{lang}(_Selection|_Auswahl)?\.pdf", n):
            return f'<a href="{url[n]}">{"English" if lang == "English" else "Deutsch"}</a>'
    return '<span class="none">—</span>'


scans = {}
for line in (ROOT / "site" / "scans.tsv").read_text(encoding="utf-8").splitlines()[1:]:
    v, ppn, pages = line.split("\t")
    scans[v] = (ppn, pages)

rows = []
by_vol = {r[0]: r for r in orig}
for v in VOLS:
    key = {"X.1": "X, part 1", "X.2": "X, part 2", "XI.1": "XI, part 1", "XI.2": "XI, part 2"}.get(v, v)
    r = by_vol.get(key)
    ppn, sp = scans.get(v, ("", ""))
    scan = f'<a href="https://gdz.sub.uni-goettingen.de/id/{ppn}">GDZ {ppn}</a><br><span class="small">{sp} scan pages</span>' if ppn else ""
    if r:
        rows.append(f"<tr><th>{v}</th><td>{inline(r[2])}</td><td>{inline(r[3])}{(' · ' + inline(r[4])) if len(r) > 4 and r[4] else ''}<br><span class='small'>{r[1]} pages</span></td>"
                    f"<td>{tr_link(v, 'English')} · {tr_link(v, 'Deutsch')}</td><td>{scan}</td></tr>")
    else:
        rows.append(f"<tr><th>{v}</th><td><span class='none'>not yet transcribed</span></td><td>—</td><td>—</td><td>{scan}</td></tr>")

coll = " · ".join(f'<a href="{url[n]}">{lab}</a>' for n, lab in (("Gauss_Collected_English.pdf", "English collection"),
                                                                ("Gauss_Werke_Deutsch.pdf", "German collection")) if n in url)
page = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Gauss, Werke: editions and translations</title>
<style>
:root{{--bg:#fdfcf8;--fg:#1f1d1a;--mute:#6b665d;--line:#ddd8cc;--link:#1d4f91}}
@media (prefers-color-scheme:dark){{:root{{--bg:#16150f;--fg:#ece8de;--mute:#a39d90;--line:#3a372f;--link:#8fb6ee}}}}
body{{margin:0;background:var(--bg);color:var(--fg);font:16px/1.55 Georgia,"Times New Roman",serif}}
main{{max-width:980px;margin:0 auto;padding:24px 16px 48px}}
h1{{font-size:1.7rem;margin:.2em 0}} h2{{font-size:1.2rem;margin-top:2em;border-bottom:1px solid var(--line)}}
a{{color:var(--link)}} .small{{font-size:.85em;color:var(--mute)}} .none{{color:var(--mute)}}
.wrap{{overflow-x:auto}} table{{border-collapse:collapse;width:100%;font-size:.92rem}}
th,td{{border-bottom:1px solid var(--line);padding:8px 6px;vertical-align:top;text-align:left}}
thead th{{font-size:.85rem;color:var(--mute)}}
@media (max-width:640px){{thead{{display:none}} table,tbody,tr,td,th{{display:block;width:auto}}
 tr{{border:1px solid var(--line);border-radius:6px;margin:0 0 12px;padding:6px 8px}} td,th{{border:0;padding:4px 0}}
 td:nth-of-type(1):before{{content:"Coverage: ";color:var(--mute)}} td:nth-of-type(2):before{{content:"Original: ";color:var(--mute)}}
 td:nth-of-type(3):before{{content:"Translations: ";color:var(--mute)}} td:nth-of-type(4):before{{content:"Scan: ";color:var(--mute)}}}}
</style></head><body><main>
<h1>Carl Friedrich Gauss, <em>Werke</em></h1>
<p>{inline(intro.splitlines()[0])}</p>
<p><strong>Read in translation:</strong> {coll}</p>
<h2>Volumes</h2>
<p class="small">Original language: the reader PDF and the editable LaTeX of each volume. Translations: the English and
modern German readers of release <a href="https://github.com/{REPO}/releases/tag/{tag}">{tag}</a>. Scan: the
Göttingen State and University Library (GDZ) digitization of the volume.</p>
<div class="wrap"><table><thead><tr><th>Vol.</th><th>Coverage</th><th>Original language</th><th>Translations</th><th>Scan</th></tr></thead>
<tbody>
{chr(10).join(rows)}
</tbody></table></div>
<h2>Sources and editions</h2>
<p>All sources are in the repository: <a href="https://github.com/{REPO}/tree/main/original-language">original-language
sources</a>, <a href="https://github.com/{REPO}/tree/main/translations">English and German sources</a>, and the
<a href="https://github.com/{REPO}/blob/main/docs/english-german.md">translation guide</a>. All releases:
<a href="https://github.com/{REPO}/releases">github.com/{REPO}/releases</a>.</p>
<h2>Authorship and sources</h2>
{chr(10).join(f"<p>{inline(p)}</p>" for p in authorship)}
<p class="small">This page is generated by <code>site/build_site.py</code> from the repository's README and releases.</p>
</main></body></html>
"""
(ROOT / "docs").mkdir(exist_ok=True)
(ROOT / "docs" / "index.html").write_text(page, encoding="utf-8")
print("docs/index.html", len(page), "bytes;", len(rows), "volumes; release", tag)
