#!/usr/bin/env python3
"""
Level 1: Credit Tally Engine
CSE226.1 Project - Audit Core

This CLI tool reads a student transcript and calculates total valid credits earned.
Handles edge cases: F grades, W (withdrawal), I (incomplete), 0-credit courses.

Usage:
    python audit_L1.py <transcript_file>
    
Example:
    python audit_L1.py transcript.csv
    python audit_L1.py test_L1.csv
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
    base_code = course_code[:-1] if course_code.endswith('L') else course_code
    if base_code in NSU_COURSES:
        return True
    return False


def get_grade_status(grade):
    """
    Determine if a grade earns credit based on NSU policy.
    
    Returns:
        tuple: (earns_credit: bool, is_valid: bool, description: str)
    """
    if not grade or grade.strip() == '':
        return (False, False, "Blank/Missing Grade - No credit")
    
    grade = grade.strip().upper()
    
    # Valid passing grades (earn credit)
    passing_grades = {'A', 'A-', 'B+', 'B', 'B-', 'C+', 'C', 'C-', 'D+', 'D'}
    
    # Valid non-passing grades (no credit)
    failing_grades = {'F'}
    non_credit_grades = {'W', 'I', 'AU'}  # Withdrawal, Incomplete, Audit
    
    if grade in passing_grades:
        return (True, True, f"{grade} - Passing Grade (Earns Credit)")
    elif grade in failing_grades:
        return (False, True, f"{grade} - Failure (No Credit)")
    elif grade in non_credit_grades:
        return (False, True, f"{grade} - No Credit Awarded")
    else:
        return (False, False, f"{grade} - Invalid Grade (No Credit)")


def get_field_value(row, possible_names, default=None):
    """Get value from row using multiple possible column names."""
    result = default
    for name in possible_names:
        # Try exact match
        if name in row and row[name]:
            result = row[name]
            break
        # Try case-insensitive match
        for key in row.keys():
            if key.lower() == name.lower() and row[key]:
                result = row[key]
                break
        if result != default:
            break
    return result if result is not None else ''


def calculate_credits(transcript_file):
    """
    Read transcript CSV and calculate total valid credits.
    
    Args:
        transcript_file: Path to the transcript CSV file
        
    Returns:
        dict: Analysis results
    """
    results = {
        'total_courses': 0,
        'valid_credits': 0.0,
        'failed_credits': 0.0,
        'withdrawn_credits': 0.0,
        'incomplete_credits': 0.0,
        'audit_credits': 0.0,
        'zero_credit_courses': 0,
        'invalid_entries': 0,
        'invalid_courses': [],
        'course_details': [],
        'errors': []
    }
    
    # Define possible column name variations
    column_mappings = {
        'course_code': ['course_code', 'course', 'code', 'course_id', 'courseCode'],
        'course_title': ['course_title', 'title', 'course_name', 'name'],
        'credits': ['credits', 'credit', 'cr', 'credit_hours'],
        'grade': ['grade', 'grades', 'letter_grade'],
        'semester': ['semester', 'term', 'session'],
        'year': ['year', 'yr'],
        'attempt': ['attempt', 'try', 'retake']
    }
    
    try:
        with open(transcript_file, 'r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            for row_num, row in enumerate(reader, start=2):
                try:
                    # Extract fields with flexible column names
                    course_code = str(get_field_value(row, column_mappings['course_code'], '')).strip()
                    course_title = str(get_field_value(row, column_mappings['course_title'], '')).strip()
                    credits_str = get_field_value(row, column_mappings['credits'], '0')
                    credits = float(credits_str) if credits_str else 0.0
                    grade = str(get_field_value(row, column_mappings['grade'], '')).strip()
                    semester = str(get_field_value(row, column_mappings['semester'], '')).strip()
                    year = str(get_field_value(row, column_mappings['year'], '')).strip()
                    attempt_str = get_field_value(row, column_mappings['attempt'], '1')
                    attempt = int(attempt_str) if attempt_str else 1
                    
                    # Validate course - check if it's a valid NSU course
                    is_valid_nsu = validate_nsu_course(course_code)
                    if not is_valid_nsu:
                        results['invalid_courses'].append({
                            'row': row_num,
                            'code': course_code,
                            'title': course_title,
                            'credits': credits,
                            'grade': grade if grade else '(blank)'
                        })
                        continue  # Skip invalid courses
                    
                    results['total_courses'] += 1
                    
                    # Analyze grade
                    earns_credit, is_valid, status_desc = get_grade_status(grade)
                    
                    course_info = {
                        'row': row_num,
                        'course_code': course_code,
                        'course_title': course_title,
                        'credits': credits,
                        'grade': grade if grade else '(blank)',
                        'semester': semester,
                        'year': year,
                        'attempt': attempt,
                        'earns_credit': earns_credit,
                        'status': status_desc
                    }
                    
                    # Track by grade type
                    grade_upper = grade.upper() if grade else ''
                    
                    if not is_valid:
                        results['invalid_entries'] += 1
                        course_info['category'] = 'INVALID'
                    elif grade_upper == 'F':
                        results['failed_credits'] += credits
                        course_info['category'] = 'FAILED'
                    elif grade_upper == 'W':
                        results['withdrawn_credits'] += credits
                        course_info['category'] = 'WITHDRAWN'
                    elif grade_upper == 'I':
                        results['incomplete_credits'] += credits
                        course_info['category'] = 'INCOMPLETE'
                    elif grade_upper == 'AU':
                        results['audit_credits'] += credits
                        course_info['category'] = 'AUDIT'
                    elif earns_credit:
                        results['valid_credits'] += credits
                        course_info['category'] = 'PASSED'
                    
                    # Track zero-credit courses
                    if credits == 0:
                        results['zero_credit_courses'] += 1
                    
                    results['course_details'].append(course_info)
                    
                except ValueError as e:
                    results['errors'].append(f"Row {row_num}: Invalid data format - {e}")
                    results['invalid_entries'] += 1
                except Exception as e:
                    results['errors'].append(f"Row {row_num}: Error processing - {e}")
                    results['invalid_entries'] += 1
                    
    except FileNotFoundError:
        print(f"Error: File '{transcript_file}' not found.")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading file: {e}")
        sys.exit(1)
    
    return results


def print_report(results):
    """
    Print formatted audit report.
    """
    print("=" * 80)
    print("NSU ACADEMIC AUDIT REPORT - LEVEL 1: CREDIT TALLY ENGINE")
    print("=" * 80)
    print()
    
    # Summary Statistics
    print("SUMMARY STATISTICS")
    print("-" * 80)
    print(f"Total Courses Processed:     {results['total_courses']}")
    print(f"Credits Earned:              {results['valid_credits']:.1f}")
    print(f"Zero-Credit Courses:         {results['zero_credit_courses']}")
    print(f"Invalid Entries:             {results['invalid_entries']}")
    
    # Invalid NSU Courses Warning
    if results['invalid_courses']:
        print()
        print("-" * 80)
        print("[!] INVALID NSU COURSES DETECTED")
        print("-" * 80)
        print("The following courses are NOT valid NSU courses and were EXCLUDED:")
        for inv in results['invalid_courses']:
            print(f"  Row {inv['row']}: {inv['code']} ({inv['title']}) - {inv['credits']:.1f} cr - Grade: {inv['grade']}")
    
    print()
    
    # Credit Breakdown
    print("CREDIT BREAKDOWN BY STATUS")
    print("-" * 80)
    print(f"[+] Credits Earned (A-D):      {results['valid_credits']:.1f}")
    print(f"[-] Failed Credits (F):        {results['failed_credits']:.1f}")
    print(f"[-] Withdrawn Credits (W):     {results['withdrawn_credits']:.1f}")
    print(f"[-] Incomplete Credits (I):    {results['incomplete_credits']:.1f}")
    print(f"[-] Audit Credits (AU):        {results['audit_credits']:.1f}")
    print()
    
    # Total Attempted
    total_attempted = (results['valid_credits'] + results['failed_credits'] + 
                      results['withdrawn_credits'] + results['incomplete_credits'] +
                      results['audit_credits'])
    print(f"Total Credits Attempted:     {total_attempted:.1f}")
    print()
    
    # Course Details Table
    print("COURSE DETAILS")
    print("-" * 80)
    print(f"{'Row':<4} {'Course':<12} {'Credits':<8} {'Grade':<8} {'Status':<30}")
    print("-" * 80)
    
    for course in results['course_details']:
        row = course['row']
        code = course['course_code'][:11]
        credits = f"{course['credits']:.1f}"
        grade = course['grade'][:7]
        status = course['status'][:28]
        
        # Add symbol based on category
        if course['category'] == 'PASSED':
            symbol = "[OK]"
        elif course['category'] == 'INVALID':
            symbol = "[ER]"
        else:
            symbol = "[NO]"
        
        print(f"{row:<4} {code:<12} {credits:<8} {grade:<8} {symbol} {status}")
    
    print("-" * 80)
    print()
    
    # Errors (if any)
    if results['errors']:
        print("ERRORS ENCOUNTERED")
        print("-" * 80)
        for error in results['errors']:
            print(f"  * {error}")
        print()
    
    # Final Result
    print("=" * 80)
    print(f"FINAL RESULT: Credits Earned = {results['valid_credits']:.1f}")
    print("=" * 80)
    print()
    
    # NSU Policy Reference
    print("NOTE: Based on NSU Academic Policy:")
    print("  * Minimum passing grade: D (60-66, 1.0 grade points)")
    print("  * F grades: No credit earned, but counted in GPA")
    print("  * W (Withdrawal): No credit, not counted in GPA")
    print("  * I (Incomplete): No credit, not counted in GPA")
    print("  * 0-credit courses: Included but contribute 0 to total")


def main():
    """
    Main entry point.
    """
    # Check command line arguments
    if len(sys.argv) < 2:
        print("Usage: python audit_L1.py <transcript_file>")
        print("Example: python audit_L1.py transcript.csv")
        print("         python audit_L1.py test_L1.csv")
        sys.exit(1)
    
    transcript_file = sys.argv[1]
    
    # Verify file exists
    if not Path(transcript_file).exists():
        print(f"Error: File '{transcript_file}' not found.")
        sys.exit(1)
    
    print(f"Processing transcript: {transcript_file}")
    print()
    
    # Calculate credits
    results = calculate_credits(transcript_file)
    
    # Print report
    print_report(results)


if __name__ == "__main__":
    main()
