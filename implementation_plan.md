## Implementation Plan

### Understanding the Request

The user wants to find:
1. **Which item has the most Stat Actual** - Sum of `Stat Actual` per item
2. **For that item, what is the MA fcst value** - Get `AUR Fcst Moving Average` for that item

### Data Specifications

| Source | File | Key Column | Value Column(s) |
|--------|------|------------|-----------------|
| Stat Actual | `Fact.DownloadResult5f91b9b7bbd54041ab2571a41c3de1c5.csv` | `Item.[Product Planning Level]` | `Stat Actual` |
| MA Forecast | `Fact.DownloadResultc047fe8aa2ef4774a1784d3e6eeea5de.csv` | `Item.[Product Planning Level]` | `AUR Fcst Moving Average` |

### Logic

1. **Load Stat Actual Data**: Read `Fact.DownloadResult5f91b9b7bbd54041ab2571a41c3de1c5.csv`
2. **Calculate Total Stat Actual per Item**: Sum `Stat Actual` grouped by `Item.[Product Planning Level]`
3. **Identify Item with Maximum Stat Actual**: Find the item with the highest total Stat Actual
4. **Load MA Forecast Data**: Read `Fact.DownloadResultc047fe8aa2ef4774a1784d3e6eeea5de.csv`
5. **Filter MA Data for Max Item**: Get rows where `Item.[Product Planning Level]` equals the max Stat Actual item
6. **Calculate Total MA Forecast**: Sum `AUR Fcst Moving Average` for that item
7. **Output Result**: Display item name, total Stat Actual, and total MA forecast

### Note on Input Path

The specified path `input.csv` does not match the available files. Based on the metadata:
- Use `Fact.DownloadResult5f91b9b7bbd54041ab2571a41c3de1c5.csv` for Stat Actual
- Use `Fact.DownloadResultc047fe8aa2ef4774a1784d3e6eeea5de.csv` for MA forecast

---

## Checklist

- [ ] Load Stat Actual data from `Fact.DownloadResult5f91b9b7bbd54041ab2571a41c3de1c5.csv`
- [ ] Calculate total Stat Actual per item (sum of `Stat Actual`)
- [ ] Identify item with maximum total Stat Actual
- [ ] Load MA forecast data from `Fact.DownloadResultc047fe8aa2ef4774a1784d3e6eeea5de.csv`
- [ ] Filter MA data to max Stat Actual item
- [ ] Calculate total MA forecast for that item (sum of `AUR Fcst Moving Average`)
- [ ] Display results (item name, total Stat Actual, total MA forecast)

---

**Please confirm if this interpretation is correct before proceeding with code generation.**

PLAN_GENERATED