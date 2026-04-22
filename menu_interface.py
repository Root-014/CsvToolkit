"""
Menu-Driven AutoGen CSV Analysis Interface
Easy-to-use menu system for interactive CSV analysis.
"""

import os
import sys
import pandas as pd
from pathlib import Path

# Try to import autogen
try:
    import autogen
    AUTOGEN_AVAILABLE = True
except ImportError:
    AUTOGEN_AVAILABLE = False
    print("[WARNING] AutoGen not installed. Install with: pip install autogen")


# ------------------------ Configuration ------------------------ #
config_list = {
    'model': 'minimax-m2:cloud',
    'base_url': 'http://localhost:11434/v1',
    'api_key': 'ollama',
    'api_type': 'openai',
}

CSV_FILE = 'Input/input.csv'
REPORT_FILE = 's.md'


# ------------------------ Utility Functions ------------------------ #

def load_csv():
    """Load CSV data."""
    try:
        df = pd.read_csv(CSV_FILE)
        return df
    except Exception as e:
        print(f"[ERROR] Failed to load CSV: {e}")
        return None


def show_csv_info(df):
    """Display basic CSV information."""
    print("\n" + "=" * 70)
    print("CSV DATA INFORMATION")
    print("=" * 70)
    print(f"File: {CSV_FILE}")
    print(f"Shape: {df.shape} (rows × columns)")
    print(f"\nColumns ({len(df.columns)}):")
    for i, col in enumerate(df.columns, 1):
        dtype = df[col].dtype
        non_null = df[col].count()
        print(f"  {i:2d}. {col:<40} | {str(dtype):<10} | {non_null}/{len(df)} non-null")
    print("=" * 70)


def run_basic_analysis():
    """Run basic analysis without LLM."""
    df = load_csv()
    if df is None:
        return

    print("\n" + "=" * 70)
    print("BASIC DATA ANALYSIS")
    print("=" * 70)

    # Basic info
    print("\n1. BASIC INFORMATION:")
    print(f"   - Total rows: {df.shape[0]:,}")
    print(f"   - Total columns: {df.shape[1]}")
    print(f"   - Memory usage: {df.memory_usage(deep=True).sum() / 1024:.2f} KB")

    # Numeric columns
    numeric_cols = df.select_dtypes(include=['number']).columns
    print(f"\n2. NUMERIC COLUMNS ({len(numeric_cols)}):")
    for col in numeric_cols:
        print(f"   - {col}")
        print(f"     Min: {df[col].min()}, Max: {df[col].max()}, Mean: {df[col].mean():.2f}")

    # Categorical columns
    cat_cols = df.select_dtypes(include=['object', 'category']).columns
    print(f"\n3. CATEGORICAL COLUMNS ({len(cat_cols)}):")
    for col in cat_cols:
        unique = df[col].nunique()
        print(f"   - {col}: {unique} unique values")

    # Missing values
    print(f"\n4. MISSING VALUES:")
    missing = df.isnull().sum()
    if missing.sum() > 0:
        for col, count in missing[missing > 0].items():
            pct = (count / len(df)) * 100
            print(f"   - {col}: {count} ({pct:.1f}%)")
    else:
        print("   No missing values found!")

    print("=" * 70)


def run_autogen_analysis():
    """Run AutoGen-powered analysis."""
    if not AUTOGEN_AVAILABLE:
        print("\n[ERROR] AutoGen is not installed.")
        print("Please install it with: pip install autogen")
        return

    # Import AutoGen components
    from autogen_simple import interactive_shell
    print("\n[OK] Starting AutoGen Interactive Shell...")
    interactive_shell()


# ------------------------ Menu System ------------------------ #

def show_main_menu():
    """Display the main menu."""
    print("\n" + "=" * 70)
    print("AUTOGEN CSV ANALYSIS - MAIN MENU")
    print("=" * 70)
    print("\n1. View CSV Information")
    print("2. Run Basic Analysis (no LLM)")
    print("3. Run Interactive Analysis (with LLM)")
    print("4. Show Example Requests")
    print("5. View Generated Code Directory")
    print("0. Exit")
    print("=" * 70)


