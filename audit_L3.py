#!/usr/bin/env python3
"""
Level 3: Audit & Deficiency Reporter
CSE226.1 Project - Audit Core

Comprehensive graduation audit with:
- Best grade calculation for retakes
- Detailed deficiency reporting
- Major/concentration detection
- Full program requirement checking

Usage:
    python audit_L3.py <transcript_file> <program_name> <program_knowledge.md>
    
Example:
    python audit_L3.py transcript.csv CSE program_knowledge.md
    python audit_L3.py test_L3.csv BBA program_knowledge.md
"""

import csv
import sys
import re
from pathlib import Path
from collections import defaultdict


# NSU Course Catalog - Complete list of all valid NSU courses
NSU_COURSES = {
    # Accounting (ACT)
    'ACT201', 'ACT202', 'ACT310', 'ACT320', 'ACT360', 'ACT370', 'ACT380', 'ACT410', 'ACT430',
    
    # Applied Mathematics & Computer Science (AMCS)
    'AMCS502', 'AMCS504', 'AMCS505',
    
    # Anthropology (ANT)
    'ANT101',
    
    # Architecture (ARC)
    'ARC111', 'ARC112', 'ARC121', 'ARC122', 'ARC123', 'ARC131', 'ARC133', 'ARC200',
    'ARC213', 'ARC214', 'ARC215', 'ARC241', 'ARC242', 'ARC251', 'ARC261', 'ARC262',
    'ARC263', 'ARC264', 'ARC271', 'ARC272', 'ARC273', 'ARC281', 'ARC282', 'ARC283',
    'ARC293', 'ARC310', 'ARC316', 'ARC317', 'ARC318', 'ARC324', 'ARC334', 'ARC343',
    'ARC344', 'ARC384', 'ARC410', 'ARC419', 'ARC437', 'ARC438', 'ARC445', 'ARC453',
    'ARC455', 'ARC474', 'ARC492', 'ARC510', 'ARC576', 'ARC598',
    
    # Biochemistry and Biotechnology (BBT)
    'BBT203', 'BBT221', 'BBT230', 'BBT312', 'BBT312L', 'BBT314', 'BBT314L', 'BBT315',
    'BBT316', 'BBT316L', 'BBT317', 'BBT318', 'BBT335', 'BBT413', 'BBT413L', 'BBT415',
    'BBT415L', 'BBT416', 'BBT417', 'BBT419', 'BBT421', 'BBT423', 'BBT424', 'BBT425',
    'BBT427', 'BBT601', 'BBT608', 'BBT609', 'BBT615', 'BBT616', 'BBT622', 'BBT623',
    'BBT631', 'BBT638', 'BBT639', 'BBT654', 'BBT671', 'BBT685',
    
    # Languages (BEN, CHN, ENG)
    'BEN205', 'CHN101', 'CHN201', 'ENG101', 'ENG102', 'ENG103', 'ENG466', 'ENG481', 'ENG501',
    'ENG511', 'ENG522', 'ENG525', 'ENG552', 'ENG555', 'ENG557', 'ENG570', 'ENG573',
    'ENG574', 'ENG576', 'ENG581', 'ENG602', 'ENG111', 'ENG105',
    
    # Biology (BIO)
    'BIO103', 'BIO103L', 'BIO201', 'BIO201L', 'BIO202', 'BIO202L',
    
    # Basic Sciences (BSC, CHE)
    'BSC201', 'CHE101', 'CHE101L', 'CHE201', 'CHE202', 'CHE202L', 'CHE203', 'CHE203L',
    
    # Mathematics (MAT)
    'MAT116',
    
    # Statistics (STA)
    'STA101', 'STA102',
    
    # Business & Management (BUS)
    'BUS112', 'BUS135', 'BUS172', 'BUS173', 'BUS251', 'BUS498', 'BUS500', 'BUS501', 'BUS505',
    'BUS511', 'BUS516', 'BUS518', 'BUS520', 'BUS525', 'BUS530', 'BUS535', 'BUS601',
    'BUS620', 'BUS635', 'BUS650', 'BUS685', 'BUS690', 'BUS700',
    
    # Executive MBA (EMB)
    'EMB500', 'EMB501', 'EMB502', 'EMB510', 'EMB520', 'EMB601', 'EMB602', 'EMB620',
    'EMB650', 'EMB660', 'EMB670', 'EMB690',
    
    # Finance (FIN)
    'FIN254', 'FIN440', 'FIN444', 'FIN455', 'FIN464',
    
    # Human Resource Management (HRM)
    'HRM603', 'HRM604', 'HRM610', 'HRM631', 'HRM660',
    
    # International Business (INB)
    'INB350', 'INB372', 'INB400', 'INB410', 'INB480', 'INB490',
    
    # Civil and Environmental Engineering (CEE)
    'CEE100', 'CEE110', 'CEE209', 'CEE210', 'CEE211', 'CEE211L', 'CEE212', 'CEE212L',
    'CEE213', 'CEE214', 'CEE214L', 'CEE215', 'CEE240', 'CEE240L', 'CEE250', 'CEE250L',
    'CEE260', 'CEE271L', 'CEE310', 'CEE330', 'CEE331', 'CEE335', 'CEE340', 'CEE350',
    'CEE360', 'CEE360L', 'CEE370', 'CEE371L', 'CEE373', 'CEE373L', 'CEE415', 'CEE430',
    'CEE431', 'CEE435', 'CEE460', 'CEE470', 'CEE475',
    
    # Computer Science and Engineering (CSE)
    'CSE115', 'CSE115L', 'CSE173', 'CSE215', 'CSE215L', 'CSE225', 'CSE225L', 'CSE231',
    'CSE231L', 'CSE273', 'CSE299', 'CSE311', 'CSE311L', 'CSE323', 'CSE325', 'CSE327',
    'CSE331', 'CSE331L', 'CSE332', 'CSE332L', 'CSE338', 'CSE338L', 'CSE373', 'CSE411',
    'CSE413', 'CSE413L', 'CSE425', 'CSE435', 'CSE435L', 'CSE438', 'CSE438L', 'CSE440',
    'CSE445', 'CSE465', 'CSE482', 'CSE482L', 'CSE491', 'CSE495A', 'CSE495B', 'CSE499A',
    'CSE499B', 'CSE562', 'CSE564',
    
    # Development Studies (DEV)
    'DEV564', 'DEV565', 'DEV569',
    
    # Economics (ECO)
    'ECO101', 'ECO103', 'ECO104', 'ECO135', 'ECO172', 'ECO173', 'ECO201', 'ECO202', 'ECO204',
    'ECO245', 'ECO301', 'ECO302', 'ECO304', 'ECO317', 'ECO328', 'ECO348', 'ECO354', 'ECO372',
    'ECO380', 'ECO406', 'ECO414', 'ECO415', 'ECO472', 'ECO490', 'ECO501', 'ECO504',
    'ECO511', 'ECO613', 'ECO650', 'ECO682', 'ECO687',
    
    # Electrical and Electronic Engineering (EEE)
    'EEE111', 'EEE111L', 'EEE141', 'EEE141L', 'EEE154', 'EEE211', 'EEE211L', 'EEE221', 'EEE221L', 'EEE241',
    'EEE241L', 'EEE299', 'EEE311', 'EEE311L', 'EEE312', 'EEE312L', 'EEE321', 'EEE321L',
    'EEE331', 'EEE331L', 'EEE336L', 'EEE342', 'EEE342L', 'EEE361', 'EEE362', 'EEE362L',
    'EEE453L', 'EEE461', 'EEE462', 'EEE464', 'EEE465', 'EEE494', 'EEE499A', 'EEE499B',
    'EEE551',
    
    # Environmental Science & Management (ENV)
    'ENV203', 'ENV204', 'ENV205', 'ENV207', 'ENV209', 'ENV214', 'ENV215', 'ENV260',
    'ENV311', 'ENV315', 'ENV316', 'ENV373', 'ENV405', 'ENV409', 'ENV421', 'ENV436',
    'ENV455', 'ENV501', 'ENV502', 'ENV602', 'ENV606', 'ENV609', 'ENV627', 'ENV632',
    'ENV635', 'ENV649', 'ENV652',
    
    # Electronics and Telecommunication Engineering (ETE)
    'ETE111', 'ETE211L', 'ETE221', 'ETE241', 'ETE241L', 'ETE299', 'ETE311', 'ETE311L',
    'ETE312', 'ETE312L', 'ETE321', 'ETE321L', 'ETE331', 'ETE331L', 'ETE332', 'ETE332L',
    'ETE333', 'ETE334', 'ETE334L', 'ETE335', 'ETE335L', 'ETE499B',
    
    # Public Policy and Public Health (EMPG, EMPH)
    'EMPG500', 'EMPG510', 'EMPG530', 'EMPG555', 'EMPG570', 'EMPH601', 'EMPH609', 'EMPH611',
    'EMPH631', 'EMPH642', 'EMPH644', 'EMPH653', 'EMPH663', 'EMPH671', 'EMPH672', 'EMPH678',
    'EMPH681', 'EMPH704', 'EMPH706', 'EMPH711', 'EMPH712', 'EMPH713', 'EMPH742', 'EMPH745',
    'EMPH771', 'EMPH781', 'EMPH842',
    
    # Law (LAW)
    'LAW101', 'LAW200',
    
    # Other Disciplines (ETH, LBA)
    'ETH201', 'LBA104',
    
    # CSE Additional courses from original list
    'CSE199', 'CSE399', 'CSE422', 'CSE423', 'CSE427', 'CSE428', 'CSE450', 'CSE455',
    'CSE460', 'CSE498R',
    
    # Mathematics additional
    'MAT112', 'MAT120', 'MAT130', 'MAT250', 'MAT260', 'MAT350', 'MAT361', 'MAT370',
    
    # Physics
    'PHY107', 'PHY107L', 'PHY108', 'PHY108L', 'PHY201',
    
    # BBA Core
    'MIS107', 'MIS207', 'MGT212', 'MGT351', 'MGT314', 'MGT368', 'MGT489', 'MKT202',
    
    # BBA Majors
    'MKT337', 'MKT344', 'MKT460', 'MKT470',
    'FIN433', 'FIN435',
    'MIS210', 'MIS310', 'MIS320', 'MIS470',
    'HRM340', 'HRM360', 'HRM380', 'HRM450',
    'SCM310', 'SCM320', 'SCM450', 'MGT460',
    
    # Additional courses
    'SC0101', 'PHI101', 'PHI104', 'HIS102', 'HIS103', 'SOC101', 'GEO205', 'POL101',
}


