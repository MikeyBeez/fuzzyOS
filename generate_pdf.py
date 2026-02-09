#!/usr/bin/env python3
"""Generate paper.pdf from paper.md using weasyprint."""

import markdown
from weasyprint import HTML
from pathlib import Path

ROOT = Path(__file__).parent
MD_FILE = ROOT / "paper.md"
CSS_FILE = ROOT / "pdf-style.css"
PDF_FILE = ROOT / "paper.pdf"

AUTHOR_BLOCK = '<p class="author">Michael Bonsignore — February 2026</p>'

md_text = MD_FILE.read_text()
html_body = markdown.markdown(md_text)

# Insert author line after the subtitle (first </h2>)
parts = html_body.split("</h2>", 1)
if len(parts) >= 2:
    html_body = parts[0] + "</h2>\n" + AUTHOR_BLOCK + parts[1]

css = CSS_FILE.read_text()

html_doc = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>{css}</style>
</head>
<body>
{html_body}
</body>
</html>"""

HTML(string=html_doc).write_pdf(str(PDF_FILE))
print(f"Generated {PDF_FILE}")
