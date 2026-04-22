import pandas as pd

# Define the input file path
input_file_path = 'C:/Users/hariharan.balaji/Desktop/Personal/Codebase/Agents_openai revised/generated_code/Input/input.csv'

try:
    # Load the CSV file
    df = pd.read_csv(input_file_path)
    
    # Sort by 'Ensemble Fcst Weighted' column in descending order (highest values first)
    df_sorted = df.sort_values(by='Ensemble Fcst Weighted', ascending=False)
    
    # Retrieve the top 5 rows
    top_5_rows = df_sorted.head(5)
    
    # Display the result
    print("Top 5 rows based on highest 'Ensemble Fcst Weighted' values:")
    print(top_5_rows)
    
except FileNotFoundError:
    print(f"Error: File not found at {input_file_path}")
except Exception as e:
    print(f"An error occurred: {e}")