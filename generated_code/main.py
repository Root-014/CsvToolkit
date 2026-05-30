import pandas as pd

# Step 1: Load the CSV file
file_path = 'generated_code/Input/Fact.BucketWeights11.csv'

try:
    df = pd.read_csv(file_path)
except Exception as e:
    print(f"Error loading file: {e}")
    raise

# Display basic info about the dataset
print("=" * 60)
print("DATASET OVERVIEW")
print("=" * 60)
print(f"Total Rows: {len(df)}")
print(f"Total Columns: {len(df.columns)}")
print("\nColumn Names:")
for col in df.columns:
    print(f"  - {col}")

# Step 2: Detect null values in all columns
# Also consider empty strings as null values
df_clean = df.replace('', pd.NA)

# Count null values per column
null_counts = df_clean.isnull().sum()

print("\n" + "=" * 60)
print("NULL VALUES SUMMARY")
print("=" * 60)
print("\nNull Count per Column:")
for col, count in null_counts.items():
    print(f"  {col}: {count}")

# Total null count for entire dataset
total_nulls = df_clean.isnull().sum().sum()
print(f"\nTotal Null Values in Dataset: {total_nulls}")

# Step 3: Find row indices with null values
print("\n" + "=" * 60)
print("ROW INDICES WITH NULL VALUES")
print("=" * 60)

# Get rows with any null values
rows_with_nulls = df_clean[df_clean.isnull().any(axis=1)]

if len(rows_with_nulls) > 0:
    print(f"\nNumber of rows with at least one null value: {len(rows_with_nulls)}")
    print("\nRow indices with null values:")
    null_row_indices = rows_with_nulls.index.tolist()
    print(null_row_indices)
    
    # Show details of each row with nulls
    print("\n" + "-" * 60)
    print("DETAILED VIEW OF ROWS WITH NULL VALUES:")
    print("-" * 60)
    for idx in null_row_indices:
        print(f"\nRow Index: {idx}")
        for col in df.columns:
            if pd.isna(df_clean.loc[idx, col]):
                print(f"  {col}: NULL")
else:
    print("\nNo null values found in the dataset!")

print("\n" + "=" * 60)
print("COMPLETE")
print("=" * 60)