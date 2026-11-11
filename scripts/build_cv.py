from pathlib import Path
import re

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    Image,
    KeepTogether,
    PageTemplate,
    Paragraph,
    PageBreak,
    SimpleDocTemplate,
    Spacer,
)

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "README.md"
OUTPUT = ROOT / "Evgeny_Gamza_CV.pdf"
PHOTO = ROOT / "assets" / "cv-profile.jpg"


def inline_markup(text):
    text = re.sub(r"\[([^]]+)\]\(([^)]+)\)", r'<link href="\2" color="#2367a5">\1</link>', text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"`([^`]+)`", r"<font name='Courier'>\1</font>", text)
    return text


def build():
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="Name", parent=styles["Title"], fontName="Helvetica-Bold", fontSize=21, leading=25, alignment=0, textColor=colors.HexColor("#172b4d"), spaceAfter=3))
    styles.add(ParagraphStyle(name="Headline", parent=styles["Normal"], fontSize=12, leading=15, alignment=0, textColor=colors.HexColor("#2367a5"), spaceAfter=5))
    styles.add(ParagraphStyle(name="Contact", parent=styles["Normal"], fontSize=8.5, leading=11, alignment=0, textColor=colors.HexColor("#49566a"), spaceAfter=12))
    styles.add(ParagraphStyle(name="Section", parent=styles["Heading2"], fontName="Helvetica-Bold", fontSize=12, leading=15, textColor=colors.HexColor("#2367a5"), spaceBefore=9, spaceAfter=4, keepWithNext=True))
    styles.add(ParagraphStyle(name="Role", parent=styles["Heading3"], fontName="Helvetica-Bold", fontSize=10, leading=12, textColor=colors.HexColor("#172b4d"), spaceBefore=5, spaceAfter=2, keepWithNext=True))
    styles.add(ParagraphStyle(name="BodyCV", parent=styles["BodyText"], fontName="Helvetica", fontSize=8.6, leading=11.4, textColor=colors.HexColor("#222b38"), spaceAfter=3))
    styles.add(ParagraphStyle(name="BulletCV", parent=styles["BodyCV"], leftIndent=11, firstLineIndent=-7, bulletIndent=0, spaceAfter=2))
    styles.add(ParagraphStyle(name="Small", parent=styles["BodyText"], fontSize=8, leading=10, textColor=colors.HexColor("#49566a"), spaceAfter=4))

    doc = SimpleDocTemplate(str(OUTPUT), pagesize=A4, rightMargin=17*mm, leftMargin=17*mm, topMargin=13*mm, bottomMargin=14*mm, title="Evgeny Gamza - AQA | SDET", author="Evgeny Gamza")
    story = []
    lines = SOURCE.read_text(encoding="utf-8").splitlines()
    in_header = True
    for line in lines:
        raw = line.strip()
        if not raw or raw == "<br clear=\"all\">":
            continue
        if raw.startswith("<img "):
            continue
        if raw.startswith("!["):
            if PHOTO.exists():
                photo = Image(str(PHOTO), width=27*mm, height=27*mm)
                photo.hAlign = "LEFT"
                story.append(photo)
                story.append(Spacer(1, 2*mm))
            continue
        if raw.startswith("# "):
            name = raw[2:].strip()
            story.append(Paragraph(inline_markup(name), styles["Name"]))
            continue
        if raw.startswith("**") and raw.endswith("**") and in_header:
            story.append(Paragraph(inline_markup(raw[2:-2]), styles["Headline"]))
            continue
        if raw.startswith("## "):
            in_header = False
            story.append(Paragraph(inline_markup(raw[3:]), styles["Section"]))
            continue
        if raw.startswith("### Ozon Tech"):
            story.append(PageBreak())
        if raw.startswith("### "):
            story.append(Paragraph(inline_markup(raw[4:]), styles["Role"]))
            continue
        if raw.startswith("- "):
            story.append(Paragraph("• " + inline_markup(raw[2:]), styles["BulletCV"]))
            continue
        if raw.startswith("["):
            story.append(Paragraph(inline_markup(raw), styles["Contact" if in_header else "Small"]))
            continue
        if in_header:
            story.append(Paragraph(inline_markup(raw), styles["Contact"]))
        else:
            story.append(Paragraph(inline_markup(raw), styles["BodyCV"]))

    def footer(canvas, document):
        canvas.saveState()
        canvas.setStrokeColor(colors.HexColor("#d9e0e9"))
        canvas.line(17*mm, 10*mm, A4[0]-17*mm, 10*mm)
        canvas.setFont("Helvetica", 7.5)
        canvas.setFillColor(colors.HexColor("#687386"))
        canvas.drawRightString(A4[0]-17*mm, 6*mm, f"{document.page}")
        canvas.restoreState()

    doc.build(story, onFirstPage=footer, onLaterPages=footer)


if __name__ == "__main__":
    build()
