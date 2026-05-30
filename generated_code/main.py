import pandas as pd
import os

try:
    # Define file path
    file_path = "generated_code/Input/Fact.BucketWeights11.csv"
    
    # Load the CSV file
    df = pd.read_csv(file_path)
    
    print("=" * 60)
    print("NULL VALUE ANALYSIS REPORT")
    print("=" * 60)
    print(f"\nFile: {file_path}")
    print(f"Total Rows: {len(df)}")
    print(f"Total Columns: {len(df.columns)}")
    print("\n" + "-" * 60)
    print("COLUMN NAMES:")
    print("-" * 60)
    for i, col in enumerate(df.columns):
        print(f"  {i}: {col}")
    
    print("\n" + "-" * 60)
    print("NULL COUNT PER COLUMN:")
    print("-" * 60)
    null_counts = df.isnull().sum()
    for col, count in null_counts.items():
        print(f"  {col}: {count} nulls")
    
    # Total nulls overall
    total_nulls = df.isnull().sum().sum()
    print(f"\n  TOTAL NULL VALUES IN DATASET: {total_nulls}")
    
    print("\n" + "-" * 60)
    print("ROWS WITH NULL VALUES:")
    print("-" * 60)
    
    # Get rows with null values
    rows_with_nulls = df[df.isnull().any(axis=1)]
    
    if len(rows_with_nulls) > 0:
        print(f"\nNumber of rows with at least one null: {len(rows_with_nulls)}")
        print("\nRow indices (0-based) with null values:")
        
        # Get null count per row
        null_count_per_row = df.isnull().sum(axis=1)
        rows_having_nulls = null_count_per_row[null_count_per_row > 0]
        
        print("\n  Row Index -> Null Count -> Columns with Nulls")
        print("  " + "-" * 55)
        
        for row_idx in rows_having_nulls.index:
            null_count = rows_having_nulls[row_idx]
            # Get column names with nulls for this row
            null_cols = df.columns[df.loc[row_idx].isnull()].tolist()
            null_cols_str = ", ".join(null_cols)
            print(f"  {row_idx:5d} -> {null_count:2d} null(s) -> {null_cols_str}")
    else:
        print("\n  No null values found in any row.")
    
    print("\n" + "-" * 60)
    print("SUMMARY STATISTICS:")
    print("-" * 60)
    print(f"  - Columns with nulls: {len(null_counts[null_counts > 0])}")
    print(f"  - Columns without nulls: {len(null_counts[null_counts == 0])}")
    print(f"  - Rows containing nulls: {len(rows_with_nulls)}")
    print(f"  - Percentage of rows with nulls: {(len(rows_with_nulls)/len(df))*100:.2f}%")
    
    print("\n" + "=" * 60)
    print("ANALYSIS COMPLETE")
    print("=" * 60)

except FileNotFoundError:
    print(f"ERROR: File not found at {file_path}")
except Exception as e:
    print(f"ERROR: {str(e)}")