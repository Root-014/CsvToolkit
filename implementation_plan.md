# Implementation Plan

## Objective
Validate that all sales domains from the ship_to file exist in the source customer file's CUSTOMER_NUMBER field, filtering only for records where ACTIVITY_SOURCE is not null.

---

## Data Sources

| File | Column | Description |
|------|--------|-------------|
| `generated_code/Input/Ship_Tos_copy (2).csv` | `Sales Domain.[Ship to]` | Sales domain values to validate |
| `generated_code/Input/Source_Customer (1).csv` | `CUSTOMER NUMBER` | Customer numbers to validate against |
| `generated_code/Input/Source_Customer (1).csv` | `ACTIVITY_SOURCE` | Filter condition - must be NOT NULL |

---

## Logic / Validation Steps

1. **Load Ship_To File:**
   - Read `Ship_Tos_copy (2).csv`
   - Extract unique values from column `Sales Domain.[Ship to]`

2. **Load Source Customer File:**
   - Read `Source_Customer (1).csv`
   - Filter rows where `ACTIVITY_SOURCE` is NOT NULL (exclude NaN/null values)
   - Extract unique `CUSTOMER NUMBER` values from filtered data

3. **Validation:**
   - Compare the two sets:
     - Identify sales domains from ship_to that are **missing** from source customer
     - Identify sales domains that **exist** in both

4. **Output:**
   - Generate a report showing:
     - Total count of sales domains in ship_to
     - Total count of active customers (with non-null ACTIVITY_SOURCE)
     - Count of sales domains found in source customer
     - Count of sales domains **NOT found** in source customer
     - List of missing sales domains (if any)

---

## Expected Output File
- Save results to: `generated_code/Output/sales_domain_validation_result.csv`

---

## Assumptions
- The "active source" field refers to `ACTIVITY_SOURCE` column in Source_Customer file
- "Not null" means excluding both NULL values and NaN/missing entries in ACTIVITY_SOURCE
- Sales domain values should be compared as exact string matches

---

## Open Questions
None - The metadata provided sufficient details to proceed with implementation.

---