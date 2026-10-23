# Build the page at 0trm.dev/data-science-at-camp-nou/ from README.md.
# Run from the repo root: python3 site/build.py  (needs markdown-it-py); it writes _site/.

# %%
import pathlib
import re
import shutil

from markdown_it import MarkdownIt

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

heads = []  # (level, text, id) for every h2 and h3
for i, token in enumerate(tokens):
    if token.type == "heading_open":
        text = "".join(c.content for c in tokens[i + 1].children if c.type in ("text", "code_inline"))
        token.attrSet("id", slug(text))
        if token.tag in ("h2", "h3"):
            heads.append((int(token.tag[1]), text, slug(text)))

# %%
content = md.renderer.render(tokens, md.options, {})
# The README puts each caption in a grey <p> under its image, for GitHub; here the pair is one figure
content = re.sub(
    r"<p>(<img [^>]*>)</p>\n<p [^>]*><em>(.*?)</em></p>",
    r"<figure>\1<figcaption>\2</figcaption></figure>",
    content,
)
# Every h2 has its own rule, so the README's --- between sections would draw a second one
content = re.sub(r"<hr />\n(?=<h2)", "", content)
# Links off the page open in a new tab; the page's own #anchors stay in it
content = content.replace('<a href="http', '<a target="_blank" rel="noopener" href="http')

toc = "\n".join(f'      <li class="l{level}"><a href="#{hid}">{text}</a></li>' for level, text, hid in heads)

# %%
OUT.mkdir(exist_ok=True)
page = (SITE / "template.html").read_text().replace("{{toc}}", toc).replace("{{content}}", content)
(OUT / "index.html").write_text(page)
for name in ASSETS:
    shutil.copy(SITE / name, OUT / name)
shutil.copytree(ROOT / "images", OUT / "images", dirs_exist_ok=True)
print(f"_site/index.html: {len(heads)} headings, {content.count('<figure>')} figures")
