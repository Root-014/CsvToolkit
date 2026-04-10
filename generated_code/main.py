import pandas as pd
import plotly.graph_objects as go
import numpy as np
import os

# Define file path
input_file = 'C:/Users/hariharan.balaji/Desktop/Personal/Codebase/Agents_openai revised/generated_code/Input/input.csv'
output_folder = 'C:/Users/hariharan.balaji/Desktop/Personal/Codebase/Agents_openai revised/generated_code/Output'

# Create output folder if it doesn't exist
os.makedirs(output_folder, exist_ok=True)

try:
    # Read the CSV file
    df = pd.read_csv(input_file)
    
    # Display basic info
    print("CSV loaded successfully!")
    print(f"Shape: {df.shape}")
    print(f"Columns: {df.columns.tolist()}")
    
    # Extract year from Time column (format: "MMM-YY" e.g., "Jul-23")
    # The last 2 characters represent the year
    df['Year'] = '20' + df['Time.[Retail Planning Month]'].str[-2:]
    
    # Convert Year to integer for proper sorting
    df['Year'] = df['Year'].astype(int)
    
    print(f"\nUnique Years found: {sorted(df['Year'].unique())}")
    
    # Calculate yearly totals for both value columns
    # Using MFP_Geo_Net_Sls_Rtl_HS (Retail Sales) as the main contribution value
    # This is typically what "contribution" refers to in sales data
    
    yearly_totals = df.groupby('Year').agg({
        'MFP_Geo_Net_Sls_Unt_HS': 'sum',
        'MFP_Geo_Net_Sls_Rtl_HS': 'sum'
    }).reset_index()
    
    # Rename columns for clarity
    yearly_totals.columns = ['Year', 'Total_Units', 'Total_Retail_Sales']
    
    # Calculate percentages for retail sales
    total_contribution = yearly_totals['Total_Retail_Sales'].sum()
    yearly_totals['Percentage'] = (yearly_totals['Total_Retail_Sales'] / total_contribution * 100).round(2)
    
    # Format numbers with commas
    yearly_totals['Total_Retail_Sales_Formatted'] = yearly_totals['Total_Retail_Sales'].apply(lambda x: f"{x:,.0f}")
    yearly_totals['Total_Units_Formatted'] = yearly_totals['Total_Units'].apply(lambda x: f"{x:,.0f}")
    
    print("\n" + "="*70)
    print("YEARLY CONTRIBUTION TOTAL AND PERCENTAGE")
    print("="*70)
    print(yearly_totals[['Year', 'Total_Retail_Sales_Formatted', 'Percentage']].to_string(index=False))
    print("="*70)
    
    # Create visualization with both percentage and total actual value
    fig = go.Figure()
    
    # Add bar chart for Total Retail Sales
    fig.add_trace(go.Bar(
        x=yearly_totals['Year'],
        y=yearly_totals['Total_Retail_Sales'],
        name='Total Retail Sales',
        marker_color='#1f77b4',
        text=yearly_totals['Total_Retail_Sales_Formatted'],
        textposition='outside',
        texttemplate='%{text}',
        hovertemplate='<b>Year: %{x}</b><br>Total Sales: %{text}<br>Percentage: %{customdata}%<extra></extra>',
        customdata=yearly_totals['Percentage']
    ))
    
    # Add line chart for Percentage on secondary y-axis
    fig.add_trace(go.Scatter(
        x=yearly_totals['Year'],
        y=yearly_totals['Percentage'],
        name='Percentage (%)',
        mode='lines+markers+text',
        marker=dict(color='#ff7f0e', size=10),
        line=dict(color='#ff7f0e', width=2),
        text=yearly_totals['Percentage'].apply(lambda x: f"{x:.1f}%"),
        textposition='top center',
        hovertemplate='<b>Year: %{x}</b><br>Percentage: %{y:.2f}%<extra></extra>',
        yaxis='y2'
    ))
    
    # Update layout
    fig.update_layout(
        title={
            'text': 'Yearly Contribution: Total Sales and Percentage',
            'font': {'size': 20},
            'x': 0.5
        },
        xaxis=dict(
            title='Year',
            tickmode='linear',
            tick0=yearly_totals['Year'].min(),
            dtick=1
        ),
        yaxis=dict(
            title='Total Retail Sales',
            tickformat=',',
            showgrid=True,
            gridcolor='lightgray'
        ),
        yaxis2=dict(
            title='Percentage (%)',
            overlaying='y',
            side='right',
            tickformat='.1f',
            showgrid=False
        ),
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='center',
            x=0.5
        ),
        hovermode='x unified',
        template='plotly_white',
        height=600,
        width=1000,
        margin=dict(t=120, b=80)
    )
    
    # Save as HTML
    output_path = os.path.join(output_folder, 'yearly_contribution_chart.html')
    fig.write_html(output_path)
    print(f"\nChart saved to: {output_path}")
    
    # Display the plot
    fig.show()
    
    # Save summary table to CSV
    summary_path = os.path.join(output_folder, 'yearly_contribution_summary.csv')
    yearly_totals[['Year', 'Total_Retail_Sales', 'Percentage']].to_csv(summary_path, index=False)
    print(f"Summary table saved to: {summary_path}")
    
    # Print final summary
    print("\n" + "="*70)
    print("ANALYSIS COMPLETE")
    print("="*70)
    print(f"Total Years Analyzed: {len(yearly_totals)}")
    print(f"Year Range: {yearly_totals['Year'].min()} - {yearly_totals['Year'].max()}")
    print(f"Total Contribution (All Years): {total_contribution:,.0f}")
    
except FileNotFoundError:
    print(f"ERROR: File not found at {input_file}")
except Exception as e:
    print(f"ERROR: {str(e)}")
    import traceback
    traceback.print_exc()