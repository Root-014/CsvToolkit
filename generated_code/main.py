import duckdb
import pandas as pd

try:
    # Connect to DuckDB
    conn = duckdb.connect()
    
    # Load data from CSV
    query = """
    SELECT 
        "Location.[Country]" as location,
        "Time.[Retail Planning Month]" as time_period,
        "Stat Actual Amt" as actual,
        "Final Revenue Forecast" as forecast
    FROM read_csv('generated_code/Input/Rev_NA.csv')
    WHERE "Stat Actual Amt" IS NOT NULL 
      AND "Final Revenue Forecast" IS NOT NULL
    """
    
    df = conn.execute(query).df()
    
    print("Data loaded successfully!")
    print(f"Total rows after filtering NULL values: {len(df)}")
    print(f"\nSample data:")
    print(df.head())
    
    # Step 1: Aggregate at Location + Time Level
    location_time_agg = df.groupby(['location', 'time_period']).agg({
        'actual': 'sum',
        'forecast': 'sum'
    }).reset_index()
    
    location_time_agg.columns = ['location', 'time_period', 'sum_actual', 'sum_forecast']
    
    print(f"\n--- Step 1: Aggregated at Location + Time Level ---")
    print(f"Number of Location + Time combinations: {len(location_time_agg)}")
    print(location_time_agg.head())
    
    # Step 2: Calculate Absolute Errors for each Location + Time
    location_time_agg['abs_error'] = abs(location_time_agg['sum_actual'] - location_time_agg['sum_forecast'])
    
    print(f"\n--- Step 2: Calculated Absolute Errors ---")
    print(location_time_agg.head())
    
    # Step 3: Aggregate at Location Level
    location_agg = location_time_agg.groupby('location').agg({
        'sum_actual': 'sum',
        'sum_forecast': 'sum',
        'abs_error': 'sum'
    }).reset_index()
    
    location_agg.columns = ['Location', 'Total_Actual', 'Total_Forecast', 'Total_Abs_Error']
    
    print(f"\n--- Step 3: Aggregated at Location Level ---")
    print(location_agg)
    
    # Step 4: Calculate WMAPE
    location_agg['WMAPE'] = location_agg['Total_Abs_Error'] / location_agg['Total_Actual']
    location_agg['WMAPE_Pct'] = location_agg['WMAPE'] * 100
    
    # Handle division by zero (if Total_Actual is 0)
    location_agg['WMAPE'] = location_agg['WMAPE'].fillna(0)
    location_agg['WMAPE_Pct'] = location_agg['WMAPE_Pct'].fillna(0)
    
    print(f"\n--- Step 4: Final WMAPE Results at Location Level ---")
    print(location_agg)
    
    # Format output for display
    print("\n" + "="*80)
    print("FINAL OUTPUT: WMAPE at Location Level")
    print("="*80)
    
    final_output = location_agg.copy()
    final_output['Total_Actual'] = final_output['Total_Actual'].apply(lambda x: f"{x:,.2f}")
    final_output['Total_Forecast'] = final_output['Total_Forecast'].apply(lambda x: f"{x:,.2f}")
    final_output['Total_Abs_Error'] = final_output['Total_Abs_Error'].apply(lambda x: f"{x:,.2f}")
    final_output['WMAPE'] = final_output['WMAPE'].apply(lambda x: f"{x:.4f}")
    final_output['WMAPE_Pct'] = final_output['WMAPE_Pct'].apply(lambda x: f"{x:.2f}%")
    
    print(final_output.to_string(index=False))
    
    # Save results to CSV
    location_agg.to_csv('generated_code/Output/wmape_location_level.csv', index=False)
    print("\nResults saved to: generated_code/Output/wmape_location_level.csv")
    
    conn.close()
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()