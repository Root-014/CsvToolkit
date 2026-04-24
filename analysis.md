## File: Fact.DownloadResult247872ef3de7467cb8ff769b234539c5.csv
# CSV Data Analysis Report

**Generated**: 2026-04-25 00:31:39

**Source File**: `Fact.DownloadResult247872ef3de7467cb8ff769b234539c5.csv`

---

## Overview

- **Total Rows**: 2,018,846
- **Total Columns**: 12
- **Shape**: 2,018,846 × 12

---

## Data Structure

### Columns

| Column Name | Data Type |
|-------------|-----------|
| BusinessOrg.[Business Org] | object |
| Location.[Country] | object |
| Location.[Geo Territory] | object |
| Version.[Version Name] | object |
| Channel.[MPU Level 3] | object |
| Channel.[MPU] | object |
| Item.[Product Planning Level] | object |
| Item.[Consumer Offense Cd] | object |
| Time.[Week] | object |
| Class.[Class] | object |
| Product Customer L1 Segment | int64 |
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
| BusinessOrg.[Business Org] | object | No | - |
| Location.[Country] | object | No | - |
| Location.[Geo Territory] | object | No | - |
| Version.[Version Name] | object | No | - |
| Channel.[MPU Level 3] | object | No | - |
| Channel.[MPU] | object | No | - |
| Item.[Product Planning Level] | object | No | - |
| Item.[Consumer Offense Cd] | object | No | - |
| Time.[Week] | object | No | - |
| Class.[Class] | object | No | - |
| Product Customer L1 Segment | int64 | No | - |
| Actual Cleansed | float64 | No | - |

---

## Statistical Summary

| Column | Count | Min | Max | Missing |
|--------|-------|-----|-----|---------|
| Product Customer L1 Segment | 2018846 | N/A | N/A | 0 |
| Actual Cleansed | 2018846 | N/A | N/A | 0 |


---

## Categorical Columns Summary

### BusinessOrg.[Business Org]

- **Unique Values**: 2
- **Sample Values**: GSA, NON-GSA

### Location.[Country]

- **Unique Values**: 14
- **Sample Values**: REPUBLIC OF KOREA, JAPAN, BRAZIL, SINGAPORE, THAILAND

### Location.[Geo Territory]

- **Unique Values**: 7
- **Sample Values**: KOREA, JAPAN, BRAZIL, SOUTHEAST ASIA INDIA, MEXICO

### Version.[Version Name]

- **Unique Values**: 1
- **Sample Values**: CurrentWorkingView

### Channel.[MPU Level 3]

- **Unique Values**: 313
- **Sample Values**: NIKE.COM KOREA, NVS KOREA, KASINA, CAPO SPORTS TOWN, RACEMENT

### Channel.[MPU]

- **Unique Values**: 57
- **Sample Values**: KR_ND_NDDC, KR_ND_Value, KR_NMP_Authenticating, KR_NMP_Key Partner, KR_NMP_Strategic Partner

### Item.[Product Planning Level]

- **Unique Values**: 199
- **Sample Values**: Nike_KOBE_KIDS_APPAREL DIVISION_GLOBAL FOOTBALL, Nike_NOT_SUPPLD_MENS_APPAREL DIVISION_SPORTSWEAR, Nike_NOT_SUPPLD_MENS_EQUIPMENT DIVISION_GLOBAL FOOTBALL, Nike_NOT_SUPPLD_WOMENS_APPAREL DIVISION_GLOBAL FOOTBALL, Nike_NOT_SUPPLD_MENS_APPAREL DIVISION_GLOBAL FOOTBALL

### Item.[Consumer Offense Cd]

- **Unique Values**: 4
- **Sample Values**: KIDS, MENS, WOMENS, NOT_SUPPLD

### Time.[Week]

- **Unique Values**: 156
- **Sample Values**: 12-Oct-25, 24-Aug-25, 14-Sep-25, 17-Aug-25, 09-Nov-25

### Class.[Class]

- **Unique Values**: 6
- **Sample Values**: NEW LAUNCH, DISC, BY, AY, BX

---

## Numeric Columns Summary

### Product Customer L1 Segment

- **Count**: 2018846
- **Min**: 1
- **Max**: 1
- **Missing Count**: 0

### Actual Cleansed

- **Count**: 2018846
- **Min**: 0.0
- **Max**: 165848.0
- **Missing Count**: 0

---

## Time Columns Summary

### Time.[Week]

- **Data Type**: object
- **Format**: string/object (time-like)
- **Sample Values**: ['12-Oct-25', '24-Aug-25', '14-Sep-25', '17-Aug-25', '09-Nov-25']
- **Missing Count**: 0

---

## Duplicate Analysis

- **Total Duplicate Rows**: 0
- **Percentage**: 0.00%

[OK] No duplicate rows found.

---

## Data Preview

### First 5 Rows

