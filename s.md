# CSV Data Analysis Report

**Generated**: 2026-03-26 17:53:18

**Source File**: `generated_code/Input/input.csv`

---

## Overview

- **Total Rows**: 11,733
- **Total Columns**: 9
- **Shape**: 11,733 × 9

---

## Data Structure

### Columns

| Column Name | Data Type |
|-------------|-----------|
| BusinessOrg.[Business Org] | str |
| Forecast Iteration.[Forecast Iteration] | str |
| Version.[Version Name] | str |
| Location.[Country] | str |
| Channel.[MPU] | str |
| Channel.[MPU Level 3] | str |
| Item.[Division] | str |
| Item.[Sports Planning Level] | str |
| Actual Cleansed | float64 |

---

## Data Quality

**Completeness**: 100.00%

### Missing Values

[OK] No missing values found

---

## Data Types & Time Detection

| Column | Type | Is Time Column | Time Format |
|--------|------|----------------|-------------|
| BusinessOrg.[Business Org] | str | No | - |
| Forecast Iteration.[Forecast Iteration] | str | No | - |
| Version.[Version Name] | str | No | - |
| Location.[Country] | str | No | - |
| Channel.[MPU] | str | No | - |
| Channel.[MPU Level 3] | str | No | - |
| Item.[Division] | str | No | - |
| Item.[Sports Planning Level] | str | No | - |
| Actual Cleansed | float64 | No | - |

---

## Statistical Summary

| Column | Count | Min | Max | Missing |
|--------|-------|-----|-----|---------|
| Actual Cleansed | 11733 | N/A | N/A | 0 |


---

## Categorical Columns Summary

### BusinessOrg.[Business Org]

- **Unique Values**: 2
- **Sample Values**: GSA, NON-GSA

### Forecast Iteration.[Forecast Iteration]

- **Unique Values**: 1
- **Sample Values**: FI-Default

### Version.[Version Name]

- **Unique Values**: 1
- **Sample Values**: CurrentWorkingView

### Location.[Country]

- **Unique Values**: 1
- **Sample Values**: EMEA

### Channel.[MPU]

- **Unique Values**: 15
- **Sample Values**: EMEA Key Sport Partners MPU, EMEA CEMEA MPU, EMEA Authenticators & Key Lifestyle Partners MPU, EMEA JD Group MPU, EMEA Sports Direct Group MPU

### Channel.[MPU Level 3]

- **Unique Values**: 145
- **Sample Values**: IS GROUP ITALY, ST88, SPORT TIME, ECI, SIZE GROUP

### Item.[Division]

- **Unique Values**: 4
- **Sample Values**: APPAREL DIVISION, EQUIPMENT DIVISION, FOOTWEAR DIVISION, NOT_SUPPLD

### Item.[Sports Planning Level]

- **Unique Values**: 265
- **Sample Values**: Nike_Other_KIDS_APPAREL DIVISION_Kids Football_Global Football Kids, Nike_Other_MENS_APPAREL DIVISION_Mens Basketball_Basketball Mens & Womens, Nike_Other_MENS_APPAREL DIVISION_Mens Football_Global Football Mens & Womens, Nike_Other_MENS_EQUIPMENT DIVISION_Mens Football_Global Football Mens & Womens, Nike_Other_WOMENS_APPAREL DIVISION_Womens Sport_Global Football Mens & Womens

---

## Numeric Columns Summary

### Actual Cleansed

- **Count**: 11733
- **Min**: 0.0399999997
- **Max**: 35356755.30999999
- **Missing Count**: 0

---

## Time Columns Summary

No time columns detected.

---

## Duplicate Analysis

- **Total Duplicate Rows**: 0
- **Percentage**: 0.00%

[OK] No duplicate rows found.

---

## Data Preview

### First 5 Rows

