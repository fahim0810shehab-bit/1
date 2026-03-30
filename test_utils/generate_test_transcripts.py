#!/usr/bin/env python3
"""
Utility to generate sample transcripts in PDF and image formats for testing
the multi-platform app (web/mobile/CLI).
This script focuses on Level 1 data (L1) but can be extended for L2/L3.
"""
from datetime import datetime
import os
import sys

try:
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas
except ImportError:
    print("ReportLab not installed. PDF generation will fail.")
    letter = (612, 792)  # default 8.5x11 in points
    canvas = None

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    Image = None
    ImageDraw = None
    ImageFont = None

ROOT = os.path.join(os.path.dirname(__file__), '..', 'test_outputs')
os.makedirs(ROOT, exist_ok=True)

SAMPLE_COURSES = [
    {"code":"CSE115","title":"Programming I","credits":3,"grade":"A","term":"Fall","year":2023},
    {"code":"CSE115L","title":"Programming I Lab","credits":1,"grade":"A-","term":"Fall","year":2023},
    {"code":"MAT116","title":"Pre-Calculus","credits":3,"grade":"B+","term":"Fall","year":2023},
    {"code":"ENG102","title":"Introduction to Composition","credits":3,"grade":"B","term":"Fall","year":2023}
]

def make_pdf(path, courses=None):
    if canvas is None:
        raise SystemExit("ReportLab is not installed. Cannot generate PDF.")
    if courses is None:
        courses = SAMPLE_COURSES
    c = canvas.Canvas(path, pagesize=letter)
    width, height = letter
    y = height - 60
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y, "NSU Transcript - Sample (L1 Data)")
    c.setFont("Helvetica", 10)
    y -= 22
    c.drawString(50, y, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    y -= 28
    c.setFont("Helvetica-Bold", 11)
    c.drawString(50, y, "Course | Title | Credits | Grade | Term-Year")
    y -= 14
    c.setFont("Helvetica", 11)
    for cc in courses:
        line = f"{cc['code']} | {cc['title']} | {cc['credits']} | {cc['grade']} | {cc['term']} {cc['year']}"
        c.drawString(50, y, line)
        y -= 14
        if y < 60:
            c.showPage()
            y = height - 60
    c.save()

def make_image(path, courses=None):
    if Image is None:
        raise SystemExit("Pillow is not installed. Cannot generate image.")
    if courses is None:
        courses = SAMPLE_COURSES
    W, H = 800, 480
    img = Image.new('RGB', (W, H), color=(255, 255, 255))
    d = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("arial.ttf", 14)
    except Exception:
        font = ImageFont.load_default()
    y = 40
    d.text((40, y), "NSU Transcript - Sample (L1 Data)", fill=(0,0,0), font=font)
    y += 26
    d.text((40, y), f"Generated: {datetime.now().strftime('%Y-%m-%d')}", fill=(0,0,0), font=font)
    y += 40
    header = "Code | Title | Credits | Grade | Term-Year"
    d.text((40, y), header, fill=(0,0,0), font=font)
    y += 20
    for cc in courses:
        line = f"{cc['code']} | {cc['title']} | {cc['credits']} | {cc['grade']} | {cc['term']} {cc['year']}"
        d.text((40, y), line, fill=(0,0,0), font=font)
        y += 18
        if y > H-40:
            break
    img.save(path)

def main():
    # simple CLI: --out_pdf, --out_img
    out_pdf = os.path.join(ROOT, 'transcript_L1_sample.pdf')
    out_img = os.path.join(ROOT, 'transcript_L1_sample.png')
    make_pdf(out_pdf, SAMPLE_COURSES)
    make_image(out_img, SAMPLE_COURSES)
    print(f"Generated {out_pdf} and {out_img}")

if __name__ == '__main__':
    main()