|    | BusinessOrg.[Business Org]   | Location.[Country]   | Location.[Geo Territory]   | Version.[Version Name]   | Channel.[MPU Level 3]   | Channel.[MPU]   | Item.[Product Planning Level]                   | Item.[Consumer Offense Cd]   | Time.[Week]   | Class.[Class]   |   Product Customer L1 Segment |   Actual Cleansed |
|---:|:-----------------------------|:---------------------|:---------------------------|:-------------------------|:------------------------|:----------------|:------------------------------------------------|:-----------------------------|:--------------|:----------------|------------------------------:|------------------:|
|  0 | GSA                          | REPUBLIC OF KOREA    | KOREA                      | CurrentWorkingView       | NIKE.COM KOREA          | KR_ND_NDDC      | Nike_KOBE_KIDS_APPAREL DIVISION_GLOBAL FOOTBALL | KIDS                         | 12-Oct-25     | NEW LAUNCH      |                             1 |                 0 |
|  1 | GSA                          | REPUBLIC OF KOREA    | KOREA                      | CurrentWorkingView       | NIKE.COM KOREA          | KR_ND_NDDC      | Nike_KOBE_KIDS_APPAREL DIVISION_GLOBAL FOOTBALL | KIDS                         | 24-Aug-25     | NEW LAUNCH      |                             1 |                 3 |
|  2 | GSA                          | REPUBLIC OF KOREA    | KOREA                      | CurrentWorkingView       | NIKE.COM KOREA          | KR_ND_NDDC      | Nike_KOBE_KIDS_APPAREL DIVISION_GLOBAL FOOTBALL | KIDS                         | 14-Sep-25     | NEW LAUNCH      |                             1 |                 4 |
|  3 | GSA                          | REPUBLIC OF KOREA    | KOREA                      | CurrentWorkingView       | NIKE.COM KOREA          | KR_ND_NDDC      | Nike_KOBE_KIDS_APPAREL DIVISION_GLOBAL FOOTBALL | KIDS                         | 17-Aug-25     | NEW LAUNCH      |                             1 |                 7 |
|  4 | GSA                          | REPUBLIC OF KOREA    | KOREA                      | CurrentWorkingView       | NIKE.COM KOREA          | KR_ND_NDDC      | Nike_KOBE_KIDS_APPAREL DIVISION_GLOBAL FOOTBALL | KIDS                         | 09-Nov-25     | NEW LAUNCH      |                             1 |                14 |

### Last 5 Rows

|         | BusinessOrg.[Business Org]   | Location.[Country]   | Location.[Geo Territory]   | Version.[Version Name]   | Channel.[MPU Level 3]   | Channel.[MPU]          | Item.[Product Planning Level]                | Item.[Consumer Offense Cd]   | Time.[Week]   | Class.[Class]   |   Product Customer L1 Segment |   Actual Cleansed |
|--------:|:-----------------------------|:---------------------|:---------------------------|:-------------------------|:------------------------|:-----------------------|:---------------------------------------------|:-----------------------------|:--------------|:----------------|------------------------------:|------------------:|
| 2018841 | NON-GSA                      | INDONESIA            | SOUTHEAST ASIA INDIA       | CurrentWorkingView       | ID NSP VALUE - CV MITRA | SEAI_NSP_Value Partner | Nike_NOT_SUPPLD_KIDS_FOOTWEAR DIVISION_SKATE | KIDS                         | 10-Nov-24     | BY              |                             1 |              0.46 |
| 2018842 | NON-GSA                      | INDONESIA            | SOUTHEAST ASIA INDIA       | CurrentWorkingView       | ID NSP VALUE - CV MITRA | SEAI_NSP_Value Partner | Nike_NOT_SUPPLD_KIDS_FOOTWEAR DIVISION_SKATE | KIDS                         | 14-Sep-25     | BY              |                             1 |              0    |
| 2018843 | NON-GSA                      | INDONESIA            | SOUTHEAST ASIA INDIA       | CurrentWorkingView       | ID NSP VALUE - CV MITRA | SEAI_NSP_Value Partner | Nike_NOT_SUPPLD_KIDS_FOOTWEAR DIVISION_SKATE | KIDS                         | 23-Mar-25     | BY              |                             1 |              1.54 |
| 2018844 | NON-GSA                      | INDONESIA            | SOUTHEAST ASIA INDIA       | CurrentWorkingView       | ID NSP VALUE - CV MITRA | SEAI_NSP_Value Partner | Nike_NOT_SUPPLD_KIDS_FOOTWEAR DIVISION_SKATE | KIDS                         | 30-Jun-24     | BY              |                             1 |              0.32 |
| 2018845 | NON-GSA                      | INDONESIA            | SOUTHEAST ASIA INDIA       | CurrentWorkingView       | ID NSP VALUE - CV MITRA | SEAI_NSP_Value Partner | Nike_NOT_SUPPLD_KIDS_FOOTWEAR DIVISION_SKATE | KIDS                         | 18-May-25     | BY              |                             1 |              0    |

---

## Recommendations

No specific recommendations at this time.

---

## Report Information

---

*Report generated by CSV Analysis Agent using EDA Utilities*