|    | BusinessOrg.[Business Org]   | Forecast Iteration.[Forecast Iteration]   | Version.[Version Name]   | Location.[Country]   | Channel.[MPU]               | Channel.[MPU Level 3]   | Item.[Division]    | Item.[Sports Planning Level]                                                   |   Actual Cleansed |
|---:|:-----------------------------|:------------------------------------------|:-------------------------|:---------------------|:----------------------------|:------------------------|:-------------------|:-------------------------------------------------------------------------------|------------------:|
|  0 | GSA                          | FI-Default                                | CurrentWorkingView       | EMEA                 | EMEA Key Sport Partners MPU | IS GROUP ITALY          | APPAREL DIVISION   | Nike_Other_KIDS_APPAREL DIVISION_Kids Football_Global Football Kids            |          33251.8  |
|  1 | GSA                          | FI-Default                                | CurrentWorkingView       | EMEA                 | EMEA Key Sport Partners MPU | IS GROUP ITALY          | APPAREL DIVISION   | Nike_Other_MENS_APPAREL DIVISION_Mens Basketball_Basketball Mens & Womens      |          45110.3  |
|  2 | GSA                          | FI-Default                                | CurrentWorkingView       | EMEA                 | EMEA Key Sport Partners MPU | IS GROUP ITALY          | APPAREL DIVISION   | Nike_Other_MENS_APPAREL DIVISION_Mens Football_Global Football Mens & Womens   |          42610.8  |
|  3 | GSA                          | FI-Default                                | CurrentWorkingView       | EMEA                 | EMEA Key Sport Partners MPU | IS GROUP ITALY          | EQUIPMENT DIVISION | Nike_Other_MENS_EQUIPMENT DIVISION_Mens Football_Global Football Mens & Womens |           2484.64 |
|  4 | GSA                          | FI-Default                                | CurrentWorkingView       | EMEA                 | EMEA CEMEA MPU              | ST88                    | APPAREL DIVISION   | Nike_Other_KIDS_APPAREL DIVISION_Kids Football_Global Football Kids            |          11367.6  |

### Last 5 Rows

|       | BusinessOrg.[Business Org]   | Forecast Iteration.[Forecast Iteration]   | Version.[Version Name]   | Location.[Country]   | Channel.[MPU]                                    | Channel.[MPU Level 3]   | Item.[Division]    | Item.[Sports Planning Level]                                                    |   Actual Cleansed |
|------:|:-----------------------------|:------------------------------------------|:-------------------------|:---------------------|:-------------------------------------------------|:------------------------|:-------------------|:--------------------------------------------------------------------------------|------------------:|
| 11728 | NON-GSA                      | FI-Default                                | CurrentWorkingView       | EMEA                 | EMEA Key Sport Partners MPU                      | IBERIA GP               | FOOTWEAR DIVISION  | Nike_Other_KIDS_FOOTWEAR DIVISION_No Fields of Play_Nike_Other                  |              0.28 |
| 11729 | NON-GSA                      | FI-Default                                | CurrentWorkingView       | EMEA                 | EMEA JD Group MPU                                | JD OUTWEAR              | EQUIPMENT DIVISION | Nike_Other_KIDS_EQUIPMENT DIVISION_Kids Running and Fitness_Training Kids       |              1.97 |
| 11730 | NON-GSA                      | FI-Default                                | CurrentWorkingView       | EMEA                 | EMEA JD Group MPU                                | JD OUTWEAR              | EQUIPMENT DIVISION | Nike_Other_MENS_EQUIPMENT DIVISION_Mens Lifestyle_Nike Sportswear Mens & Womens |              0.29 |
| 11731 | NON-GSA                      | FI-Default                                | CurrentWorkingView       | EMEA                 | EMEA CEMEA MPU                                   | ISRAEL ROB              | EQUIPMENT DIVISION | Nike_Other_KIDS_EQUIPMENT DIVISION_Kids Basketball_Basketball Kids              |              0.7  |
| 11732 | NON-GSA                      | FI-Default                                | CurrentWorkingView       | EMEA                 | EMEA Authenticators & Key Lifestyle Partners MPU | OTTO                    | EQUIPMENT DIVISION | Nike_Other_MENS_EQUIPMENT DIVISION_Mens Football_Global Football Mens & Womens  |              3.94 |

---

## Recommendations

No specific recommendations at this time.

---

## Report Information

---

*Report generated by CSV Analysis Agent using EDA Utilities*
