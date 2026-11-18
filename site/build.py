# Build the page at 0trm.dev/data-science-at-camp-nou/ from README.md.
# Run from the repo root: python3 site/build.py  (needs markdown-it-py); it writes _site/.

# %%
import pathlib
import re
import shutil

from markdown_it import MarkdownIt

import chart

ROOT = pathlib.Path(__file__).resolve().parent.parent
SITE = ROOT / "site"
OUT = ROOT / "_site"
ASSETS = ["favicon.ico", "apple-touch-icon.png"]


def slug(text):
    # GitHub's anchor rule, so links to the README's sections work on the page too
    return re.sub(r"[^\w\- ]", "", text.strip().lower()).replace(" ", "-")


# %%
md = MarkdownIt("commonmark").enable("table")
tokens = md.parse((ROOT / "README.md").read_text())

heads = []  # (text, id) for every h2; the h3s are the practical examples, which stay out of the contents
for i, token in enumerate(tokens):
    if token.type == "heading_open":
        text = "".join(c.content for c in tokens[i + 1].children if c.type in ("text", "code_inline"))
        token.attrSet("id", slug(text))
        if token.tag == "h2":
            heads.append((text, slug(text)))

# %%
content = md.renderer.render(tokens, md.options, {})
# The README puts each caption in a grey <p> under its image, for GitHub; here the pair is one figure
content = re.sub(
    r"<p>(<img [^>]*>)</p>\n<p [^>]*><em>(.*?)</em></p>",
    r"<figure>\1<figcaption>\2</figcaption></figure>",
    content,
)
# Fig. 6 is an Excel screenshot in the README; here it is redrawn in the page's colours
content = re.sub(
    r'<img src="images/a-simplified-graph-explaining-the-problem-smartbooking-solves.webp"[^>]*>',
    lambda m: chart.fig6(),
    content,
)
# Each image carries its size, so the text does not jump when it arrives; all but the first wait until scrolled near
SIZES = {
    "an-aerial-view-of-spotify-camp-nou-on-a-match-day.webp": (1200, 415),
    "match-day-at-spotify-camp-nou-from-field-perspective-photo-by-michael-lee.webp": (1200, 601),
    "ux-prototype-of-recommended-areas-predicted-by-the-model.webp": (1200, 715),
    "ticketing-landing-page-for-a-home-match-against-valencia.webp": (1200, 998),
    "a-screenshot-of-the-seient-lliure-app-as-featured-on-the-app-store.webp": (307, 640),
}
content = re.sub(
    r'<img src="images/([^"]+)"',
    lambda m: '<img src="images/%s" width="%d" height="%d"%s'
    % (m.group(1), *SIZES[m.group(1)], "" if m.group(1).startswith("an-aerial") else ' loading="lazy" decoding="async"'),
    content,
)
# The README folds the model details for GitHub; here the table stays open, titled by its summary
content = re.sub(r"<details>\n<summary>(.*?)</summary>\n<table>", r"<table>\n<caption>\1</caption>", content)
content = content.replace("</table>\n</details>", "</table>")
# The code companion note is for readers on GitHub; the page leaves it out
content = re.sub(r"<blockquote>\n<p><strong>Code companion:</strong>.*?</blockquote>\n", "", content, flags=re.S)
# Every h2 has its own rule, so the README's --- between sections would draw a second one
content = re.sub(r"<hr />\n(?=<h2)", "", content)
# Links off the page open in a new tab; the page's own #anchors stay in it
content = content.replace('<a href="http', '<a target="_blank" rel="noopener" href="http')

toc = "\n".join(f'      <li class="l2"><a href="#{hid}">{text}</a></li>' for text, hid in heads)

# %%
OUT.mkdir(exist_ok=True)
page = (SITE / "template.html").read_text().replace("{{toc}}", toc).replace("{{content}}", content)
(OUT / "index.html").write_text(page)
for name in ASSETS:
    shutil.copy(SITE / name, OUT / name)
shutil.copytree(ROOT / "images", OUT / "images", dirs_exist_ok=True)
charts = content.count('<div class="chart">')
print(f"_site/index.html: {len(heads)} sections, {content.count('<figure>')} figures, {charts} redrawn")
