## Implementation Plan: Find All Null Values in Fact.BucketWeights11.csv

### Context
Based on the provided metadata, the target file is `Fact.BucketWeights11.csv` with 870 rows and 6 columns.

### Data Source
- **File Path**: `Fact.BucketWeights11.csv`
- **Location**: Use the exact path where the file is stored

### Columns to Analyze
| Column Name | Type | Notes |
|-------------|------|-------|
| Forecast Iteration.[Forecast Iteration] | object | 1 unique |
| Version.[Version Name] | object | 1 unique |
| Time.[Partial Week] | object | time (870 unique values) |
| Stat Bucket Weight | float64 | min=0.032, max=0.25 |
| Stat Bucket Weight AUR | float64 | min=0.0, max=0.25 |
| Stat Bucket Weight AUR Fcst | int64 | min=0, max=1 |

### Implementation Steps
1. **Load the CSV file** `Fact.BucketWeights11.csv` into a pandas DataFrame
2. **Check each column** for null/missing values using:
   - `df.isnull().sum()` - count of null values per column
   - `df.isnull().sum(axis=1)` - count of null values per row
3. **Generate a report** containing:
   - Total null count per column
   - List of row indices with null values
   - Summary statistics of null value distribution

### Output Requirements
- Report the exact count of null values found in each column
- List specific row numbers (index) where null values are present
- Provide a clean summary of findings

---

****