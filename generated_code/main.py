import pandas as pd
import numpy as np
import plotly.graph_objects as go
from statsmodels.tsa.holtwinters import ExponentialSmoothing
import warnings
warnings.filterwarnings('ignore')

# Define file path
file_path = 'C:/Users/hariharan.balaji/Desktop/Personal/Codebase/Agents_openai revised/generated_code/Input/input.csv'

try:
    # Step 1: Read the CSV
    df = pd.read_csv(file_path)
    print("CSV loaded successfully")
    print(f"Total records: {len(df)}")
    
    # Step 2: Parse the Time column
    df['Date'] = pd.to_datetime(df['Time.[Week]'], format='%d-%b-%y')
    df['YearMonth'] = df['Date'].dt.to_period('M')
    
    # Find the last month in the dataset
    last_month = df['YearMonth'].max()
    print(f"Last month in dataset: {last_month}")
    
    # Step 3: Filter data for last month and find top item
    last_month_df = df[df['YearMonth'] == last_month]
    
    # Aggregate actuals by item for last month
    item_actuals = last_month_df.groupby('Item.[Product Planning Level]')['Actual Cleansed'].sum()
    
    # Find the top item with highest actuals in last month
    top_item = item_actuals.idxmax()
    top_actual = item_actuals.max()
    print(f"Top item in last month ({last_month}): {top_item}")
    print(f"Actual value: {top_actual}")
    
    # Step 4: Aggregate data to monthly level for the top item
    item_df = df[df['Item.[Product Planning Level]'] == top_item].copy()
    monthly_data = item_df.groupby('YearMonth')['Actual Cleansed'].sum().reset_index()
    monthly_data['YearMonth'] = monthly_data['YearMonth'].dt.to_timestamp()
    monthly_data = monthly_data.sort_values('YearMonth').reset_index(drop=True)
    
    print(f"\nMonthly data for top item:")
    print(monthly_data)
    print(f"\nNumber of months: {len(monthly_data)}")
    
    # Step 5: Apply DES (Double Exponential Smoothing) - trend only, no seasonality
    des_model = ExponentialSmoothing(
        monthly_data['Actual Cleansed'],
        trend='add',
        seasonal=None,
        damped_trend=True
    )
    des_fit = des_model.fit(optimized=True)
    des_forecast = des_fit.forecast(12)
    
    # Apply TES (Triple Exponential Smoothing) - trend + seasonality
    # Need at least 2 seasons (24 months) for seasonal model, but let's try
    if len(monthly_data) >= 24:
        tes_model = ExponentialSmoothing(
            monthly_data['Actual Cleansed'],
            trend='add',
            seasonal='add',
            seasonal_periods=12
        )
        tes_fit = tes_model.fit(optimized=True)
        tes_forecast = tes_fit.forecast(12)
    else:
        # If not enough data, use additive seasonality with smaller period
        tes_model = ExponentialSmoothing(
            monthly_data['Actual Cleansed'],
            trend='add',
            seasonal='add',
            seasonal_periods=min(12, len(monthly_data) // 2)
        )
        tes_fit = tes_model.fit(optimized=True)
        tes_forecast = tes_fit.forecast(12)
    
    print("\nDES Forecast (12 months):")
    print(des_forecast)
    print("\nTES Forecast (12 months):")
    print(tes_forecast)
    
    # Step 6: Create forecast dates
    last_date = monthly_data['YearMonth'].max()
    forecast_dates = pd.date_range(start=last_date + pd.DateOffset(months=1), periods=12, freq='MS')
    
    # Step 7: Plot using Plotly
    fig = go.Figure()
    
    # Historical data
    fig.add_trace(go.Scatter(
        x=monthly_data['YearMonth'],
        y=monthly_data['Actual Cleansed'],
        mode='lines+markers',
        name='Historical',
        line=dict(color='#1f77b4', width=2),
        marker=dict(size=6)
    ))
    
    # DES Forecast
    fig.add_trace(go.Scatter(
        x=forecast_dates,
        y=des_forecast,
        mode='lines+markers',
        name='DES Forecast',
        line=dict(color='#ff7f0e', width=2, dash='dash'),
        marker=dict(size=6)
    ))
    
    # TES Forecast
    fig.add_trace(go.Scatter(
        x=forecast_dates,
        y=tes_forecast,
        mode='lines+markers',
        name='TES Forecast',
        line=dict(color='#2ca02c', width=2, dash='dot'),
        marker=dict(size=6)
    ))
    
    # Update layout
    fig.update_layout(
        title=f'Monthly Forecast for Top Item: {top_item}<br>(DES vs TES - 12 Month Forecast)',
        xaxis_title='Date',
        yaxis_title='Actual Cleansed',
        template='plotly_white',
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01
        ),
        hovermode='x unified'
    )
    
    # Save as HTML
    output_path = 'C:/Users/hariharan.balaji/Desktop/Personal/Codebase/Agents_openai revised/generated_code/Output/forecast_plot.html'
    fig.write_html(output_path)
    print(f"\nPlot saved to: {output_path}")
    
    # Display the plot
    fig.show()
    
    print("\n=== SUMMARY ===")
    print(f"Top Item: {top_item}")
    print(f"Last Month: {last_month}")
    print(f"DES Forecast values: {des_forecast.values}")
    print(f"TES Forecast values: {tes_forecast.values}")

except Exception as e:
    print(f"Error: {str(e)}")
    import traceback
    traceback.print_exc()