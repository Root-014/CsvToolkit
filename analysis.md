## File: Fact.BucketWeights11.csv
# CSV Data Analysis Report

**Generated**: 2026-05-30 13:11:03

**Source File**: `Fact.BucketWeights11.csv`

---

## Overview

- **Total Rows**: 870
- **Total Columns**: 6
- **Shape**: 870 × 6

---

## Data Structure

### Columns

| Column Name | Data Type |
|-------------|-----------|
| Forecast Iteration.[Forecast Iteration] | object |
| Version.[Version Name] | object |
| Time.[Partial Week] | object |
| Stat Bucket Weight | float64 |
| Stat Bucket Weight AUR | float64 |
| Stat Bucket Weight AUR Fcst | int64 |

---

## Data Quality

**Completeness**: 100.00%

### Missing Values

[OK] No missing values found

---

## Data Types & Time Detection

| Column | Type | Is Time Column | Time Format |
|--------|------|----------------|-------------|
| Forecast Iteration.[Forecast Iteration] | object | No | - |
| Version.[Version Name] | object | No | - |
| Time.[Partial Week] | object | No | - |
| Stat Bucket Weight | float64 | No | - |
| Stat Bucket Weight AUR | float64 | No | - |
| Stat Bucket Weight AUR Fcst | int64 | No | - |

---

## Statistical Summary

| Column | Count | Min | Max | Missing |
|--------|-------|-----|-----|---------|
| Stat Bucket Weight | 870 | N/A | N/A | 0 |
| Stat Bucket Weight AUR | 870 | N/A | N/A | 0 |
| Stat Bucket Weight AUR Fcst | 870 | N/A | N/A | 0 |


---

## Categorical Columns Summary

### Forecast Iteration.[Forecast Iteration]

- **Unique Values**: 1
- **Sample Values**: FI-Default

### Version.[Version Name]

- **Unique Values**: 1
- **Sample Values**: CurrentWorkingView

### Time.[Partial Week]

- **Unique Values**: 870
- **Sample Values**: 03-Jul-16, 10-Jul-16, 17-Jul-16, 24-Jul-16, 31-Jul-16

---

## Numeric Columns Summary

### Stat Bucket Weight

- **Count**: 870
- **Min**: 0.032258064516129
- **Max**: 0.25
- **Missing Count**: 0

### Stat Bucket Weight AUR

- **Count**: 870
- **Min**: 0.0
- **Max**: 0.25
- **Missing Count**: 0

### Stat Bucket Weight AUR Fcst

- **Count**: 870
- **Min**: 0
- **Max**: 1
- **Missing Count**: 0

---

## Time Columns Summary

### Time.[Partial Week]

- **Data Type**: object
- **Format**: string/object (time-like)
- **Sample Values**: ['03-Jul-16', '10-Jul-16', '17-Jul-16', '24-Jul-16', '31-Jul-16']
- **Missing Count**: 0

---

## Duplicate Analysis

- **Total Duplicate Rows**: 0
- **Percentage**: 0.00%

[OK] No duplicate rows found.

---

## Data Preview

### First 5 Rows

|    | Forecast Iteration.[Forecast Iteration]   | Version.[Version Name]   | Time.[Partial Week]   |   Stat Bucket Weight |   Stat Bucket Weight AUR |   Stat Bucket Weight AUR Fcst |
|---:|:------------------------------------------|:-------------------------|:----------------------|---------------------:|-------------------------:|------------------------------:|
|  0 | FI-Default                                | CurrentWorkingView       | 03-Jul-16             |            0.241379  |                      0.2 |                             1 |
|  1 | FI-Default                                | CurrentWorkingView       | 10-Jul-16             |            0.241379  |                      0   |                             0 |
|  2 | FI-Default                                | CurrentWorkingView       | 17-Jul-16             |            0.241379  |                      0   |                             0 |
|  3 | FI-Default                                | CurrentWorkingView       | 24-Jul-16             |            0.241379  |                      0   |                             0 |
|  4 | FI-Default                                | CurrentWorkingView       | 31-Jul-16             |            0.0344828 |                      0   |                             0 |

### Last 5 Rows

|     | Forecast Iteration.[Forecast Iteration]   | Version.[Version Name]   | Time.[Partial Week]   |   Stat Bucket Weight |   Stat Bucket Weight AUR |   Stat Bucket Weight AUR Fcst |
|----:|:------------------------------------------|:-------------------------|:----------------------|---------------------:|-------------------------:|------------------------------:|
| 865 | FI-Default                                | CurrentWorkingView       | 01-May-30             |             0.129032 |                      0.2 |                             1 |
| 866 | FI-Default                                | CurrentWorkingView       | 05-May-30             |             0.225806 |                      0   |                             0 |
| 867 | FI-Default                                | CurrentWorkingView       | 12-May-30             |             0.225806 |                      0   |                             0 |
| 868 | FI-Default                                | CurrentWorkingView       | 19-May-30             |             0.225806 |                      0   |                             0 |
| 869 | FI-Default                                | CurrentWorkingView       | 26-May-30             |             0.193548 |                      0   |                             0 |

---

## Recommendations

No specific recommendations at this time.

---

## Report Information

---

*Report generated by CSV Analysis Agent using EDA Utilities*