def validate_nsu_course(course_code):
    """
    Check if a course is a valid NSU course.
    Returns: (is_valid, course_type)
    """
    # First check exact match (handles CSE498R, CSE499A, CSE499B, etc.)
    if course_code in NSU_COURSES:
        return True, "NSU Course"
    
    # Try removing 'L' suffix for lab courses (CSE115L -> CSE115)
    base_code = course_code[:-1] if course_code.endswith('L') else course_code
    if base_code in NSU_COURSES:
        return True, "NSU Course"
    
    return False, "Unknown/External"


def get_field_value(row, possible_names, default=None):
    """Get value from row using multiple possible column names."""
    result = default
    for name in possible_names:
        if name in row and row[name]:
            result = row[name]
            break
        for key in row.keys():
            if key.lower() == name.lower() and row[key]:
                result = row[key]
                break
        if result != default:
            break
    return result if result is not None else ''


# Define possible column name variations
COLUMN_MAPPINGS = {
    'course_code': ['course_code', 'course', 'code', 'course_id', 'courseCode'],
    'course_title': ['course_title', 'title', 'course_name', 'name'],
    'credits': ['credits', 'credit', 'cr', 'credit_hours'],
    'grade': ['grade', 'grades', 'letter_grade'],
    'semester': ['semester', 'term', 'session'],
    'year': ['year', 'yr'],
    'attempt': ['attempt', 'try', 'retake']
}


