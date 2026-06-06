## File: Rev_NA.csv
# CSV Data Analysis Report

**Generated**: 2026-06-06 18:26:10

**Source File**: `Rev_NA.csv`

---

## Overview

- **Total Rows**: 276,577
- **Total Columns**: 10
- **Shape**: 276,577 × 10
- **Memory Usage**: 130.31 MB

---

## Data Structure

### Columns

| Column Name | Data Type |
|-------------|-----------|
| Version.[Version Name] | object |
| Forecast Iteration.[Forecast Iteration] | object |
| BusinessOrg.[Business Org] | object |
| Location.[Country] | object |
| Channel.[MPU Level 3] | object |
| Time.[Retail Planning Month] | object |
| Item.[Product Planning Level] | object |
| Stat Actual Amt | float64 |
| Final Revenue Forecast | float64 |
| Revenue Fcst Baseline | float64 |

---

## Data Quality

**Completeness**: 87.97%

### Missing Values

| Column | Missing Count | Missing Percentage |
|--------|---------------|--------------------|
| Stat Actual Amt | 51555 | 18.64% |
| Final Revenue Forecast | 159289 | 57.59% |
| Revenue Fcst Baseline | 121765 | 44.03% |

---

## Data Types & Time Detection

| Column | Type | Is Time Column | Time Format |
|--------|------|----------------|-------------|
| Version.[Version Name] | object | No | - |
| Forecast Iteration.[Forecast Iteration] | object | No | - |
| BusinessOrg.[Business Org] | object | No | - |
| Location.[Country] | object | No | - |
| Channel.[MPU Level 3] | object | No | - |
| Time.[Retail Planning Month] | object | No | - |
| Item.[Product Planning Level] | object | No | - |
| Stat Actual Amt | float64 | No | - |
| Final Revenue Forecast | float64 | No | - |
| Revenue Fcst Baseline | float64 | No | - |

---

## Statistical Summary

| Column | Count | Min | Max | Missing |
|--------|-------|-----|-----|---------|
| Stat Actual Amt | 225022 | 0.0 | 148100126.0 | 51555 |
| Final Revenue Forecast | 117288 | 0.0 | 127358557.62694466 | 159289 |
| Revenue Fcst Baseline | 154812 | 0.0 | 148100126.9619211 | 121765 |


---

## Categorical Columns Summary

### Version.[Version Name]

- **Unique Values**: 1
- **Sample Values**: CurrentWorkingView

### Forecast Iteration.[Forecast Iteration]

- **Unique Values**: 1
- **Sample Values**: FI-Default

### BusinessOrg.[Business Org]

- **Unique Values**: 2
- **Sample Values**: GSA, NON-GSA

### Location.[Country]

- **Unique Values**: 2
- **Sample Values**: UNITED STATES OF AMERICA, CANADA

### Channel.[MPU Level 3]

- **Unique Values**: 75
- **Sample Values**: DIGITAL FIRST PARTNERS TIER 1, FAMOUS FOOTWEAR, INC, SHOE CARNIVAL INC, SHOE PALACE, TENNIS SPECIALTY

### Time.[Retail Planning Month]

- **Unique Values**: 54
- **Sample Values**: Jul-21, Aug-21, Sep-21, Oct-21, Nov-21

### Item.[Product Planning Level]

- **Unique Values**: 250
- **Sample Values**: Nike_NOT_SUPPLD_MENS_APPAREL DIVISION_BASKETBALL, Nike_NOT_SUPPLD_MENS_APPAREL DIVISION_GLOBAL FOOTBALL, Nike_NOT_SUPPLD_WOMENS_APPAREL DIVISION_BASKETBALL, Nike_NOT_SUPPLD_MENS_EQUIPMENT DIVISION_GLOBAL FOOTBALL, Nike_NOT_SUPPLD_KIDS_APPAREL DIVISION_SPORTSWEAR

---

## Numeric Columns Summary

### Stat Actual Amt

- **Count**: 225022
- **Min**: 0.0
- **Max**: 148100126.0
- **Missing Count**: 51555

### Final Revenue Forecast

- **Count**: 117288
- **Min**: 0.0
- **Max**: 127358557.62694466
- **Missing Count**: 159289

### Revenue Fcst Baseline

- **Count**: 154812
- **Min**: 0.0
- **Max**: 148100126.9619211
- **Missing Count**: 121765

---

## Time Columns Summary

### Time.[Retail Planning Month]

- **Data Type**: object
- **Format**: string/object (time-like)
- **Sample Values**: ['Jul-21', 'Jul-21', 'Jul-21', 'Jul-21', 'Jul-21']
- **Missing Count**: 0

---

## Duplicate Analysis