def show_examples():
    """Show example analysis requests."""
    print("\n" + "=" * 70)
    print("EXAMPLE ANALYSIS REQUESTS")
    print("=" * 70)

    examples = {
        "Statistics": [
            "Show basic statistics for all numeric columns",
            "What is the mean and median of Location?",
            "Show summary statistics for forecast values"
        ],
        "Visualizations": [
            "Create a histogram for the Location column",
            "Show a bar chart of Channel distribution",
            "Create a box plot for numeric columns",
            "Generate a correlation heatmap"
        ],
        "Data Exploration": [
            "Show the first 10 rows of data",
            "Group data by Channel and show counts",
            "Find unique values in Demand Domain",
            "Show data types of all columns"
        ],
        "Filtering": [
            "Show rows where Location > 5000",
            "Filter data for a specific Channel",
            "Find rows with missing values"
        ],
        "Advanced": [
            "Find correlations between numeric columns",
            "Create a scatter plot of Location vs Forecast",
            "Show trends over time",
            "Group by Channel and calculate averages"
        ]
    }

    for category, reqs in examples.items():
        print(f"\n{category}:")
        for req in reqs:
            print(f"  • {req}")

    print("\n" + "=" * 70)
    print("\n[TIP] Use these examples when running the LLM-powered analysis!")


def view_generated_code():
    """View files in the generated code directory."""
    output_dir = 'generated_code'

    print(f"\n{'=' * 70}")
    print(f"GENERATED CODE DIRECTORY: {output_dir}")
    print("=" * 70)

    if not os.path.exists(output_dir):
        print(f"\n[INFO] Directory '{output_dir}' does not exist yet.")
        print("       Run an LLM-powered analysis to generate files.")
        return

    files = [f for f in os.listdir(output_dir) if os.path.isfile(os.path.join(output_dir, f))]

    if not files:
        print("\n[INFO] No files generated yet.")
        return

    print(f"\nFound {len(files)} file(s):\n")
    for i, f in enumerate(sorted(files), 1):
        size = os.path.getsize(os.path.join(output_dir, f))
        size_kb = size / 1024
        print(f"  {i}. {f:<30} ({size_kb:.2f} KB)")

    print("\n" + "=" * 70)


def main():
    """Main menu loop."""
    print("\n" + "=" * 70)
    print("AUTOGEN CSV ANALYSIS SYSTEM")
    print("=" * 70)
    print("\nWelcome! This system helps you analyze CSV data interactively.")
    print("\nFeatures:")
    print("  • View CSV structure and metadata")
    print("  • Run basic statistical analysis")
    print("  • Use LLM to generate custom analysis code")
    print("  • Create visualizations")
    print("  • Export results")

    # Check if CSV exists
    if not os.path.exists(CSV_FILE):
        print(f"\n[ERROR] CSV file not found: {CSV_FILE}")
        print("        Please place your CSV file in the Input/ directory.")
        return

    print(f"\n[OK] Found CSV file: {CSV_FILE}")

    # Check if markdown report exists
    if not os.path.exists(REPORT_FILE):
        print(f"[INFO] Markdown report not found: {REPORT_FILE}")
        print("       You can generate it by running: python main.py")
        print("       (Optional - system will work without it)")

    # Main menu loop
    while True:
        try:
            show_main_menu()
            choice = input("\nSelect an option (0-5): ").strip()

            if choice == '0':
                print("\n[OK] Goodbye!")
                break
            elif choice == '1':
                df = load_csv()
                if df is not None:
                    show_csv_info(df)
            elif choice == '2':
                run_basic_analysis()
            elif choice == '3':
                run_autogen_analysis()
            elif choice == '4':
                show_examples()
            elif choice == '5':
                view_generated_code()
            else:
                print("\n[ERROR] Invalid option. Please select 0-5.")

        except KeyboardInterrupt:
            print("\n\n[OK] Interrupted. Goodbye!")
            break
        except Exception as e:
            print(f"\n[ERROR] An error occurred: {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    main()