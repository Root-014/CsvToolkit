**Source File**: `Fact.BucketWeights11.csv`
**Rows**: 870 | **Columns**: 6
**Memory Usage**: 176.8 KB

## Columns & Data Types

| Column | Type | Notes |
|--------|------|-------|
| Forecast Iteration.[Forecast Iteration] | object | 1 unique (e.g. FI-Default) |
| Version.[Version Name] | object | 1 unique (e.g. CurrentWorkingView) |
| Time.[Partial Week] | object | time |
| Stat Bucket Weight | float64 | min=0.032258064516129, max=0.25, missing=0 |
| Stat Bucket Weight AUR | float64 | min=0.0, max=0.25, missing=0 |
| Stat Bucket Weight AUR Fcst | int64 | min=0, max=1, missing=0 |

## Time Columns

- **Time.[Partial Week]**: string/object (time-like) — 870 unique values