- **Total Duplicate Rows**: 0
- **Percentage**: 0.00%

[OK] No duplicate rows found.

---

## Data Preview

### First 5 Rows

|    | Version.[Version Name]   | Forecast Iteration.[Forecast Iteration]   | BusinessOrg.[Business Org]   | Location.[Country]       | Channel.[MPU Level 3]         | Time.[Retail Planning Month]   | Item.[Product Planning Level]                           |   Stat Actual Amt |   Final Revenue Forecast |   Revenue Fcst Baseline |
|---:|:-------------------------|:------------------------------------------|:-----------------------------|:-------------------------|:------------------------------|:-------------------------------|:--------------------------------------------------------|------------------:|-------------------------:|------------------------:|
|  0 | CurrentWorkingView       | FI-Default                                | GSA                          | UNITED STATES OF AMERICA | DIGITAL FIRST PARTNERS TIER 1 | Jul-21                         | Nike_NOT_SUPPLD_MENS_APPAREL DIVISION_BASKETBALL        |           9139.26 |                      nan |                     nan |
|  1 | CurrentWorkingView       | FI-Default                                | GSA                          | UNITED STATES OF AMERICA | DIGITAL FIRST PARTNERS TIER 1 | Jul-21                         | Nike_NOT_SUPPLD_MENS_APPAREL DIVISION_GLOBAL FOOTBALL   |           2206.77 |                      nan |                     nan |
|  2 | CurrentWorkingView       | FI-Default                                | GSA                          | UNITED STATES OF AMERICA | DIGITAL FIRST PARTNERS TIER 1 | Jul-21                         | Nike_NOT_SUPPLD_WOMENS_APPAREL DIVISION_BASKETBALL      |             96.54 |                      nan |                     nan |
|  3 | CurrentWorkingView       | FI-Default                                | GSA                          | UNITED STATES OF AMERICA | DIGITAL FIRST PARTNERS TIER 1 | Jul-21                         | Nike_NOT_SUPPLD_MENS_EQUIPMENT DIVISION_GLOBAL FOOTBALL |           1309.17 |                      nan |                     nan |
|  4 | CurrentWorkingView       | FI-Default                                | GSA                          | UNITED STATES OF AMERICA | DIGITAL FIRST PARTNERS TIER 1 | Jul-21                         | Nike_NOT_SUPPLD_KIDS_APPAREL DIVISION_SPORTSWEAR        |            122.74 |                      nan |                     nan |

### Last 5 Rows

|        | Version.[Version Name]   | Forecast Iteration.[Forecast Iteration]   | BusinessOrg.[Business Org]   | Location.[Country]   | Channel.[MPU Level 3]   | Time.[Retail Planning Month]   | Item.[Product Planning Level]                             |   Stat Actual Amt |   Final Revenue Forecast |   Revenue Fcst Baseline |
|-------:|:-------------------------|:------------------------------------------|:-----------------------------|:---------------------|:------------------------|:-------------------------------|:----------------------------------------------------------|------------------:|-------------------------:|------------------------:|
| 276572 | CurrentWorkingView       | FI-Default                                | NON-GSA                      | CANADA               | LACROSSE SPECIALTY      | Dec-25                         | Nike_NOT_SUPPLD_MENS_EQUIPMENT DIVISION_AMERICAN FOOTBALL |               nan |                  32.5617 |                  233.75 |
| 276573 | CurrentWorkingView       | FI-Default                                | NON-GSA                      | CANADA               | LACROSSE SPECIALTY      | Dec-25                         | Nike_NOT_SUPPLD_MENS_APPAREL DIVISION_TRAINING            |               nan |                 281.074  |                    2.38 |
| 276574 | CurrentWorkingView       | FI-Default                                | NON-GSA                      | CANADA               | LACROSSE SPECIALTY      | Dec-25                         | Nike_NOT_SUPPLD_MENS_APPAREL DIVISION_GOLF                |               nan |                 488.484  |                  489.27 |
| 276575 | CurrentWorkingView       | FI-Default                                | NON-GSA                      | CANADA               | LACROSSE SPECIALTY      | Dec-25                         | Nike_NOT_SUPPLD_MENS_FOOTWEAR DIVISION_BASEBALL           |               nan |                 368.305  |                    0    |
| 276576 | CurrentWorkingView       | FI-Default                                | NON-GSA                      | CANADA               | LACROSSE SPECIALTY      | Dec-25                         | Nike_NOT_SUPPLD_MENS_FOOTWEAR DIVISION_GLOBAL FOOTBALL    |               nan |                 540.048  |                   16.52 |

---

## Recommendations

No specific recommendations at this time.

---

## Report Information

---

*Report generated by CSV Analysis Agent using EDA Utilities*


