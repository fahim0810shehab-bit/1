# ============================================
# LEVEL 2 - CGPA CALCULATOR & WAIVER HANDLER
# CSE226.1 NSU Academic Audit System
# ============================================

## ✅ ALL 12 TESTS PASSED!

| # | File Name | Program | CGPA | Standing | Status |
|---|-----------|---------|------|----------|--------|
| 01 | test_L2_01_cse_easy.csv | CSE | 3.58 | GOOD | ✅ PASS |
| 02 | test_L2_02_cse_medium.csv | CSE | 2.07 | GOOD | ✅ PASS |
| 03 | test_L2_03_cse_hard.csv | CSE | 0.80 | PROBATION | ✅ PASS |
| 04 | test_L2_04_cse_probation.csv | CSE | 1.33 | PROBATION | ✅ PASS |
| 05 | test_L2_05_cse_all_waived.csv | CSE | 3.70 | GOOD | ✅ PASS |
| 06 | test_L2_06_cse_partial_waived.csv | CSE | 3.50 | GOOD | ✅ PASS |
| 07 | test_L2_07_bba_easy.csv | BBA | 3.61 | GOOD | ✅ PASS |
| 08 | test_L2_08_bba_medium.csv | BBA | 2.16 | GOOD | ✅ PASS |
| 09 | test_L2_09_bba_probation.csv | BBA | 1.14 | PROBATION | ✅ PASS |
| 10 | test_L2_10_bba_with_waivers.csv | BBA | 3.72 | GOOD | ✅ PASS |
| 11 | test_L2_11_economics.csv | ECON | 3.56 | GOOD | ✅ PASS |
| 12 | test_L2_12_cse_with_zero_credit.csv | CSE | 3.63 | GOOD | ✅ PASS |

---

## ✅ Features Verified

### CGPA Calculation:
- ✅ All letter grades (A to F)
- ✅ Quality points calculation
- ✅ Weighted CGPA
- ✅ W, I, AU excluded from CGPA
- ✅ Invalid grades handled

### Waiver Handling:
- ✅ CSE: ENG102, MAT116 (3 credits each)
- ✅ BBA: ENG102, BUS112 (3 credits each)
- ✅ Economics: ENG102, MAT112 (3 credits each)
- ✅ All waived scenarios
- ✅ Partial waiver scenarios
- ✅ No waiver scenarios

### Academic Standing:
- ✅ Good Standing (CGPA ≥ 2.0)
- ✅ Probation (CGPA < 2.0)

### Credit Types:
- ✅ 0-credit (CSE498R internship)
- ✅ 1-credit (lab courses)
- ✅ 1.5-credit (CSE499A, CSE499B)
- ✅ 3-credit (regular courses)

---

## 🎯 How to Run Tests

```bash
# CSE Tests (answer "n" for no waiver)
cmd /c "echo n & echo n" | python audit_L2.py test_L2_01_cse_easy.csv CSE
cmd /c "echo n & echo n" | python audit_L2.py test_L2_02_cse_medium.csv CSE
cmd /c "echo n & echo n" | python audit_L2.py test_L2_03_cse_hard.csv CSE
cmd /c "echo n & echo n" | python audit_L2.py test_L2_04_cse_probation.csv CSE

# CSE Waivers (answer "y" for yes)
cmd /c "echo y & echo y" | python audit_L2.py test_L2_05_cse_all_waived.csv CSE
cmd /c "echo n & echo y" | python audit_L2.py test_L2_06_cse_partial_waived.csv CSE
cmd /c "echo n & echo n" | python audit_L2.py test_L2_12_cse_with_zero_credit.csv CSE

# BBA Tests (answer "y" for yes - all waived)
cmd /c "echo y & echo y" | python audit_L2.py test_L2_07_bba_easy.csv BBA
cmd /c "echo y & echo y" | python audit_L2.py test_L2_08_bba_medium.csv BBA
cmd /c "echo y & echo y" | python audit_L2.py test_L2_09_bba_probation.csv BBA

# BBA no waiver
cmd /c "echo n & echo n" | python audit_L2.py test_L2_10_bba_with_waivers.csv BBA

# Economics
cmd /c "echo n & echo n" | python audit_L2.py test_L2_11_economics.csv ECONOMICS
```

---

## ✅ NSU Policy Compliance Verified

- ✅ CGPA includes grades A through F only
- ✅ W and I grades excluded from CGPA
- ✅ Minimum passing grade: D (1.0)
- ✅ Academic Standing: Good ≥ 2.0, Probation < 2.0
- ✅ Waivers reduce credit requirements
- ✅ All grade points match NSU scale

---

## 🎓 PROJECT STATUS: 100% COMPLETE ✅

All 12 Level 2 tests passing!
Ready for demonstration!
