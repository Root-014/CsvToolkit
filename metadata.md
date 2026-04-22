# CSV Data Analysis Report

**Generated**: 2026-03-25 16:46:09

**Source File**: `Input/input.csv`

---

## Overview

- **Total Rows**: 144
- **Total Columns**: 11
- **Shape**: 144 × 11

---

## Data Structure

### Columns

| Column Name | Data Type |
|-------------|-----------|
| Version.[Version Name] | str |
| Item.[L3] | str |
| Account.[All Account] | str |
| PnL.[All PnL] | str |
| Region.[All Region] | str |
| Channel.[Planning Channel] | str |
| Location.[Location] | int64 |
| Demand Domain.[Demand Domain] | str |
| Post Game Cycle.[Cycle] | str |
| Time.[Planning Month] | str |
| Final_Merge Fcst_BaselineFcst_Baseline | int64 |

---

## Data Quality

**Completeness**: 100.00%

### Missing Values

[OK] No missing values found

---

## Data Types & Time Detection

| Column | Type | Is Time Column | Time Format |
|--------|------|----------------|-------------|
| Version.[Version Name] | str | No | - |
| Item.[L3] | str | No | - |
| Account.[All Account] | str | No | - |
| PnL.[All PnL] | str | No | - |
| Region.[All Region] | str | No | - |
| Channel.[Planning Channel] | str | No | - |
| Location.[Location] | int64 | No | - |
| Demand Domain.[Demand Domain] | str | No | - |
| Post Game Cycle.[Cycle] | str | No | - |
| Time.[Planning Month] | str | No | - |
| Final_Merge Fcst_BaselineFcst_Baseline | int64 | No | - |

---

## Statistical Summary

| Column | Count | Min | Max | Missing |
|--------|-------|-----|-----|---------|
| Location.[Location] | 144 | N/A | N/A | 0 |
| Final_Merge Fcst_BaselineFcst_Baseline | 144 | N/A | N/A | 0 |


---

## Categorical Columns Summary

### Version.[Version Name]

- **Unique Values**: 1
- **Sample Values**: CurrentWorkingView

### Item.[L3]

- **Unique Values**: 3
- **Sample Values**: 11113_03_01900, 11113_03_02300, 11113_03_02400

### Account.[All Account]

- **Unique Values**: 1
- **Sample Values**: All Account

### PnL.[All PnL]

- **Unique Values**: 1
- **Sample Values**: All Planning PnL

### Region.[All Region]

- **Unique Values**: 1
- **Sample Values**: All Planning Regions

### Channel.[Planning Channel]

- **Unique Values**: 2
- **Sample Values**: O9_L4_RET_BM_FP, O9_L4_RET_DI_FP

### Demand Domain.[Demand Domain]

- **Unique Values**: 2
- **Sample Values**: SU_2_23, FA_1_23

### Post Game Cycle.[Cycle]

- **Unique Values**: 1
- **Sample Values**: 27-Feb-23

### Time.[Planning Month]

- **Unique Values**: 24
- **Sample Values**: M01-24, M02-24, M03-23, M04-23, M05-23

---

## Numeric Columns Summary

### Location.[Location]

- **Count**: 144
- **Min**: 3474
- **Max**: 9686
- **Missing Count**: 0

### Final_Merge Fcst_BaselineFcst_Baseline

- **Count**: 144
- **Min**: 1
- **Max**: 2741
- **Missing Count**: 0

---

## Time Columns Summary

### Item.[L3]

- **Data Type**: str
- **Format**: string/object (time-like)
- **Sample Values**: ['11113_03_01900', '11113_03_01900', '11113_03_01900', '11113_03_01900', '11113_03_01900']
- **Missing Count**: 0

### Time.[Planning Month]

- **Data Type**: str
- **Format**: string/object (time-like)
- **Sample Values**: ['M01-24', 'M02-24', 'M03-23', 'M04-23', 'M05-23']
- **Missing Count**: 0

---

## Duplicate Analysis

- **Total Duplicate Rows**: 0
- **Percentage**: 0.00%

