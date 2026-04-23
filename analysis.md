# CSV Data Analysis Report

**Generated**: 2026-04-23 14:39:24

**Source File**: `generated_code/Input\input.csv`

---

## Overview

- **Total Rows**: 155,589
- **Total Columns**: 8
- **Shape**: 155,589 × 8

---

## Data Structure

### Columns

| Column Name | Data Type |
|-------------|-----------|
| BusinessOrg.[Business Org] | object |
| Forecast Iteration.[Forecast Iteration] | object |
| Version.[Version Name] | object |
| Location.[Country] | object |
| Channel.[MPU Level 3] | object |
| Time.[Partial Week] | object |
| Item.[Product Planning Level] | object |
| Ensemble Fcst Weighted | float64 |

---

## Data Quality

**Completeness**: 100.00%

### Missing Values

[OK] No missing values found

---

## Data Types & Time Detection

| Column | Type | Is Time Column | Time Format |
|--------|------|----------------|-------------|
| BusinessOrg.[Business Org] | object | No | - |
| Forecast Iteration.[Forecast Iteration] | object | No | - |
| Version.[Version Name] | object | No | - |
| Location.[Country] | object | No | - |
| Channel.[MPU Level 3] | object | No | - |
| Time.[Partial Week] | object | No | - |
| Item.[Product Planning Level] | object | No | - |
| Ensemble Fcst Weighted | float64 | No | - |

---

## Statistical Summary

| Column | Count | Min | Max | Missing |
|--------|-------|-----|-----|---------|
| Ensemble Fcst Weighted | 155589 | N/A | N/A | 0 |


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
- **Sample Values**: Test

### Location.[Country]

- **Unique Values**: 3
- **Sample Values**: CHINA, TAIWAN, HONG KONG

### Channel.[MPU Level 3]

- **Unique Values**: 8
- **Sample Values**: Nike Direct - Stores, Nike Marketplace Partners, Douyin, Nike Retail Factory Stores, Tmall

### Time.[Partial Week]

- **Unique Values**: 93
- **Sample Values**: 05-Apr-26, 12-Apr-26, 19-Apr-26, 26-Apr-26, 01-May-26

### Item.[Product Planning Level]

- **Unique Values**: 180
- **Sample Values**: Nike_NOT_SUPPLD_KIDS_APPAREL DIVISION_GLOBAL FOOTBALL, Nike_NOT_SUPPLD_WOMENS_APPAREL DIVISION_BASKETBALL, Nike_NOT_SUPPLD_KIDS_APPAREL DIVISION_BASKETBALL, Nike_NOT_SUPPLD_MENS_APPAREL DIVISION_GLOBAL FOOTBALL, Nike_NOT_SUPPLD_MENS_EQUIPMENT DIVISION_GLOBAL FOOTBALL

---

## Numeric Columns Summary

### Ensemble Fcst Weighted

- **Count**: 155589
- **Min**: 0.0
- **Max**: 259928.9255
- **Missing Count**: 0

---

## Time Columns Summary

### Time.[Partial Week]

- **Data Type**: object
- **Format**: string/object (time-like)
- **Sample Values**: ['05-Apr-26', '05-Apr-26', '05-Apr-26', '05-Apr-26', '05-Apr-26']
- **Missing Count**: 0

---

## Duplicate Analysis

- **Total Duplicate Rows**: 0
- **Percentage**: 0.00%

[OK] No duplicate rows found.

---

## Data Preview

### First 5 Rows

|    | BusinessOrg.[Business Org]   | Forecast Iteration.[Forecast Iteration]   | Version.[Version Name]   | Location.[Country]   | Channel.[MPU Level 3]   | Time.[Partial Week]   | Item.[Product Planning Level]                         |   Ensemble Fcst Weighted |
|---:|:-----------------------------|:------------------------------------------|:-------------------------|:---------------------|:------------------------|:----------------------|:------------------------------------------------------|-------------------------:|
|  0 | GSA                          | FI-Default                                | Test                     | CHINA                | Nike Direct - Stores    | 05-Apr-26             | Nike_NOT_SUPPLD_KIDS_APPAREL DIVISION_GLOBAL FOOTBALL |                 0.074116 |
|  1 | GSA                          | FI-Default                                | Test                     | CHINA                | Nike Direct - Stores    | 05-Apr-26             | Nike_NOT_SUPPLD_WOMENS_APPAREL DIVISION_BASKETBALL    |                 0.700004 |
|  2 | GSA                          | FI-Default                                | Test                     | TAIWAN               | Nike Direct - Stores    | 05-Apr-26             | Nike_NOT_SUPPLD_WOMENS_APPAREL DIVISION_BASKETBALL    |                 0        |
|  3 | GSA                          | FI-Default                                | Test                     | CHINA                | Nike Direct - Stores    | 05-Apr-26             | Nike_NOT_SUPPLD_KIDS_APPAREL DIVISION_BASKETBALL      |                 0        |
|  4 | GSA                          | FI-Default                                | Test                     | CHINA                | Nike Direct - Stores    | 05-Apr-26             | Nike_NOT_SUPPLD_MENS_APPAREL DIVISION_GLOBAL FOOTBALL |                51.4784   |

### Last 5 Rows

|        | BusinessOrg.[Business Org]   | Forecast Iteration.[Forecast Iteration]   | Version.[Version Name]   | Location.[Country]   | Channel.[MPU Level 3]   | Time.[Partial Week]   | Item.[Product Planning Level]                    |   Ensemble Fcst Weighted |
|-------:|:-----------------------------|:------------------------------------------|:-------------------------|:---------------------|:------------------------|:----------------------|:-------------------------------------------------|-------------------------:|
| 155584 | NON-GSA                      | FI-Default                                | Test                     | CHINA                | Nike.com                | 26-Sep-27             | Nike_NOT_SUPPLD_KIDS_FOOTWEAR DIVISION_RUNNING   |               168.811    |
| 155585 | NON-GSA                      | FI-Default                                | Test                     | CHINA                | Nike.com                | 26-Sep-27             | Nike_NOT_SUPPLD_KIDS_FOOTWEAR DIVISION_SKATE     |                 3.70842  |
| 155586 | NON-GSA                      | FI-Default                                | Test                     | CHINA                | Nike.com                | 26-Sep-27             | Nike_KOBE_MENS_FOOTWEAR DIVISION_GLOBAL FOOTBALL |                 2.06836  |
| 155587 | NON-GSA                      | FI-Default                                | Test                     | CHINA                | Nike.com                | 26-Sep-27             | Nike_KOBE_KIDS_FOOTWEAR DIVISION_GLOBAL FOOTBALL |                 0.160562 |
| 155588 | NON-GSA                      | FI-Default                                | Test                     | CHINA                | Nike.com                | 26-Sep-27             | Nike_ACG_MENS_FOOTWEAR DIVISION_SKATE            |                 8.19745  |

---

## Recommendations

No specific recommendations at this time.

---

## Report Information

---

*Report generated by CSV Analysis Agent using EDA Utilities*