def get_grade_points(grade):
    """Convert letter grade to grade points."""
    if not grade or grade.strip() == '':
        return None
    
    grade = grade.strip().upper()
    
    grade_points = {
        'A': 4.0, 'A-': 3.7,
        'B+': 3.3, 'B': 3.0, 'B-': 2.7,
        'C+': 2.3, 'C': 2.0, 'C-': 1.7,
        'D+': 1.3, 'D': 1.0,
        'F': 0.0
    }
    
    excluded_grades = {'W', 'I', 'AU'}
    
    if grade in excluded_grades:
        return None
    elif grade in grade_points:
        return grade_points[grade]
    else:
        return None


def ask_waiver_status(course_code):
    """Interactively ask admin about waiver status for a course."""
    waiver_info = {
        'ENG102': 'SAT/IELTS scores or high admission test performance',
        'BUS112': 'SAT 1150+ or high admission test scores',
        'MAT112': 'Entry test (for Economics students)',
        'MAT116': 'Entry test (for CSE/Engineering students)'
    }
    
    reason = waiver_info.get(course_code, 'University policy')
    print(f"\nCourse: {course_code}")
    print(f"Waiver criteria: {reason}")
    
    while True:
        response = input(f"Has waiver been granted for {course_code}? (yes/no): ").strip().lower()
        if response in ['yes', 'y']:
            return True
        elif response in ['no', 'n']:
            return False
        else:
            print("Please enter 'yes' or 'no'")


