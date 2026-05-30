## Implementation Plan: Total Null Values Count

### Data Source
- **File**: `Fact.BucketWeights11.csv`
- **Location**: Input directory
- **Rows**: 870
- **Columns**: 6

### Context
The dataset contains the following columns:
1. `Forecast Iteration.[Forecast Iteration]` (object)
2. `Version.[Version Name]` (object)
3. `Time.[Partial Week]` (object)
4. `Stat Bucket Weight` (float64)
5. `Stat Bucket Weight AUR` (float64)
6. `Stat Bucket Weight AUR Fcst` (int64)

Note: The metadata indicates "missing=0" for all columns, suggesting no null values exist. However, the plan should verify this by performing the count.

### Objective
Count the total number of null (missing) values across all columns in the dataset.

### Implementation Steps

1. **Load the CSV file** from the input directory
2. **Count null values** in each column using pandas `.isnull().sum()`
3. **Calculate total** null values across all columns
4. **Output results** showing:
   - Null count per column
   - Total null count for the entire dataset

### Expected Output
A summary displaying null value counts for each column and the aggregate total.

---

## Open Questions

1. Should the output include null counts per column individually, or only the grand total?
2. Do you need this information exported to a file, or just displayed in the console?

---