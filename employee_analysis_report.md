# CSV Data Analysis Report

**Generated**: 2026-03-25 11:44:15

**Source File**: `sample_employees.csv`

---

## Overview

- **Total Rows**: 15
- **Total Columns**: 8
- **Shape**: 15 × 8

---

## Data Structure

### Columns

| Column Name | Data Type |
|-------------|-----------|
| employee_id | int64 |
| name | str |
| department | str |
| salary | int64 |
| experience_years | int64 |
| hire_date | str |
| performance_score | float64 |
| location | str |

---

## Data Quality

**Completeness**: 100.00%

### Missing Values

[OK] No missing values found

---

## Data Types & Time Detection

| Column | Type | Is Time Column | Time Format |
|--------|------|----------------|-------------|
| employee_id | int64 | No | - |
| name | str | No | - |
| department | str | No | - |
| salary | int64 | No | - |
| experience_years | int64 | No | - |
| hire_date | str | No | - |
| performance_score | float64 | No | - |
| location | str | No | - |

---

## Statistical Summary

|       |   employee_id |   salary |   experience_years |   performance_score |
|:------|--------------:|---------:|-------------------:|--------------------:|
| count |      15       |     15   |           15       |           15        |
| mean  |     108       |  64133.3 |            3.86667 |            4.33333  |
| std   |       4.47214 |  10979.6 |            2.06559 |            0.394003 |
| min   |     101       |  50000   |            1       |            3.7      |
| 25%   |     104.5     |  54500   |            2       |            4.05     |
| 50%   |     108       |  62000   |            4       |            4.3      |
| 75%   |     111.5     |  76000   |            5.5     |            4.65     |
| max   |     115       |  80000   |            7       |            4.9      |

---

## Categorical Columns Summary

### name

- **Unique Values**: 15
- **Most Frequent**: Alice Johnson

**Top Values**:

| Value | Count |
|-------|-------|
| Alice Johnson | 1 |
| Bob Smith | 1 |
| Charlie Brown | 1 |
| Diana Prince | 1 |
| Edward Norton | 1 |

### department

- **Unique Values**: 3
- **Most Frequent**: HR

**Top Values**:

| Value | Count |
|-------|-------|
| Sales | 5 |
| IT | 5 |
| HR | 5 |

### hire_date

- **Unique Values**: 15
- **Most Frequent**: 2017-03-05

**Top Values**:

| Value | Count |
|-------|-------|
| 2022-01-15 | 1 |
| 2019-03-20 | 1 |
| 2021-06-10 | 1 |
| 2022-02-14 | 1 |
| 2017-11-05 | 1 |

### location

- **Unique Values**: 3
- **Most Frequent**: CA

**Top Values**:

| Value | Count |
|-------|-------|
| NY | 5 |
| CA | 5 |
| TX | 5 |

---

## Numeric Columns Summary

### employee_id

- **Count**: 15
- **Mean**: 108.00
- **Median**: 108.00
- **Std Dev**: 4.47
- **Min**: 101.00
- **Max**: 115.00
- **25th Percentile**: 104.50
- **75th Percentile**: 111.50
- **Missing Count**: 0

### salary

- **Count**: 15
- **Mean**: 64133.33
- **Median**: 62000.00
- **Std Dev**: 10979.63
- **Min**: 50000.00
- **Max**: 80000.00
- **25th Percentile**: 54500.00
- **75th Percentile**: 76000.00
- **Missing Count**: 0

### experience_years

- **Count**: 15
- **Mean**: 3.87
- **Median**: 4.00
- **Std Dev**: 2.07
- **Min**: 1.00
- **Max**: 7.00
- **25th Percentile**: 2.00
- **75th Percentile**: 5.50
- **Missing Count**: 0

### performance_score

- **Count**: 15
- **Mean**: 4.33
- **Median**: 4.30
- **Std Dev**: 0.39
- **Min**: 3.70
- **Max**: 4.90
- **25th Percentile**: 4.05
- **75th Percentile**: 4.65
- **Missing Count**: 0

---

## Time Columns Summary

### hire_date

- **Data Type**: str
- **Format**: string/object (time-like)
- **Sample Values**: ['2022-01-15', '2019-03-20', '2021-06-10', '2022-02-14', '2017-11-05']
- **Missing Count**: 0

---

## Duplicate Analysis

- **Total Duplicate Rows**: 0
- **Percentage**: 0.00%

[OK] No duplicate rows found.

---

## Data Preview

### First 5 Rows

|    |   employee_id | name          | department   |   salary |   experience_years | hire_date   |   performance_score | location   |
|---:|--------------:|:--------------|:-------------|---------:|-------------------:|:------------|--------------------:|:-----------|
|  0 |           101 | Alice Johnson | Sales        |    50000 |                  2 | 2022-01-15  |                 4.2 | NY         |
|  1 |           102 | Bob Smith     | IT           |    75000 |                  5 | 2019-03-20  |                 4.8 | CA         |
|  2 |           103 | Charlie Brown | HR           |    60000 |                  3 | 2021-06-10  |                 3.9 | TX         |
|  3 |           104 | Diana Prince  | Sales        |    55000 |                  2 | 2022-02-14  |                 4.5 | NY         |
|  4 |           105 | Edward Norton | IT           |    80000 |                  7 | 2017-11-05  |                 4.9 | CA         |

### Last 5 Rows

|    |   employee_id | name        | department   |   salary |   experience_years | hire_date   |   performance_score | location   |
|---:|--------------:|:------------|:-------------|---------:|-------------------:|:------------|--------------------:|:-----------|
| 10 |           111 | Kevin Hart  | IT           |    77000 |                  6 | 2018-04-18  |                 4.6 | CA         |
| 11 |           112 | Lisa Wong   | HR           |    63000 |                  4 | 2020-07-22  |                 4.2 | TX         |
| 12 |           113 | Mike Tyson  | Sales        |    51000 |                  1 | 2023-02-14  |                 3.8 | NY         |
| 13 |           114 | Nancy Drew  | IT           |    79000 |                  7 | 2017-03-05  |                 4.9 | CA         |
| 14 |           115 | Oscar Wilde | HR           |    65000 |                  5 | 2019-08-15  |                 4.4 | TX         |

---

## Correlation Analysis

### Correlation Matrix

|                   |   employee_id |   salary |   experience_years |   performance_score |
|:------------------|--------------:|---------:|-------------------:|--------------------:|
| employee_id       |          1.00 |     0.15 |               0.20 |                0.00 |
| salary            |          0.15 |     1.00 |               0.97 |                0.82 |
| experience_years  |          0.20 |     0.97 |               1.00 |                0.83 |
| performance_score |          0.00 |     0.82 |               0.83 |                1.00 |

### Top Correlations

| Column 1         | Column 2          |   Correlation |
|:-----------------|:------------------|--------------:|
| salary           | experience_years  |         0.968 |
| experience_years | performance_score |         0.831 |
| salary           | performance_score |         0.824 |
| employee_id      | experience_years  |         0.201 |
| employee_id      | salary            |         0.145 |
| employee_id      | performance_score |         0.004 |

---

## Recommendations

No specific recommendations at this time.

---

## Report Information

---

*Report generated by CSV Analysis Agent using EDA Utilities*