def get_program_requirements():
    """Define program requirements."""
    return {
        'CSE': {
            'total': 130,
            'waivers': {'ENG102': 3, 'MAT116': 3},
            'categories': {
                'University Core': {
                    'credits': 34,
                    'courses': ['ENG102', 'ENG103', 'ENG111', 'BEN205', 'PHI104', 'HIS102', 'HIS103', 'SC0101', 'POL101', 'BIO103'],
                    'electives': ['SOC101', 'ANT101', 'ENV203', 'GEO205']
                },
                'SEPS Core': {
                    'credits': 38,
                    'courses': ['MAT116', 'MAT120', 'MAT130', 'MAT250', 'MAT350', 'MAT361', 'PHY107', 'PHY107L', 'PHY108', 'PHY108L', 'CHE101', 'CHE101L', 'CSE115', 'CSE115L', 'CEE110']
                },
                'CSE Major Core': {
                    'credits': 42,
                    'courses': ['CSE173', 'CSE215', 'CSE215L', 'CSE225', 'CSE225L', 'CSE231', 'CSE231L', 'CSE311', 'CSE311L', 'CSE323', 'CSE327', 'CSE331', 'CSE331L', 'CSE332', 'CSE373', 'CSE425', 'EEE141', 'EEE141L', 'EEE111', 'EEE111L']
                },
                'Capstone & Electives': {
                    'credits': 16,
                    'courses': ['CSE299', 'CSE499A', 'CSE499B'],
                    'major_electives': 9,
                    'open_elective': 3,
                    'internship': 'CSE498R'
                }
            }
        },
        'BBA': {
            'total': 124,
            'waivers': {'ENG102': 3, 'BUS112': 3},
            'categories': {
                'General Education': {
                    'credits': 30,
                    'courses': ['ENG103', 'ENG105', 'HIS103', 'PHI101', 'ENV203'],
                    'electives': []
                },
                'School Core': {
                    'credits': 21,
                    'courses': ['ECO101', 'ECO104', 'MIS107', 'BUS251', 'BUS172', 'BUS173', 'BUS135']
                },
                'BBA Core': {
                    'credits': 36,
                    'courses': ['ACT201', 'ACT202', 'FIN254', 'LAW200', 'INB372', 'MKT202', 'MIS207', 'MGT212', 'MGT351', 'MGT314', 'MGT368', 'MGT489']
                },
                'Major Concentration': {
                    'credits': 18,
                    'marketing': ['MKT337', 'MKT344', 'MKT460', 'MKT470'],
                    'finance': ['FIN433', 'FIN435', 'FIN440', 'FIN444'],
                    'accounting': ['ACT310', 'ACT320', 'ACT360', 'ACT370'],
                    'hrm': ['HRM340', 'HRM360', 'HRM380', 'HRM450'],
                    'mis': ['MIS210', 'MIS310', 'MIS320', 'MIS470'],
                    'supply_chain': ['SCM310', 'SCM320', 'SCM450', 'MGT460']
                },
                'Capstone & Electives': {
                    'credits': 19,
                    'open_electives': 9,
                    'internship': 'BUS498'
                }
            }
        },
        'ECONOMICS': {
            'total': 124,
            'waivers': {'ENG102': 3, 'MAT112': 3},
            'categories': {
                'General Education': {
                    'credits': 30,
                    'courses': ['ENG103', 'ENG105', 'HIS103', 'PHI101', 'ENV203'],
                    'electives': []
                },
                'School Core': {
                    'credits': 21,
                    'courses': ['ECO101', 'ECO104', 'MIS107', 'BUS251', 'BUS172', 'BUS173', 'BUS135']
                },
                'Economics Core': {
                    'credits': 36,
                    'courses': ['ECO201', 'ECO202', 'ECO301', 'ECO302', 'ECO317', 'ECO328', 'ECO348', 'ECO354', 'ECO372', 'ECO380', 'ECO415', 'ECO472']
                },
                'Capstone & Electives': {
                    'credits': 37,
                    'open_electives': 9,
                    'internship': 'BUS498'
                }
            }
        }
    }


