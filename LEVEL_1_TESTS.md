# ============================================
# LEVEL 1 - CREDIT TALLY ENGINE
# CSE226.1 NSU Academic Audit System
# ============================================

## ✅ COMPLETE TEST FILES (12 Files)

| # | File Name | Description | Courses | Credits | Status |
|---|-----------|-------------|---------|---------|--------|
| 01 | test_L1_01_all_grades.csv | All grade types | 15 | 24.0 | ✅ PASS |
| 02 | test_L1_02_grade_A_to_D.csv | All passing grades | 10 | 24.0 | ✅ PASS |
| 03 | test_L1_03_grade_F_only.csv | All F grades | 5 | 0.0 | ✅ PASS |
| 04 | test_L1_04_grade_W_withdrawal.csv | All W grades | 5 | 0.0 | ✅ PASS |
| 05 | test_L1_05_grade_I_incomplete.csv | All I grades | 5 | 0.0 | ✅ PASS |
| 06 | test_L1_06_grade_AU_audit.csv | All AU grades | 5 | 0.0 | ✅ PASS |
| 07 | test_L1_07_mixed_grades.csv | Mixed grades | 8 | 12.0 | ✅ PASS |
| 08 | test_L1_08_lab_and_special_credits.csv | Labs & special | 9 | 9.0 | ✅ PASS |
| 09 | test_L1_09_invalid_grades.csv | Invalid grades | 6 | 0.0 | ✅ PASS |
| 10 | test_L1_10_retake_multiple_attempts.csv | Retakes | 12 | 20.0 | ✅ PASS |
| 11 | test_L1_11_bba_courses.csv | BBA courses | 12 | 36.0 | ✅ PASS |
| 12 | test_L1_12_zero_credit_courses.csv | 0-credit courses | 4 | 0.0 | ✅ PASS |

---

## 🎯 How to Run Tests

```bash
# Test 1: All grade types
python audit_L1.py test_L1_01_all_grades.csv

# Test 2: All passing grades
python audit_L1.py test_L1_02_grade_A_to_D.csv

# Test 3: All F grades
python audit_L1.py test_L1_03_grade_F_only.csv

# Test 4: All W grades
python audit_L1.py test_L1_04_grade_W_withdrawal.csv

# Test 5: All I grades
python audit_L1.py test_L1_05_grade_I_incomplete.csv

# Test 6: All AU grades
python audit_L1.py test_L1_06_grade_AU_audit.csv

# Test 7: Mixed grades
python audit_L1.py test_L1_07_mixed_grades.csv

# Test 8: Lab & special credits
python audit_L1.py test_L1_08_lab_and_special_credits.csv

# Test 9: Invalid grades
python audit_L1.py test_L1_09_invalid_grades.csv

# Test 10: Retakes
python audit_L1.py test_L1_10_retake_multiple_attempts.csv

# Test 11: BBA courses
python audit_L1.py test_L1_11_bba_courses.csv

# Test 12: 0-credit courses
python audit_L1.py test_L1_12_zero_credit_courses.csv
```

---

## ✅ Features Tested

### Grade Types:
- ✅ A (4.0), A- (3.7)
- ✅ B+ (3.3), B (3.0), B- (2.7)
- ✅ C+ (2.3), C (2.0), C- (1.7)
- ✅ D+ (1.3), D (1.0) - Minimum passing
- ✅ F (0.0) - Failure
- ✅ W - Withdrawal
- ✅ I - Incomplete
- ✅ AU - Audit
- ✅ X, P, Z, AB, NR, blank - Invalid

### Credit Types:
- ✅ 0-credit (CSE498R internship)
- ✅ 1-credit (lab courses)
- ✅ 1.5-credit (CSE499A, CSE499B)
- ✅ 3-credit (regular courses)

### Course Types:
- ✅ CSE courses (CSE115, CSE215, etc.)
- ✅ MAT courses (MAT116, MAT120, etc.)
- ✅ PHY courses (PHY107, PHY108, etc.)
- ✅ ENG courses (ENG102, ENG103, etc.)
- ✅ BBA courses (ECO101, BUS251, etc.)

### Scenarios:
- ✅ Multiple retakes with attempt numbers
- ✅ Different semesters (Fall, Spring, Summer)
- ✅ Different years
- ✅ Student ID appears once per file

---

## 📊 CSV Format

```
student_id,course_code,course_title,credits,grade,semester,year,attempt
20230001,CSE115,Computer Programming I,3.0,A,Fall,2023,1
,CSE115L,Programming Lab,1.0,A-,Fall,2023,1
,MAT116,Pre-Calculus,3.0,B+,Fall,2023,1
```

- Student ID appears ONCE in first row
- Subsequent rows have empty first column

---

## 🎓 PROJECT STATUS: 100% COMPLETE ✅

All 12 Level 1 tests passing!
Ready for demonstration!
