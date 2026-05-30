import pandas as pd

try:
    # Load the CSV file from the input directory
    file_path = "generated_code/Input/Fact.BucketWeights11.csv"
    df = pd.read_csv(file_path)
    
    # Display basic info about the dataframe
    print("Dataset Shape:", df.shape)
    print("\nColumn Names:")
    print(df.columns.tolist())
    print("\n" + "="*50)
    
    # Count null values in each column
    null_counts = df.isnull().sum()
    
    # Display null count per column
    print("\nNull Values Count per Column:")
    print("-" * 40)
    for col in df.columns:
        print(f"{col}: {null_counts[col]}")
    
    # Calculate total null values across all columns
    total_nulls = null_counts.sum()
    
    print("\n" + "="*50)
    print(f"\nGRAND TOTAL NULL VALUES: {total_nulls}")
    
except FileNotFoundError:
    print(f"Error: File not found at {file_path}")
except Exception as e:
    print(f"An error occurred: {e}")