#!/usr/bin/env python3
"""
Level 2: CGPA Calculator & Waiver Handler
CSE226.1 Project - Audit Core

This CLI tool calculates weighted CGPA and handles program-specific waivers.
It interactively asks the admin about waivers and adjusts requirements.

Usage:
    python audit_L2.py <transcript_file> <program_name>
    
Example:
    python audit_L2.py transcript.csv CSE
    python audit_L2.py test_L2.csv BBA
"""

import csv
import sys
from pathlib import Path


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
    """Check if a course is a valid NSU course."""
    if course_code in NSU_COURSES:
        return True
    # Check without trailing L for lab courses
    base_code = course_code[:-1] if course_code.endswith('L') else course_code
    if base_code in NSU_COURSES:
        return True
    return False


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
    """
    Convert letter grade to grade points based on NSU policy.
    Returns None for grades that should be excluded from CGPA (W, I, AU).
    """
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
        return None  # Excluded from CGPA calculation
    elif grade in grade_points:
        return grade_points[grade]
    else:
        return None  # Invalid grade


def get_waiver_status(course_code):
    """
    Interactively ask admin about waiver status for a course.
    """
    waiver_info = {
        'ENG102': 'SAT/IELTS scores or high admission test performance',
        'BUS112': 'SAT 1150+ or high admission test scores',
        'MAT112': 'Entry test (for BBA/Economics students)',
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


def get_program_requirements(program_name):
    """
    Get credit requirements for each program.
    """
    requirements = {
        'CSE': {'total': 130, 'waivers': {'ENG102': 3, 'MAT116': 3}},
        'BBA': {'total': 124, 'waivers': {'ENG102': 3, 'BUS112': 3}},
        'ECONOMICS': {'total': 124, 'waivers': {'ENG102': 3, 'MAT112': 3}}
    }
    return requirements.get(program_name.upper(), {'total': 130, 'waivers': {'ENG102': 3}})


def calculate_cgpa_and_credits(transcript_file, program_name):
    """
    Read transcript and calculate CGPA and credits.
    """
    program_reqs = get_program_requirements(program_name)
    
    results = {
        'total_courses': 0,
        'valid_credits': 0.0,
        'cgpa_credits': 0.0,  # Credits included in CGPA (A-F only)
        'quality_points': 0.0,
        'cgpa': 0.0,
        'failed_credits': 0.0,
        'withdrawn_credits': 0.0,
        'incomplete_credits': 0.0,
        'audit_credits': 0.0,
        'zero_credit_courses': 0,
        'invalid_entries': 0,
        'course_details': [],
        'errors': [],
        'waiver_courses': {},
        'program_total': program_reqs['total'],
        'program_waivers': program_reqs['waivers'],
        'adjusted_required': program_reqs['total'],
        'invalid_courses': []  # Track invalid NSU courses
    }
    
    # Track waiver-eligible courses found in transcript (course_code -> grade)
    waiver_eligible = {'ENG102', 'BUS112', 'MAT112', 'MAT116'}
    found_waiver_courses = {}
    
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
                    
                    # Validate course - check if it's a valid NSU course
                    is_valid = validate_nsu_course(course_code)
                    if not is_valid:
                        results['invalid_courses'].append({
                            'row': row_num,
                            'code': course_code,
                            'title': course_title,
                            'credits': credits,
                            'grade': grade
                        })
                        continue  # Skip invalid courses
                    year = str(get_field_value(row, COLUMN_MAPPINGS['year'], '')).strip()
                    attempt_str = get_field_value(row, COLUMN_MAPPINGS['attempt'], '1')
                    attempt = int(attempt_str) if attempt_str else 1
                    
                    results['total_courses'] += 1
                    
                    # Check if this is a waiver-eligible course
                    base_code = course_code[:-1] if course_code.endswith('L') else course_code
                    if base_code in waiver_eligible:
                        found_waiver_courses[base_code] = grade
                    
                    # Get grade points (None if excluded from CGPA)
                    grade_points = get_grade_points(grade)
                    
                    # Calculate quality points and track credits
                    if grade_points is not None:
                        # Valid grade for CGPA calculation (A-F)
                        results['cgpa_credits'] += credits
                        results['quality_points'] += (credits * grade_points)
                        
                        if grade.upper() == 'F':
                            results['failed_credits'] += credits
                            status = "F - Failure (0.0 GPA, No Credit)"
                            category = 'FAILED'
                        else:
                            results['valid_credits'] += credits
                            status = f"{grade} - Passing ({grade_points} GPA, Earns Credit)"
                            category = 'PASSED'
                    else:
                        # W, I, AU - excluded from CGPA
                        grade_upper = grade.upper() if grade else ''
                        if grade_upper == 'W':
                            results['withdrawn_credits'] += credits
                            status = "W - Withdrawn (No Credit, Excluded from CGPA)"
                            category = 'WITHDRAWN'
                        elif grade_upper == 'I':
                            results['incomplete_credits'] += credits
                            status = "I - Incomplete (No Credit, Excluded from CGPA)"
                            category = 'INCOMPLETE'
                        elif grade_upper == 'AU':
                            results['audit_credits'] += credits
                            status = "AU - Audit (No Credit, Excluded from CGPA)"
                            category = 'AUDIT'
                        else:
                            results['invalid_entries'] += 1
                            status = f"{grade if grade else '(blank)'} - Invalid (No Credit)"
                            category = 'INVALID'
                    
                    if credits == 0:
                        results['zero_credit_courses'] += 1
                    
                    course_info = {
                        'row': row_num,
                        'course_code': course_code,
                        'course_title': course_title,
                        'credits': credits,
                        'grade': grade if grade else '(blank)',
                        'grade_points': grade_points,
                        'semester': semester,
                        'year': year,
                        'attempt': attempt,
                        'status': status,
                        'category': category
                    }
                    
                    results['course_details'].append(course_info)
                    
                except ValueError as e:
                    results['errors'].append(f"Row {row_num}: Invalid data - {e}")
                    results['invalid_entries'] += 1
                except Exception as e:
                    results['errors'].append(f"Row {row_num}: Error - {e}")
                    results['invalid_entries'] += 1
                    
    except FileNotFoundError:
        print(f"Error: File '{transcript_file}' not found.")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading file: {e}")
        sys.exit(1)
    
    # Calculate CGPA
    if results['cgpa_credits'] > 0:
        results['cgpa'] = results['quality_points'] / results['cgpa_credits']
    else:
        results['cgpa'] = 0.0
    
    # Ask about waivers for relevant courses
    print("\n" + "=" * 80)
    print("WAIVER VERIFICATION")
    print("=" * 80)
    print(f"\nProgram: {program_name}")
    print("\nChecking for waiver-eligible courses...")
    
    # Determine which waivers to ask about based on program
    program_waivers = {
        'CSE': ['ENG102', 'MAT116'],
        'BBA': ['ENG102', 'BUS112'],
        'ECONOMICS': ['ENG102', 'MAT112']
    }
    
    relevant_waivers = program_waivers.get(program_name.upper(), ['ENG102'])
    
    for course in relevant_waivers:
        if course in found_waiver_courses:
            # Course is in transcript - check the grade
            course_grade = found_waiver_courses[course]
            if course_grade in ['A', 'A-', 'B+', 'B', 'B-', 'C+', 'C', 'C-', 'D+', 'D']:
                # Course passed - no waiver needed
                results['waiver_courses'][course] = False
                print(f"\n{course}: Completed with grade {course_grade} - No waiver needed")
            else:
                # Course failed or no credit - ask if waived
                is_waived = get_waiver_status(course)
                results['waiver_courses'][course] = is_waived
        else:
            # Course not in transcript - ask if waived (student never took it)
            print(f"\nCourse: {course} (Not found in transcript)")
            response = input(f"Was this course waived? (yes/no): ").strip().lower()
            results['waiver_courses'][course] = response in ['yes', 'y']
    
    # Adjust total credits required based on waivers
    waived_credits = 0
    for course, is_waived in results['waiver_courses'].items():
        if is_waived and course in results['program_waivers']:
            waived_credits += results['program_waivers'][course]
    
    results['adjusted_required'] = results['program_total'] - waived_credits
    results['waived_credits'] = waived_credits
    
    return results


def print_report(results, program_name):
    """
    Print formatted Level 2 audit report.
    """
    print("\n" + "=" * 80)
    print("NSU ACADEMIC AUDIT REPORT - LEVEL 2: CGPA & WAIVER HANDLER")
    print("=" * 80)
    print()
    
    # Program Info
    print(f"Program: {program_name.upper()}")
    print()
    
    # CGPA Section
    print("CGPA CALCULATION")
    print("-" * 80)
    print(f"Total Quality Points:        {results['quality_points']:.2f}")
    print(f"Credits in CGPA (A-F only):  {results['cgpa_credits']:.1f}")
    print(f"CGPA:                        {results['cgpa']:.2f}")
    print()
    
    # Academic Standing
    if results['cgpa'] >= 2.0:
        standing = "GOOD STANDING"
        symbol = "[+]"
    else:
        standing = "PROBATION"
        symbol = "[!]"
    
    print(f"Academic Standing:           {symbol} {standing}")
    print(f"  (Minimum required: 2.00)")
    print()
    
    # Invalid Courses Warning
    if results['invalid_courses']:
        print("-" * 80)
        print("[!] INVALID NSU COURSES DETECTED")
        print("-" * 80)
        print("The following courses are NOT valid NSU courses and were EXCLUDED:")
        for inv in results['invalid_courses']:
            print(f"  Row {inv['row']}: {inv['code']} ({inv['title']}) - {inv['credits']:.1f} cr - Grade: {inv['grade']}")
        print()
    
    # Credit Summary
    print("CREDIT SUMMARY")
    print("-" * 80)
    print(f"Credits Earned:               {results['valid_credits']:.1f}")
    print(f"Failed Credits (F):          {results['failed_credits']:.1f}")
    print(f"Withdrawn Credits (W):       {results['withdrawn_credits']:.1f}")
    print(f"Incomplete Credits (I):      {results['incomplete_credits']:.1f}")
    print(f"Audit Credits (AU):          {results['audit_credits']:.1f}")
    print()
    
    # Waiver Status
    print("WAIVER STATUS")
    print("-" * 80)
    if results['waiver_courses']:
        for course, is_waived in results['waiver_courses'].items():
            status = "WAIVED" if is_waived else "REQUIRED"
            symbol = "[-]" if is_waived else "[+]"
            print(f"{symbol} {course}: {status}")
    else:
        print("No waiver-eligible courses for this program.")
    print()
    
    # Course Details
    print("COURSE DETAILS WITH GPA")
    print("-" * 80)
    print(f"{'Row':<4} {'Course':<12} {'Cr':<5} {'Grade':<7} {'GPA':<6} {'Status':<25}")
    print("-" * 80)
    
    for course in results['course_details']:
        row = course['row']
        code = course['course_code'][:11]
        credits = f"{course['credits']:.1f}"
        grade = course['grade'][:6]
        gpa = f"{course['grade_points']:.1f}" if course['grade_points'] is not None else "N/A"
        status = course['status'][:24]
        
        if course['category'] == 'PASSED':
            symbol = "[OK]"
        elif course['category'] == 'FAILED':
            symbol = "[F]"
        elif course['category'] == 'INVALID':
            symbol = "[ER]"
        else:
            symbol = "[--]"
        
        print(f"{row:<4} {code:<12} {credits:<5} {grade:<7} {gpa:<6} {symbol} {status}")
    
    print("-" * 80)
    print()
    
    # Errors
    if results['errors']:
        print("ERRORS")
        print("-" * 80)
        for error in results['errors']:
            print(f"  * {error}")
        print()
    
    # Final Summary
    print("=" * 80)
    print("FINAL SUMMARY")
    print("=" * 80)
    print(f"CGPA:                        {results['cgpa']:.2f}")
    print(f"Academic Standing:           {standing}")
    print()
    print("CREDIT REQUIREMENTS:")
    print(f"  Original credits required:  {results['program_total']}")
    print(f"  Credits waived:             {results.get('waived_credits', 0)}")
    print(f"  Adjusted credits required:  {results['adjusted_required']}")
    print(f"  Credits earned:             {results['valid_credits']:.1f}")
    print(f"  Credits remaining:          {max(0, results['adjusted_required'] - results['valid_credits']):.1f}")
    print()
    print(f"Waiver Courses Waived:       {sum(results['waiver_courses'].values())}/{len(results['waiver_courses'])}")
    print("=" * 80)
    print()
    
    # NSU Policy Notes
    print("NOTE: Based on NSU Academic Policy:")
    print("  * CGPA includes grades A through F only")
    print("  * W and I grades are excluded from CGPA calculation")
    print("  * Waived courses do not count toward credit requirements")
    print("  * Minimum CGPA for Good Standing: 2.00")


def main():
    """
    Main entry point.
    """
    if len(sys.argv) < 3:
        print("Usage: python audit_L2.py <transcript_file> <program_name>")
        print("Example: python audit_L2.py transcript.csv CSE")
        print("         python audit_L2.py test_L2.csv BBA")
        print("\nSupported programs: CSE, BBA, ECONOMICS")
        sys.exit(1)
    
    transcript_file = sys.argv[1]
    program_name = sys.argv[2]
    
    if not Path(transcript_file).exists():
        print(f"Error: File '{transcript_file}' not found.")
        sys.exit(1)
    
    print(f"Processing transcript: {transcript_file}")
    print(f"Program: {program_name}")
    
    # Calculate CGPA and handle waivers
    results = calculate_cgpa_and_credits(transcript_file, program_name)
    
    # Print report
    print_report(results, program_name)


if __name__ == "__main__":
    main()
