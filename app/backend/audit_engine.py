import json
import os
from collections import defaultdict
from datetime import datetime

CATALOG_PATH = os.path.join(os.path.dirname(__file__), "nsu_catalog.json")

with open(CATALOG_PATH, "r") as f:
    CATALOG = json.load(f)

NSU_COURSES = set(CATALOG["courses"].keys())
GRADE_POINTS = CATALOG["grade_points"]
PROGRAMS = CATALOG["programs"]


def get_grade_points(grade):
    if not grade:
        return None
    grade = grade.strip().upper()
    if grade in ("", "W", "I", "AU"):
        return None
    if grade in GRADE_POINTS:
        return GRADE_POINTS[grade]
    return None


def detect_program(courses):
    code_set = set(c["course_code"] for c in courses)
    scores = {}
    for prog_key, prog_data in PROGRAMS.items():
        score = 0
        all_prog_codes = set()
        for cat_data in prog_data.get("categories", {}).values():
            if isinstance(cat_data, dict):
                for k, v in cat_data.items():
                    if isinstance(v, list) and k != "electives":
                        all_prog_codes.update(v)
        score = len(code_set & all_prog_codes)
        scores[prog_key] = score

    if not scores or max(scores.values()) == 0:
        return "CSE"

    best = max(scores, key=scores.get)
    return best


def detect_major(courses, program):
    if program != "BBA":
        return None
    code_set = set(c["course_code"] for c in courses)
    bba = PROGRAMS.get("BBA", {})
    major_cat = bba.get("categories", {}).get("Major Concentration", {})
    major_scores = {}
    for major_name, major_codes in major_cat.items():
        if isinstance(major_codes, list):
            major_scores[major_name] = len(code_set & set(major_codes))
    if major_scores and max(major_scores.values()) > 0:
        return max(major_scores, key=major_scores.get)
    return None


def process_retakes(courses):
    courses_by_code = defaultdict(list)
    for c in courses:
        code = c["course_code"]
        base = code[:-1] if code.endswith("L") else code
        courses_by_code[base].append(c)

    best_courses = {}
    retake_history = defaultdict(list)

    for base, attempts in courses_by_code.items():
        valid = [a for a in attempts if get_grade_points(a.get("grade")) is not None]
        if valid:
            best = max(valid, key=lambda x: (get_grade_points(x["grade"]) or 0, -x.get("attempt", 1)))
            best_courses[base] = best
            if len(valid) > 1:
                retake_history[base] = sorted(valid, key=lambda x: x.get("attempt", 1))
        else:
            best_courses[base] = attempts[0]

    return best_courses, retake_history


def calculate_cgpa(best_courses):
    total_qp = 0.0
    total_cr = 0.0
    failed = 0.0
    withdrawn = 0.0
    incomplete = 0.0

    for code, c in best_courses.items():
        grade = c.get("grade", "").strip().upper()
        credits = c.get("credits", 0.0)
        gp = get_grade_points(grade)

        if grade == "F":
            failed += credits
            total_qp += 0.0 * credits
            total_cr += credits
        elif grade == "W":
            withdrawn += credits
        elif grade == "I":
            incomplete += credits
        elif gp is not None:
            total_qp += gp * credits
            total_cr += credits

    cgpa = total_qp / total_cr if total_cr > 0 else 0.0
    standing = "GOOD STANDING" if cgpa >= 2.0 else "PROBATION"

    return {
        "cgpa": round(cgpa, 2),
        "total_quality_points": round(total_qp, 2),
        "credits_attempted": round(total_cr, 1),
        "credits_earned": round(total_cr - failed, 1),
        "failed_credits": round(failed, 1),
        "withdrawn_credits": round(withdrawn, 1),
        "incomplete_credits": round(incomplete, 1),
        "academic_standing": standing
    }


