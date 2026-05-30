# Implementation Plan: Find All Null Values in Fact.BucketWeights11.csv

## Context
- **Data Source**: `Fact.BucketWeights11.csv`
- **File Path**: `generated_code/Input/Fact.BucketWeights11.csv`
- **Rows**: 870
- **Columns**: 6

## Dataset Structure

| Column Name | Data Type | Notes |
|-------------|-----------|-------|
| Forecast Iteration.[Forecast Iteration] | object | 1 unique value (FI-Default) |
| Version.[Version Name] | object | 1 unique value (CurrentWorkingView) |
| Time.[Partial Week] | object | Time column, 870 unique values |
| Stat Bucket Weight | float64 | Range: 0.032 - 0.25 |
| Stat Bucket Weight AUR | float64 | Range: 0.0 - 0.25 |
| Stat Bucket Weight AUR Fcst | int64 | Range: 0 - 1 |

## Objective
Identify and report all null (missing) values across all columns in the dataset.

## Implementation Steps

1. **Load the CSV file** from `generated_code/Input/Fact.BucketWeights11.csv`

2. **Detect null values** in all 6 columns using pandas `.isnull()` or `.isna()` method

3. **Generate summary report** containing:
   - Total null count per column
   - Total null count for entire dataset
   - List of row indices (if any) containing null values

4. **Output results** to a clear, readable format

## Expected Output Format
- Column-by-column null count
- Row indices with null values (if applicable)
- Total null value count

## Notes
- Consider both `None`, `NaN`, and empty string values as null
- All columns should be checked regardless of data type

---

****