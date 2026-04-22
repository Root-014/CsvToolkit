"""
AutoGen CSV Analysis System
Interactive agent that learns from CSV metadata and generates code based on user requests.
"""

import os
import pandas as pd
from datetime import datetime
from pathlib import Path
import autogen

# ------------------------ Global declarations ------------------------ #
config_list = {
    'model': 'minimax-m2:cloud',
    'base_url': 'http://localhost:11434/v1',
    'api_key': 'ollama',
    'api_type': 'openai',
}

llm_config = {
    "config_list": [config_list],
    "temperature": 0.7,
    "max_tokens": 2000,
}

csv_file_path = 'Input/input.csv'
markdown_report_path = 's.md'
code_output_dir = 'generated_code'

# Create output directory
os.makedirs(code_output_dir, exist_ok=True)


# ------------------------ Load CSV Metadata ------------------------ #
def load_csv_metadata():
    """Load CSV metadata from the markdown report."""
    if not os.path.exists(markdown_report_path):
        print(f"[WARNING] Markdown report not found at {markdown_report_path}")
        return None

    with open(markdown_report_path, 'r', encoding='utf-8') as f:
        content = f.read()

    return content


def load_csv_data():
    """Load the actual CSV data."""
    try:
        data = pd.read_csv(csv_file_path)
        print(f"[OK] Loaded CSV: {csv_file_path}")
        print(f"  Shape: {data.shape}")
        return data
    except Exception as e:
        print(f"[ERROR] Failed to load CSV: {e}")
        return None


# ------------------------ Agent Definitions ------------------------ #

# Create the Coder Agent
coder_agent = autogen.AssistantAgent(
    name="CoderAgent",
    llm_config=llm_config,
    system_message="""You are an expert Python data analyst and programmer.

Your role:
1. Generate Python code based on user requests and CSV metadata
2. Use pandas, numpy, matplotlib, seaborn, and other data analysis libraries
3. Make the code executable and well-commented
4. Save code to files and execute when appropriate
5. Provide clear explanations of what the code does

When given a user request:
1. First, review the CSV metadata to understand the data structure
2. Generate Python code that addresses the request
3. Save the code to a file in the generated_code directory
4. Execute the code if it's safe to do so
5. Explain what was done and show results

Always be precise, helpful, and generate production-quality code.
"""
)

# Create the User Proxy Agent
user_proxy = autogen.UserProxyAgent(
    name="UserProxy",
    human_input_mode="ALWAYS",  # Always ask for user input
    max_consecutive_auto_reply=10,
    code_execution_config={
        "work_dir": code_output_dir,
        "use_docker": False,
    },
    system_message="""You are the User Proxy Agent.

Your responsibilities:
1. Take user input requests
2. Pass requests to the CoderAgent
3. Facilitate communication between user and CoderAgent
4. Ensure code is executed and results are shown to the user

When a user makes a request:
1. Acknowledge the request
2. Forward it to the CoderAgent with context about the CSV
3. Monitor execution and provide feedback
"""
)


# ------------------------ Main Execution Function ------------------------ #
def main():
    """Main execution function for the AutoGen CSV Analysis System."""

    print("\n" + "=" * 70)
    print("AUTOGEN CSV ANALYSIS SYSTEM")
    print("=" * 70)
    print("\nInitializing system...")

    # Load CSV metadata and data
    metadata = load_csv_metadata()
    csv_data = load_csv_data()

    if csv_data is None:
        print("[ERROR] Cannot proceed without CSV data")
        return

    print(f"\n[OK] System ready!")
    print(f"  - CSV File: {csv_file_path}")
    print(f"  - Markdown Report: {markdown_report_path}")
    print(f"  - Output Directory: {code_output_dir}")
    print("\n" + "=" * 70)
    print("\nYou can now ask me to:")
    print("  • Analyze specific columns")
    print("  • Create visualizations")
    print("  • Perform statistical tests")
    print("  • Generate summaries")
    print("  • Filter or transform data")
    print("  • Export results")
    print("\nType your request below (or 'exit' to quit):")
    print("=" * 70 + "\n")

    # Start the conversation
    while True:
        try:
            # Get user input
            user_input = input("\n>>> Your request: ")

            if user_input.lower() in ['exit', 'quit', 'q']:
                print("\n[OK] Goodbye!")
                break

            if not user_input.strip():
                print("[INFO] Please enter a valid request.")
                continue

            # Prepare context for the coder agent
            context = f"""
USER REQUEST: {user_input}

CSV FILE CONTEXT:
- File: {csv_file_path}
- Shape: {csv_data.shape}
- Columns: {', '.join(csv_data.columns.tolist())}
- Data Types: {dict(csv_data.dtypes)}

CSV METADATA (from markdown report):
{metadata[:2000] if metadata else 'No metadata available'}

INSTRUCTIONS:
1. Generate Python code to address this request
2. Use the CSV data loaded from '{csv_file_path}'
3. Make the code executable and well-documented
4. Save code to a file and execute it
5. Show results to the user

Please proceed with coding.
"""

            # Initiate the conversation
            user_proxy.initiate_chat(
                coder_agent,
                message=context
            )

        except KeyboardInterrupt:
            print("\n\n[OK] Goodbye!")
            break
        except Exception as e:
            print(f"\n[ERROR] An error occurred: {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    main()