def check_requirements(best_courses, program_name):
    prog = PROGRAMS.get(program_name, PROGRAMS.get("CSE"))
    categories = prog.get("categories", {})
    all_required = set()
    category_progress = {}
    missing_courses = []

    for cat_name, cat_data in categories.items():
        if not isinstance(cat_data, dict):
            continue
        required = set(cat_data.get("courses", []))
        elective_codes = cat_data.get("electives", [])
        if isinstance(elective_codes, list):
            required.update(elective_codes)
        all_required.update(required)

        cat_credits = 0.0
        completed_in_cat = []
        for req_code in required:
            if req_code in best_courses:
                course = best_courses[req_code]
                grade = course.get("grade", "").strip().upper()
                gp = get_grade_points(grade)
                if gp is not None and gp > 0:
                    cat_credits += course.get("credits", 0.0)
                    completed_in_cat.append(req_code)
                else:
                    missing_courses.append(req_code)
            else:
                missing_courses.append(req_code)

        cat_total = cat_data.get("credits", 0)
        category_progress[cat_name] = {
            "completed": round(cat_credits, 1),
            "required": cat_total,
            "percent": round(cat_credits / cat_total * 100, 1) if cat_total > 0 else 0,
            "courses_completed": completed_in_cat
        }

    total_completed = 0.0
    for code, c in best_courses.items():
        grade = c.get("grade", "").strip().upper()
        gp = get_grade_points(grade)
        if gp is not None and gp > 0:
            total_completed += c.get("credits", 0.0)

    return category_progress, missing_courses, total_completed


def run_audit(courses, level=3):
    program = detect_program(courses)
    major = detect_major(courses, program) if level >= 3 else None
    best_courses, retake_history = process_retakes(courses)
    cgpa_data = calculate_cgpa(best_courses)

    prog = PROGRAMS.get(program, PROGRAMS.get("CSE"))
    total_required = prog.get("total_credits", 130)

    category_progress = {}
    missing_courses = []
    total_completed = 0.0

    if level >= 2:
        category_progress, missing_courses, total_completed = check_requirements(best_courses, program)
    else:
        for code, c in best_courses.items():
            grade = c.get("grade", "").strip().upper()
            gp = get_grade_points(grade)
            if gp is not None and gp > 0:
                total_completed += c.get("credits", 0.0)

    credits_remaining = max(0, total_required - total_completed)
    progress_percent = round(total_completed / total_required * 100, 1) if total_required > 0 else 0
    estimated_semesters = max(1, int(credits_remaining / 15)) if credits_remaining > 0 else 0

    invalid_courses = [c for c in courses if c.get("is_valid_nsu") == 0]

    waiver_status = {}
    waiver_courses = prog.get("waivers", {})
    for wc, wcr in waiver_courses.items():
        if wc in best_courses:
            grade = best_courses[wc].get("grade", "").strip().upper()
            gp = get_grade_points(grade)
            if gp is not None and gp > 0:
                waiver_status[wc] = "COMPLETED"
            else:
                waiver_status[wc] = "NEEDS WAIVER"
        else:
            waiver_status[wc] = "NOT IN TRANSCRIPT"

    return {
        "cgpa": cgpa_data["cgpa"],
        "total_quality_points": cgpa_data["total_quality_points"],
        "credits_attempted": cgpa_data["credits_attempted"],
        "credits_earned": cgpa_data["credits_earned"],
        "failed_credits": cgpa_data["failed_credits"],
        "withdrawn_credits": cgpa_data["withdrawn_credits"],
        "incomplete_credits": cgpa_data["incomplete_credits"],
        "academic_standing": cgpa_data["academic_standing"],
        "program": program,
        "major": major,
        "total_required": total_required,
        "credits_remaining": round(credits_remaining, 1),
        "progress_percent": progress_percent,
        "estimated_semesters": estimated_semesters,
        "waiver_status": waiver_status,
        "missing_courses": missing_courses[:20],
        "category_progress": category_progress,
        "invalid_courses": invalid_courses,
        "retake_history": {k: [{"grade": r.get("grade"), "semester": r.get("semester"), "attempt": r.get("attempt")} for r in v] for k, v in retake_history.items()},
        "level_used": level
    }