def process_transcript_with_retakes(transcript_file):
    """Process transcript applying retake logic (best grade only)."""
    courses_by_code = defaultdict(list)
    all_courses = []
    invalid_courses = []
    
    try:
        with open(transcript_file, 'r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            for row_num, row in enumerate(reader, start=2):
                try:
                    course_code = str(get_field_value(row, COLUMN_MAPPINGS['course_code'], '')).strip()
                    course_title = str(get_field_value(row, COLUMN_MAPPINGS['course_title'], '')).strip()
                    credits_str = get_field_value(row, COLUMN_MAPPINGS['credits'], '0')
                    credits = float(credits_str) if credits_str else 0.0
                    grade = str(get_field_value(row, COLUMN_MAPPINGS['grade'], '')).strip()
                    semester = str(get_field_value(row, COLUMN_MAPPINGS['semester'], '')).strip()
                    year = str(get_field_value(row, COLUMN_MAPPINGS['year'], '')).strip()
                    attempt_str = get_field_value(row, COLUMN_MAPPINGS['attempt'], '1')
                    attempt = int(attempt_str) if attempt_str else 1
                    
                    course_data = {
                        'row': row_num,
                        'course_code': course_code,
                        'course_title': course_title,
                        'credits': credits,
                        'grade': grade,
                        'grade_points': get_grade_points(grade),
                        'semester': semester,
                        'year': year,
                        'attempt': attempt
                    }
                    
                    all_courses.append(course_data)
                    
                    # Validate course - check if it's a valid NSU course
                    is_valid, course_type = validate_nsu_course(course_code)
                    if not is_valid:
                        invalid_courses.append(course_data)
                        continue
                    
                    # Group by course code for retake analysis (only remove trailing 'L' for lab courses)
                    base_code = course_code[:-1] if course_code.endswith('L') else course_code
                    courses_by_code[base_code].append(course_data)
                    
                except Exception as e:
                    continue
                    
    except Exception as e:
        print(f"Error reading file: {e}")
        sys.exit(1)
    
    # Apply retake logic - keep only best grade for each course
    best_courses = {}
    retake_history = defaultdict(list)
    
    for base_code, attempts in courses_by_code.items():
        # Sort by grade points (descending), then by attempt number (ascending)
        valid_attempts = [a for a in attempts if a['grade_points'] is not None]
        
        if valid_attempts:
            # Find best attempt
            best = max(valid_attempts, key=lambda x: (x['grade_points'], -x['attempt']))
            best_courses[base_code] = best
            
            # Track retake history
            if len(valid_attempts) > 1:
                retake_history[base_code] = sorted(valid_attempts, key=lambda x: x['attempt'])
    
    return best_courses, retake_history, all_courses, invalid_courses


def calculate_cgpa(best_courses):
    """Calculate CGPA using only best grades."""
    total_quality_points = 0.0
    total_credits = 0.0
    valid_credits = 0.0
    failed_credits = 0.0
    
    for course_code, course in best_courses.items():
        if course['grade_points'] is not None:
            credits = course['credits']
            grade_points = course['grade_points']
            
            total_credits += credits
            total_quality_points += (credits * grade_points)
            
            if course['grade'].upper() == 'F':
                failed_credits += credits
            else:
                valid_credits += credits
    
    cgpa = total_quality_points / total_credits if total_credits > 0 else 0.0
    
    return {
        'cgpa': cgpa,
        'total_credits_attempted': total_credits,
        'quality_points': total_quality_points,
        'valid_credits': valid_credits,
        'failed_credits': failed_credits
    }


def detect_major(courses_completed, program):
    """Detect major/concentration based on courses completed."""
    if program.upper() != 'BBA':
        return None, 0
    
    majors = {
        'Marketing': ['MKT337', 'MKT344', 'MKT460', 'MKT470'],
        'Finance': ['FIN433', 'FIN435', 'FIN440', 'FIN444'],
        'Accounting': ['ACT310', 'ACT320', 'ACT360', 'ACT370'],
        'HRM': ['HRM340', 'HRM360', 'HRM380', 'HRM450'],
        'MIS': ['MIS210', 'MIS310', 'MIS320', 'MIS470'],
        'Supply Chain': ['SCM310', 'SCM320', 'SCM450', 'MGT460']
    }
    
    major_scores = {}
    for major_name, major_courses in majors.items():
        completed = sum(1 for c in major_courses if c in courses_completed)
        major_scores[major_name] = completed
    
    # Find best matching major
    if major_scores:
        best_major = max(major_scores.items(), key=lambda x: x[1])[0]
        best_score = major_scores[best_major]
        if best_score > 0:
            return best_major, best_score
    
    return None, 0


def check_requirements(best_courses, program):
    """Check program requirements and identify deficiencies."""
    reqs = get_program_requirements()
    program_reqs = reqs.get(program.upper(), reqs['CSE'])
    
    completed_courses = set(best_courses.keys())
    missing_courses = []
    category_progress = {}
    total_completed = 0.0
    
    # Detect major for BBA to check concentration courses
    detected_major, _ = detect_major(completed_courses, program)
    
    for category_name, category_data in program_reqs['categories'].items():
        required_courses = category_data.get('courses', [])
        required_credits = category_data.get('credits', 0)
        
        # Handle Major Concentration for BBA
        if category_name == 'Major Concentration' and detected_major:
            major_key = detected_major.lower().replace(' ', '_')
            required_courses = category_data.get(major_key, [])
        
        completed_in_category = []
        category_credits = 0.0
        
        for course in required_courses:
            if course in completed_courses:
                completed_in_category.append(course)
                category_credits += best_courses[course]['credits']
        
        # Find missing courses
        missing = [c for c in required_courses if c not in completed_courses]
        
        category_progress[category_name] = {
            'completed': completed_in_category,
            'missing': missing,
            'credits_completed': category_credits,
            'credits_required': required_credits,
            'percentage': (category_credits / required_credits * 100) if required_credits > 0 else 0
        }
        
        total_completed += category_credits
    
    # Collect all missing courses
    for cat_data in category_progress.values():
        for course in cat_data['missing']:
            missing_courses.append(course)
    
    # Track open electives (courses not in any required list)
    all_required = set()
    for cat_name, cat_data in program_reqs['categories'].items():
        all_required.update(cat_data.get('courses', []))
        # Also add University Core electives
        if cat_name == 'University Core':
            all_required.update(cat_data.get('electives', []))
        # Also add major concentration courses for BBA
        if 'marketing' in cat_data:
            all_required.update(cat_data['marketing'])
            all_required.update(cat_data['marketing'])
        if 'finance' in cat_data:
            all_required.update(cat_data['finance'])
        if 'accounting' in cat_data:
            all_required.update(cat_data['accounting'])
        if 'hrm' in cat_data:
            all_required.update(cat_data['hrm'])
        if 'mis' in cat_data:
            all_required.update(cat_data['mis'])
        if 'supply_chain' in cat_data:
            all_required.update(cat_data['supply_chain'])
    
    # Find elective courses (completed but not required) - only NSU courses count
    elective_credits = 0.0
    elective_courses = []
    for course_code in completed_courses:
        if course_code not in all_required:
            # Only count as elective if it's a valid NSU course
            is_valid, _ = validate_nsu_course(course_code)
            if is_valid:
                elective_credits += best_courses[course_code]['credits']
                elective_courses.append(course_code)
    
    # Add elective info to category_progress
    if 'Capstone & Electives' in category_progress:
        cat_data = category_progress['Capstone & Electives']
        open_elective_required = 0
        if program.upper() == 'CSE':
            open_elective_required = 3  # CSE needs 3 credits open elective
        elif program.upper() == 'BBA':
            open_elective_required = 9  # BBA needs 9 credits open electives
        
        cat_data['elective_credits'] = min(elective_credits, open_elective_required)
        cat_data['elective_courses'] = elective_courses
        cat_data['elective_required'] = open_elective_required
    
    # Validate courses - check which are valid NSU courses
    valid_nsu_courses = []
    unknown_courses = []
    
    for course_code in completed_courses:
        is_valid, course_type = validate_nsu_course(course_code)
        if is_valid:
            valid_nsu_courses.append(course_code)
        else:
            unknown_courses.append({
                'code': course_code,
                'credits': best_courses[course_code]['credits'],
                'grade': best_courses[course_code]['grade']
            })
    
    return category_progress, missing_courses, total_completed, valid_nsu_courses, unknown_courses


def generate_detailed_report(best_courses, retake_history, cgpa_data, program, category_progress, missing_courses, total_completed, waiver_status=None, waived_credits=0, adjusted_total=None, valid_nsu_courses=None, unknown_courses=None, invalid_courses=None):
    """Generate comprehensive deficiency report."""
    program_reqs = get_program_requirements()[program.upper()]
    if adjusted_total is None:
        adjusted_total = program_reqs['total']
    detected_major, major_courses = detect_major(set(best_courses.keys()), program)
    
    # Check graduation eligibility
    can_graduate = True
    issues = []
    
    if cgpa_data['cgpa'] < 2.0:
        can_graduate = False
        issues.append(f"CGPA {cgpa_data['cgpa']:.2f} is below 2.00 minimum")
    
    if total_completed < program_reqs['total']:
        can_graduate = False
        issues.append(f"Only {total_completed:.1f}/{program_reqs['total']} credits completed")
    
    if missing_courses:
        can_graduate = False
        issues.append(f"Missing {len(missing_courses)} required courses")
    
    # Print detailed report
    print("\n" + "=" * 80)
    print("NSU ACADEMIC AUDIT REPORT - LEVEL 3: DEFICIENCY REPORTER")
    print("=" * 80)
    print()
    
    # Header
    print(f"Program: {program.upper()}")
    print(f"Degree: Bachelor of {'Science' if program.upper() == 'CSE' else 'Business Administration'}")
    if detected_major:
        print(f"Detected Major: {detected_major} ({major_courses}/6 courses)")
    print()
    
    # Graduation Status
    print("=" * 80)
    if can_graduate:
        print("GRADUATION STATUS: [YES] ELIGIBLE TO GRADUATE")
    else:
        print("GRADUATION STATUS: [NO] CANNOT GRADUATE")
    print("=" * 80)
    print()
    
    # Issues
    if issues:
        print("ISSUES PREVENTING GRADUATION:")
        for i, issue in enumerate(issues, 1):
            print(f"  {i}. {issue}")
        print()
    
    # CGPA Summary
    print("CGPA SUMMARY (Best Grades Only)")
    print("-" * 80)
    print(f"CGPA:                        {cgpa_data['cgpa']:.2f}")
    if cgpa_data['cgpa'] >= 2.0:
        print(f"Academic Standing:           [+] GOOD STANDING")
    else:
        print(f"Academic Standing:           [!] PROBATION")
    print(f"Quality Points:              {cgpa_data['quality_points']:.2f}")
    print(f"Credits Attempted:           {cgpa_data['total_credits_attempted']:.1f}")
    print(f"Credits Earned:              {cgpa_data['valid_credits']:.1f}")
    print(f"Failed Credits:              {cgpa_data['failed_credits']:.1f}")
    print()
    
    # Course Validation
    if valid_nsu_courses or unknown_courses or invalid_courses:
        print("COURSE VALIDATION")
        print("-" * 80)
        
        # Show invalid courses (filtered out - not counted toward credits)
        if invalid_courses:
            print(f"[X] INVALID NSU COURSES:    {len(invalid_courses)}")
            print("\n  These courses are NOT valid NSU courses and were EXCLUDED from credit calculation:")
            for course in invalid_courses:
                print(f"    - {course['course_code']} ({course['course_title']}) - {course['credits']:.1f} credits - Grade: {course['grade']}")
            print()
        
        if valid_nsu_courses:
            print(f"[+] Valid NSU Courses:       {len(valid_nsu_courses)}")
        if unknown_courses:
            print(f"[!] Unknown/External Courses: {len(unknown_courses)}")
            print("\nUnknown Courses Found (not in NSU catalog):")
            for course in unknown_courses:
                print(f"  * {course['code']} - {course['credits']:.1f} credits - Grade: {course['grade']}")
        print()
    
    # Waiver Status
    if waiver_status:
        print("WAIVER STATUS")
        print("-" * 80)
        for course, is_waived in waiver_status.items():
            status = "WAIVED" if is_waived else "REQUIRED"
            symbol = "[-]" if is_waived else "[+]"
            print(f"{symbol} {course}: {status}")
        print(f"\nTotal Credits Waived:        {waived_credits}")
        print(f"Adjusted Credits Required:   {adjusted_total}")
        print()
    
    # Category Progress
    print("PROGRAM REQUIREMENT PROGRESS")
    print("-" * 80)
    for category, progress in category_progress.items():
        percentage = progress['percentage']
        bar_length = 20
        filled = int(bar_length * percentage / 100)
        bar = "#" * filled + "-" * (bar_length - filled)
        
        print(f"{category:<25} {bar} {percentage:>5.1f}%")
        print(f"  Credits: {progress['credits_completed']:.1f}/{progress['credits_required']}")
        if progress['missing']:
            print(f"  Missing: {', '.join(progress['missing'][:3])}")
            if len(progress['missing']) > 3:
                print(f"           ... and {len(progress['missing']) - 3} more")
        
        # Show open elective info for Capstone & Electives category
        if category == 'Capstone & Electives' and 'elective_credits' in progress:
            elec_credits = progress['elective_credits']
            elec_required = progress['elective_required']
            elec_courses = progress.get('elective_courses', [])
            print(f"  Open Electives: {elec_credits:.1f}/{elec_required} credits")
            if elec_courses:
                print(f"    Completed: {', '.join(elec_courses[:3])}")
                if len(elec_courses) > 3:
                    print(f"               ... and {len(elec_courses) - 3} more")
            if elec_credits < elec_required:
                remaining = elec_required - elec_credits
                print(f"    Still need: {remaining:.1f} credits (any course)")
        print()
    
    # Missing Courses Detail
    if missing_courses:
        print("MISSING MANDATORY COURSES")
        print("-" * 80)
        total_missing_credits = 0
        for course in missing_courses[:10]:  # Show first 10
            credit = 3.0  # Default, would need to lookup actual
            print(f"  * {course} (3.0 credits)")
            total_missing_credits += credit
        
        if len(missing_courses) > 10:
            print(f"  ... and {len(missing_courses) - 10} more courses")
        print(f"\nTotal Missing Credits: {total_missing_credits:.1f}")
        print()
    
    # Retake History
    if retake_history:
        print("RETAKE HISTORY")
        print("-" * 80)
        for course_code, attempts in retake_history.items():
            print(f"\n{course_code}:")
            for attempt in attempts:
                best_attempt = max(attempts, key=lambda x: (x['grade_points'] if x['grade_points'] is not None else -1))
                status = "[BEST]" if attempt == best_attempt else ""
                print(f"  Attempt {attempt['attempt']}: {attempt['grade']} ({attempt['semester']} {attempt['year']}) {status}")
        print()
    
    # Final Summary
    print("=" * 80)
    print("FINAL SUMMARY")
    print("=" * 80)
    print(f"Graduation Eligibility:      {'[YES]' if can_graduate else '[NO]'}")
    print(f"CGPA:                        {cgpa_data['cgpa']:.2f}")
    print()
    print("CREDIT REQUIREMENTS:")
    print(f"  Original credits required:  {program_reqs['total']}")
    if waived_credits > 0:
        print(f"  Credits waived:             {waived_credits}")
        print(f"  Adjusted credits required:  {adjusted_total}")
    print(f"  Credits earned:             {total_completed:.1f}")
    print(f"  Credits remaining:          {max(0, adjusted_total - total_completed):.1f}")
    print(f"  Progress:                   {(total_completed/adjusted_total*100):.1f}%")
    
    if not can_graduate:
        remaining = adjusted_total - total_completed
        avg_credits_per_sem = 15
        sems_remaining = int(remaining / avg_credits_per_sem) + (1 if remaining % avg_credits_per_sem > 0 else 0)
        print(f"\nEstimated Time to Graduate:  {sems_remaining} semesters")
    
    print("=" * 80)


def main():
    """Main entry point."""
    if len(sys.argv) < 4:
        print("Usage: python audit_L3.py <transcript_file> <program_name> <program_knowledge.md>")
        print("Example: python audit_L3.py transcript.csv CSE program_knowledge.md")
        print("         python audit_L3.py test_L3.csv BBA program_knowledge.md")
        print("\nSupported programs: CSE, BBA")
        sys.exit(1)
    
    transcript_file = sys.argv[1]
    program_name = sys.argv[2]
    knowledge_file = sys.argv[3]
    
    if not Path(transcript_file).exists():
        print(f"Error: Transcript file '{transcript_file}' not found.")
        sys.exit(1)
    
    print(f"Processing transcript: {transcript_file}")
    print(f"Program: {program_name}")
    
    # Process transcript with retake logic
    best_courses, retake_history, all_courses, invalid_courses = process_transcript_with_retakes(transcript_file)
    
    # Calculate CGPA with best grades
    cgpa_data = calculate_cgpa(best_courses)
    
    # Check requirements
    category_progress, missing_courses, total_completed, valid_nsu_courses, unknown_courses = check_requirements(best_courses, program_name)
    
    # Ask about waivers
    print("\n" + "=" * 80)
    print("WAIVER VERIFICATION")
    print("=" * 80)
    
    program_reqs = get_program_requirements()[program_name.upper()]
    waiver_courses = program_reqs.get('waivers', {})
    completed_courses = set(best_courses.keys())
    
    waived_credits = 0
    waiver_status = {}
    
    print("\nChecking waiver-eligible courses...")
    for course in waiver_courses:
        if course in completed_courses:
            # Course is already in transcript - check if passed or failed
            grade = best_courses[course]['grade']
            if grade in ['A', 'A-', 'B+', 'B', 'B-', 'C+', 'C', 'C-', 'D+', 'D']:
                # Course passed - no waiver needed
                waiver_status[course] = False
                print(f"\n{course}: Completed with grade {grade} - No waiver needed")
            else:
                # Course failed - ask about waiver
                is_waived = ask_waiver_status(course)
                waiver_status[course] = is_waived
                if is_waived:
                    waived_credits += waiver_courses[course]
        else:
            # Course not in transcript - ask about waiver
            is_waived = ask_waiver_status(course)
            waiver_status[course] = is_waived
            if is_waived:
                waived_credits += waiver_courses[course]
    
    # Adjust total required credits
    adjusted_total = program_reqs['total'] - waived_credits
    
    # Generate report with waiver info
    generate_detailed_report(best_courses, retake_history, cgpa_data, program_name, category_progress, missing_courses, total_completed, waiver_status, waived_credits, adjusted_total, valid_nsu_courses, unknown_courses, invalid_courses)


if __name__ == "__main__":
    main()
