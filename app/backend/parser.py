import csv
import io
import json
import os
import re

CATALOG_PATH = os.path.join(os.path.dirname(__file__), "nsu_catalog.json")

with open(CATALOG_PATH, "r") as f:
    CATALOG = json.load(f)

NSU_COURSES = set(CATALOG["courses"].keys())
GRADE_POINTS = CATALOG.get("grade_points", {})


def detect_file_type(filename: str) -> str:
    ext = filename.lower().rsplit(".", 1)[-1] if "." in filename else ""
    if ext == "csv":
        return "csv"
    elif ext == "pdf":
        return "pdf"
    elif ext in ("png", "jpg", "jpeg", "bmp", "tiff", "gif", "webp"):
        return "image"
    return "unknown"


def parse_csv(file_content: bytes) -> list:
    text = file_content.decode("utf-8", errors="replace")
    reader = csv.DictReader(io.StringIO(text))
    courses = []
    for row in reader:
        try:
            code = ""
            for key in ["course_code", "Course Code", "course", "code", "Course", "courseCode"]:
                if key in row and row[key]:
                    code = str(row[key]).strip()
                    break

            title = ""
            for key in ["course_title", "Course Title", "title", "course_name", "name", "Title"]:
                if key in row and row[key]:
                    title = str(row[key]).strip()
                    break

            credits = 0.0
            for key in ["credits", "Credits", "credit", "cr", "Credit"]:
                if key in row and row[key]:
                    try:
                        credits = float(row[key])
                    except:
                        pass
                    break

            grade = ""
            for key in ["grade", "Grade", "grades", "letter_grade"]:
                if key in row and row[key]:
                    grade = str(row[key]).strip().upper()
                    break

            semester = ""
            for key in ["semester", "Semester", "term", "Term"]:
                if key in row and row[key]:
                    semester = str(row[key]).strip()
                    break

            year = None
            for key in ["year", "Year"]:
                if key in row and row[key]:
                    try:
                        y = int(str(row[key]).strip())
                        if 1990 <= y <= 2035:
                            year = y
                    except:
                        pass
                    break

            attempt = 1
            for key in ["attempt", "Attempt"]:
                if key in row and row[key]:
                    try:
                        attempt = int(row[key])
                    except:
                        pass
                    break

            if code:
                courses.append(make_course(code, title, credits, grade, semester, year, attempt))
        except Exception:
            continue
    return courses


def make_course(code, title="", credits=0.0, grade="", semester="", year=None, attempt=1):
    code = code.strip().upper()
    is_valid = code in NSU_COURSES
    base_code = code[:-1] if code.endswith("L") else code
    if not is_valid:
        is_valid = base_code in NSU_COURSES
    return {
        "course_code": code,
        "course_title": title,
        "credits": credits,
        "grade": grade,
        "semester": semester,
        "year": year,
        "attempt": attempt,
        "is_valid_nsu": 1 if is_valid else 0
    }


def parse_pdf_text(file_content: bytes) -> list:
    try:
        import pdfplumber
        with pdfplumber.open(io.BytesIO(file_content)) as pdf:
            full_text = ""
            tables = []
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    full_text += text + "\n"
                try:
                    page_tables = page.extract_tables()
                    if page_tables:
                        tables.extend(page_tables)
                except:
                    pass

            if tables:
                courses = extract_courses_from_tables(tables)
                if courses:
                    return courses

            return extract_courses_from_text(full_text)
    except Exception as e:
        return []


def parse_image_text(file_content: bytes) -> list:
    try:
        import pytesseract
        from PIL import Image, ImageFilter, ImageEnhance
        img = Image.open(io.BytesIO(file_content))

        img = img.convert('L')
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(2.0)
        enhancer = ImageEnhance.Sharpness(img)
        img = enhancer.enhance(2.0)

        text = pytesseract.image_to_string(img, config='--psm 6')
        return extract_courses_from_text(text)
    except Exception as e:
        return []


def extract_courses_from_tables(tables: list) -> list:
    courses = []
    for table in tables:
        for row in table:
            if not row:
                continue
            row_str = " ".join([str(c) for c in row if c])
            code = find_course_code(row_str)
            if code:
                parts = [str(c).strip() for c in row if c]
                title = ""
                credits = 0.0
                grade = ""
                semester = ""
                year = None

                for p in parts:
                    p_clean = p.strip()
                    if p_clean.upper() == code:
                        continue
                    if re.match(r"^[A-D][+-]?$|^F$|^W$|^I$|^AU$", p_clean, re.IGNORECASE):
                        grade = p_clean.upper()
                    elif re.match(r"^\d+\.?\d*$", p_clean):
                        val = float(p_clean)
                        if 0 < val <= 6 and credits == 0.0:
                            credits = val
                    elif re.match(r"^\d{4}$", p_clean):
                        yr = int(p_clean)
                        if 1990 <= yr <= 2035:
                            year = yr
                    elif p_clean.lower() in ("fall", "spring", "summer", "winter"):
                        semester = p_clean.capitalize()
                    elif len(p_clean) > 2 and not re.match(r"^\d", p_clean) and not title:
                        title = p_clean

                courses.append(make_course(code, title, credits, grade, semester, year))
    return courses


def find_course_code(text: str) -> str:
    match = re.search(r"([A-Z]{2,5}\s*\d{3}L?)", text.upper())
    if match:
        code = match.group(1).replace(" ", "")
        if code in NSU_COURSES:
            return code
        base = code[:-1] if code.endswith("L") else code
        if base in NSU_COURSES:
            return code
    return ""


def extract_courses_from_text(text: str) -> list:
    courses = []
    lines = text.split("\n")

    course_pattern = re.compile(r"([A-Z]{2,5}\s*\d{3}L?)")
    grade_set = set(GRADE_POINTS.keys()) | {"W", "I", "AU"}

    for line in lines:
        line = line.strip()
        if not line or len(line) < 5:
            continue

        match = course_pattern.search(line.upper())
        if not match:
            continue

        raw_code = match.group(1).replace(" ", "")
        code = raw_code

        if code not in NSU_COURSES:
            base = code[:-1] if code.endswith("L") else code
            if base in NSU_COURSES:
                code = base
            else:
                continue

        tokens = re.split(r"[\s,\t;|]+", line)
        tokens = [t.strip() for t in tokens if t.strip()]

        title_parts = []
        credits = 0.0
        grade = ""
        semester = ""
        year = None

        found_code = False
        for token in tokens:
            token_upper = token.upper().replace(" ", "")

            if token_upper == raw_code or token_upper == code:
                found_code = True
                continue

            if not found_code:
                continue

            if token_upper in grade_set or re.match(r"^[A-D][+-]?$", token_upper):
                if not grade:
                    grade = token_upper
            elif re.match(r"^\d+\.?\d*$", token):
                val = float(token)
                if 0 < val <= 6 and credits == 0.0:
                    credits = val
            elif re.match(r"^\d{4}$", token):
                yr = int(token)
                if 1990 <= yr <= 2035:
                    year = yr
            elif token.lower() in ("fall", "spring", "summer", "winter"):
                semester = token.capitalize()
            elif len(token) > 2 and not re.match(r"^\d", token) and token.upper() not in grade_set:
                title_parts.append(token)

        title = " ".join(title_parts)
        if title and title[0].islower():
            title = title[0].upper() + title[1:]

        courses.append(make_course(code, title, credits, grade, semester, year))

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