[OK] No duplicate rows found.

---

## Data Preview

### First 5 Rows

|    | Version.[Version Name]   |      Item.[L3] | Account.[All Account]   | PnL.[All PnL]    | Region.[All Region]   | Channel.[Planning Channel]   |   Location.[Location] | Demand Domain.[Demand Domain]   | Post Game Cycle.[Cycle]   | Time.[Planning Month]   |   Final_Merge Fcst_BaselineFcst_Baseline |
|---:|:-------------------------|---------------:|:------------------------|:-----------------|:----------------------|:-----------------------------|----------------------:|:--------------------------------|:--------------------------|:------------------------|-----------------------------------------:|
|  0 | CurrentWorkingView       | 11113_03_01900 | All Account             | All Planning PnL | All Planning Regions  | O9_L4_RET_BM_FP              |                  9686 | SU_2_23                         | 27-Feb-23                 | M01-24                  |                                        4 |
|  1 | CurrentWorkingView       | 11113_03_01900 | All Account             | All Planning PnL | All Planning Regions  | O9_L4_RET_BM_FP              |                  9686 | SU_2_23                         | 27-Feb-23                 | M02-24                  |                                        6 |
|  2 | CurrentWorkingView       | 11113_03_01900 | All Account             | All Planning PnL | All Planning Regions  | O9_L4_RET_BM_FP              |                  9686 | SU_2_23                         | 27-Feb-23                 | M03-23                  |                                       29 |
|  3 | CurrentWorkingView       | 11113_03_01900 | All Account             | All Planning PnL | All Planning Regions  | O9_L4_RET_BM_FP              |                  9686 | SU_2_23                         | 27-Feb-23                 | M04-23                  |                                        8 |
|  4 | CurrentWorkingView       | 11113_03_01900 | All Account             | All Planning PnL | All Planning Regions  | O9_L4_RET_BM_FP              |                  9686 | SU_2_23                         | 27-Feb-23                 | M05-23                  |                                        2 |

### Last 5 Rows

|     | Version.[Version Name]   |      Item.[L3] | Account.[All Account]   | PnL.[All PnL]    | Region.[All Region]   | Channel.[Planning Channel]   |   Location.[Location] | Demand Domain.[Demand Domain]   | Post Game Cycle.[Cycle]   | Time.[Planning Month]   |   Final_Merge Fcst_BaselineFcst_Baseline |
|----:|:-------------------------|---------------:|:------------------------|:-----------------|:----------------------|:-----------------------------|----------------------:|:--------------------------------|:--------------------------|:------------------------|-----------------------------------------:|
| 139 | CurrentWorkingView       | 11113_03_02400 | All Account             | All Planning PnL | All Planning Regions  | O9_L4_RET_DI_FP              |                  4729 | FA_1_23                         | 27-Feb-23                 | M08-24                  |                                        6 |
| 140 | CurrentWorkingView       | 11113_03_02400 | All Account             | All Planning PnL | All Planning Regions  | O9_L4_RET_DI_FP              |                  4729 | FA_1_23                         | 27-Feb-23                 | M09-24                  |                                        5 |
| 141 | CurrentWorkingView       | 11113_03_02400 | All Account             | All Planning PnL | All Planning Regions  | O9_L4_RET_DI_FP              |                  4729 | FA_1_23                         | 27-Feb-23                 | M10-24                  |                                       12 |
| 142 | CurrentWorkingView       | 11113_03_02400 | All Account             | All Planning PnL | All Planning Regions  | O9_L4_RET_DI_FP              |                  4729 | FA_1_23                         | 27-Feb-23                 | M11-24                  |                                       50 |
| 143 | CurrentWorkingView       | 11113_03_02400 | All Account             | All Planning PnL | All Planning Regions  | O9_L4_RET_DI_FP              |                  4729 | FA_1_23                         | 27-Feb-23                 | M12-24                  |                                       41 |

---

## Recommendations

No specific recommendations at this time.

---

## Report Information

---

*Report generated by CSV Analysis Agent using EDA Utilities*
