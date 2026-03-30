import csv
import io
import json
import os
import re

CATALOG_PATH = os.path.join(os.path.dirname(__file__), "nsu_catalog.json")

with open(CATALOG_PATH, "r") as f:
    CATALOG = json.load(f)

NSU_COURSES = set(CATALOG["courses"].keys())


def detect_file_type(filename: str) -> str:
    ext = filename.lower().rsplit(".", 1)[-1] if "." in filename else ""
    if ext == "csv":
        return "csv"
    elif ext == "pdf":
        return "pdf"
    elif ext in ("png", "jpg", "jpeg", "bmp", "tiff", "gif"):
        return "image"
    return "unknown"


def parse_csv(file_content: bytes) -> list:
    text = file_content.decode("utf-8", errors="replace")
    reader = csv.DictReader(io.StringIO(text))
    courses = []
    for row in reader:
        try:
            code = str(row.get("course_code", row.get("course", row.get("code", "")))).strip()
            title = str(row.get("course_title", row.get("title", row.get("course_name", "")))).strip()
            credits_str = row.get("credits", row.get("credit", row.get("cr", "0")))
            credits = float(credits_str) if credits_str else 0.0
            grade = str(row.get("grade", row.get("grades", row.get("letter_grade", "")))).strip()
            semester = str(row.get("semester", "")).strip()
            year_str = row.get("year", "")
            year = int(year_str) if year_str and str(year_str).isdigit() else None
            attempt_str = row.get("attempt", "1")
            attempt = int(attempt_str) if attempt_str and str(attempt_str).isdigit() else 1

            if code:
                is_valid = code in NSU_COURSES
                base_code = code[:-1] if code.endswith("L") else code
                if not is_valid:
                    is_valid = base_code in NSU_COURSES

                courses.append({
                    "course_code": code,
                    "course_title": title,
                    "credits": credits,
                    "grade": grade,
                    "semester": semester,
                    "year": year,
                    "attempt": attempt,
                    "is_valid_nsu": 1 if is_valid else 0
                })
        except Exception:
            continue
    return courses


def parse_pdf_text(file_content: bytes) -> list:
    try:
        import pdfplumber
        with pdfplumber.open(io.BytesIO(file_content)) as pdf:
            full_text = ""
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    full_text += text + "\n"
        return extract_courses_from_text(full_text)
    except Exception:
        return []


def parse_image_text(file_content: bytes) -> list:
    try:
        import pytesseract
        from PIL import Image
        img = Image.open(io.BytesIO(file_content))
        text = pytesseract.image_to_string(img)
        return extract_courses_from_text(text)
    except Exception:
        return []


def extract_courses_from_text(text: str) -> list:
    courses = []
    lines = text.split("\n")
    grade_pattern = re.compile(r"^[A-D][+-]?$|^F$|^W$|^I$|^AU$")

    for line in lines:
        line = line.strip()
        if not line:
            continue
        match = re.search(r"([A-Z]{2,5}\d{3}L?)", line)
        if match:
            code = match.group(1)
            parts = re.split(r"\s{2,}|\t|,", line)
            parts = [p.strip() for p in parts if p.strip()]

            title = ""
            credits = 0.0
            grade = ""
            semester = ""
            year = None
            attempt = 1

            for p in parts:
                if p == code:
                    continue
                if grade_pattern.match(p) and not grade:
                    grade = p
                elif re.match(r"^\d+\.?\d*$", p) and credits == 0.0:
                    val = float(p)
                    if 0 <= val <= 6:
                        credits = val
                elif re.match(r"^\d{4}$", p) and year is None:
                    yr = int(p)
                    if 2000 <= yr <= 2030:
                        year = yr
                elif p.lower() in ("fall", "spring", "summer", "winter") and not semester:
                    semester = p
                elif not title and len(p) > 3 and not re.match(r"^\d", p):
                    title = p

            if code:
                is_valid = code in NSU_COURSES
                base_code = code[:-1] if code.endswith("L") else code
                if not is_valid:
                    is_valid = base_code in NSU_COURSES

                courses.append({
                    "course_code": code,
                    "course_title": title,
                    "credits": credits,
                    "grade": grade,
                    "semester": semester,
                    "year": year,
                    "attempt": attempt,
                    "is_valid_nsu": 1 if is_valid else 0
                })
    return courses


def parse_transcript(file_content: bytes, filename: str) -> list:
    file_type = detect_file_type(filename)
    if file_type == "csv":
        return parse_csv(file_content)
    elif file_type == "pdf":
        return parse_pdf_text(file_content)
    elif file_type == "image":
        return parse_image_text(file_content)
    return []
