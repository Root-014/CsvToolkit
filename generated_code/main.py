import pandas as pd

# Load the CSV file with the exact filepath provided
input_filepath = 'C:/Users/hariharan.balaji/Desktop/Personal/Codebase/Agents_openai revised/generated_code/Input/input.csv'

try:
    # Read the CSV file
    df = pd.read_csv(input_filepath)
    
    # Define column names
    item_col = 'Item.[Product Planning Level]'
    location_col = 'Location.[Country]'
    forecast_col = 'Ensemble Fcst Weighted'
    
    # Step 2: Find the item with maximum forecast
    # Group by item and sum the forecast values, then find the item with maximum total forecast
    item_forecast_sum = df.groupby(item_col)[forecast_col].sum()
    max_item = item_forecast_sum.idxmax()
    
    print(f"Item with Maximum Forecast: {max_item}")
    print(f"Total Forecast Value: {item_forecast_sum[max_item]}")
    print("-" * 50)
    
    # Step 3: Filter the dataframe to only rows matching the max forecast item
    filtered_df = df[df[item_col] == max_item]
    
    # Step 4: Extract unique locations for that item
    unique_locations = filtered_df[location_col].unique()
    
    # Step 5: Display results
    print(f"Unique Locations for '{max_item}':")
    print(unique_locations)
    print(f"\nTotal unique locations: {len(unique_locations)}")
    
except FileNotFoundError:
    print(f"Error: File not found at {input_filepath}")
except KeyError as e:
    print(f"Error: Column not found - {e}")
except Exception as e:
    print(f"An error occurred: {e}")