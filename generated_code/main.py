import pandas as pd

try:
    # Load the dataset
    df = pd.read_csv('generated_code/Input/Fact.BucketWeights11.csv')
    
    # Count null values per column
    null_counts_per_column = df.isnull().sum()
    
    # Calculate total null values across entire dataset
    total_null_count = df.isnull().sum().sum()
    
    # Display results
    print("Null Values Count Per Column:")
    print(null_counts_per_column)
    print("\n" + "="*50)
    print(f"Total Null Values in Dataset: {total_null_count}")
    
except FileNotFoundError:
    print("Error: File not found at specified path")
except Exception as e:
    print(f"Error occurred: {e}")