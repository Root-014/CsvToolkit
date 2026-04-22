"""
Simplified AutoGen CSV Analysis System
A user-interactive agent that uses LLM to generate code for CSV analysis.
"""

import os
import sys
import pandas as pd
import json
from pathlib import Path
import autogen

# ------------------------ Configuration ------------------------ #
config_list = {
    'model': 'minimax-m2:cloud',
    'base_url': 'http://localhost:11434/v1',
    'api_key': 'ollama',
    'api_type': 'openai',
}

llm_config = {
    "config_list": [config_list],
    "temperature": 0.2,
    "max_tokens": 1500,
}

CSV_FILE = 'Input/input.csv'
OUTPUT_DIR = 'generated_code'

os.makedirs(OUTPUT_DIR, exist_ok=True)


# ------------------------ Data Context ------------------------ #
def get_data_context():
    """Load and prepare CSV context."""
    try:
        df = pd.read_csv(CSV_FILE)

        context = {
            'file': CSV_FILE,
            'shape': df.shape,
            'columns': df.columns.tolist(),
            'dtypes': {col: str(dtype) for col, dtype in df.dtypes.items()},
            'numeric_cols': df.select_dtypes(include=['number']).columns.tolist(),
            'categorical_cols': df.select_dtypes(include=['object', 'category']).columns.tolist(),
            'sample': df.head(3).to_dict('records'),
            'missing': df.isnull().sum().to_dict(),
        }

        return df, context
    except Exception as e:
        print(f"[ERROR] Failed to load CSV: {e}")
        return None, None


# ------------------------ Agent Setup ------------------------ #

# Coder Agent - generates and executes Python code
coder_agent = autogen.AssistantAgent(
    name="Coder",
    llm_config=llm_config,
    system_message="""You are a Python data analyst.

TASK: Generate Python code to analyze CSV data based on user requests.

REQUIREMENTS:
1. Write clean, well-commented Python code
2. Use pandas, numpy, matplotlib, seaborn as needed
3. Save code to files in the generated_code directory
4. Execute code when appropriate
5. Provide clear explanations

CONSTRAINTS:
- Load data from 'Input/input.csv' using pandas
- Handle errors gracefully
- Create output files with descriptive names
- Use English for all comments and print statements

When given a request, generate executable code that directly addresses it."""
)

# User Proxy - handles user interaction
user_proxy = autogen.UserProxyAgent(
    name="User",
    human_input_mode="ALWAYS",
    max_consecutive_auto_reply=3,
    code_execution_config={
        "work_dir": OUTPUT_DIR,
        "use_docker": False,
    },
    system_message="You are a helpful assistant that facilitates CSV data analysis."
)


# ------------------------ Analysis Functions ------------------------ #

def analyze_request(request, df, context):
    """Process a user request using the coder agent."""
    if not request.strip():
        print("[INFO] Please enter a valid request.")
        return

    print(f"\n[INFO] Processing request: {request}")
    print("-" * 60)

    # Prepare context message
    message = f"""
CSV Data Context:
- File: {context['file']}
- Shape: {context['shape']}
- Columns ({len(context['columns'])}): {', '.join(context['columns'][:5])}{'...' if len(context['columns']) > 5 else ''}
- Numeric columns: {', '.join(context['numeric_cols'])}
- Categorical columns: {', '.join(context['categorical_cols'])}

User Request: {request}

Generate and execute Python code to fulfill this request.
Save code to a file and execute it. Show results clearly.
"""

    try:
        # Initiate conversation with coder agent
        user_proxy.initiate_chat(
            coder_agent,
            message=message
        )
        print("-" * 60)
        print("[OK] Request processed successfully!")

    except Exception as e:
        print(f"[ERROR] Failed to process request: {e}")
        import traceback
        traceback.print_exc()


def interactive_shell():
    """Main interactive shell."""
    print("\n" + "=" * 70)
    print("AUTOGEN CSV ANALYSIS SHELL")
    print("=" * 70)

    # Load data
    df, context = get_data_context()

    if df is None:
        print("[ERROR] Cannot proceed without CSV data.")
        return

    print(f"\n[OK] Loaded: {CSV_FILE}")
    print(f"  Shape: {context['shape']}")
    print(f"  Columns: {len(context['columns'])}")
    print(f"  Numeric: {len(context['numeric_cols'])}")
    print(f"  Categorical: {len(context['categorical_cols'])}")

    print("\n" + "=" * 70)
    print("\nAvailable Commands:")
    print("  • 'exit' or 'quit' - Exit the program")
    print("  • 'help' - Show example requests")
    print("  • Any other text - Your analysis request")
    print("\n" + "=" * 70)

    # Interactive loop
    while True:
        try:
            print("\n" + "-" * 70)
            request = input("\n>>> Enter your request: ").strip()

            if request.lower() in ['exit', 'quit', 'q']:
                print("\n[OK] Goodbye!")
                break

            if request.lower() == 'help':
                show_help()
                continue

            if not request:
                print("[INFO] Please enter a request.")
                continue

            analyze_request(request, df, context)

            # Show generated files
            files = list_files_generated()
            if files:
                print(f"\n[OK] Files generated in '{OUTPUT_DIR}':")
                for f in files[:5]:
                    print(f"  - {f}")

        except KeyboardInterrupt:
            print("\n\n[OK] Interrupted. Goodbye!")
            break
        except Exception as e:
            print(f"\n[ERROR] Unexpected error: {e}")
            import traceback
            traceback.print_exc()


def show_help():
    """Show example requests."""
    print("\n" + "=" * 70)
    print("EXAMPLE ANALYSIS REQUESTS")
    print("=" * 70)

    examples = [
        "Show basic statistics for all numeric columns",
        "Create a histogram for the Location column",
        "Find correlations between numeric columns",
        "Group data by Channel and show summary",
        "Show top 10 values in the Demand Domain column",
        "Create a box plot for forecast values",
        "Find missing values in each column",
        "Show data types of all columns",
        "Export filtered data where Location > 5000",
        "Create a bar chart showing count by Channel"
    ]

    for i, example in enumerate(examples, 1):
        print(f"{i:2d}. {example}")

    print("=" * 70)


def list_files_generated():
    """List files in the output directory."""
    try:
        files = [f for f in os.listdir(OUTPUT_DIR) if os.path.isfile(os.path.join(OUTPUT_DIR, f))]
        return sorted(files)
    except:
        return []


if __name__ == "__main__":
    interactive_shell()