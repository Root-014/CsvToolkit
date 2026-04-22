"""
Demo: AutoGen CSV Analysis System
Demonstrates the system with a sample request.
"""

import os
import pandas as pd
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
    "temperature": 0.3,
    "max_tokens": 2000,
}

CSV_FILE = 'Input/input.csv'
OUTPUT_DIR = 'generated_code'

os.makedirs(OUTPUT_DIR, exist_ok=True)


# ------------------------ Load Data ------------------------ #
print("=" * 70)
print("AUTOGEN CSV ANALYSIS DEMO")
print("=" * 70)

try:
    df = pd.read_csv(CSV_FILE)
    print(f"\n[OK] Loaded CSV: {CSV_FILE}")
    print(f"  Shape: {df.shape}")
    print(f"  Columns: {list(df.columns)}")
except Exception as e:
    print(f"[ERROR] Failed to load CSV: {e}")
    exit(1)


# ------------------------ Create Agents ------------------------ #

# Coder Agent
coder_agent = autogen.AssistantAgent(
    name="CoderAgent",
    llm_config=llm_config,
    system_message="""You are an expert Python data analyst.

Your task:
1. Generate Python code to analyze the CSV data
2. Use pandas, matplotlib, seaborn for analysis and visualization
3. Save code to files and execute it
4. Provide clear explanations

CONSTRAINTS:
- Load data from 'Input/input.csv'
- Use pandas for data manipulation
- Create well-commented, executable code
- Save outputs with descriptive names"""

)

# User Proxy
user_proxy = autogen.UserProxyAgent(
    name="UserProxy",
    human_input_mode="NEVER",  # No human input for demo
    max_consecutive_auto_reply=1,
    code_execution_config={
        "work_dir": OUTPUT_DIR,
        "use_docker": False,
    },
)


# ------------------------ Demo Requests ------------------------ #

demo_requests = [
    "Show me the basic statistics of all numeric columns",
    "Create a visualization showing the distribution of Location values",
    "Find the correlation between numeric columns and create a heatmap",
    "Show a sample of the data grouped by Channel"
]

print(f"\n[DEMO] Running {len(demo_requests)} sample requests...\n")
print("=" * 70)

for i, request in enumerate(demo_requests, 1):
    print(f"\n\n{'=' * 70}")
    print(f"REQUEST {i}/{len(demo_requests)}: {request}")
    print('=' * 70)

    context = f"""
CSV CONTEXT:
- File: {CSV_FILE}
- Shape: {df.shape}
- Columns: {list(df.columns)}
- Numeric columns: {list(df.select_dtypes(include=['number']).columns)}
- Sample data:\n{df.head(3)}

REQUEST: {request}

Generate and execute Python code to fulfill this request.
"""

    try:
        user_proxy.initiate_chat(
            coder_agent,
            message=context
        )
        print(f"\n[OK] Request {i} completed!")
    except Exception as e:
        print(f"\n[ERROR] Request {i} failed: {e}")

print("\n" + "=" * 70)
print("DEMO COMPLETE")
print("=" * 70)
print(f"\n[OK] Check the '{OUTPUT_DIR}' directory for generated code files.")
print("\nTo run interactively, use:")
print("  python advanced_autogen.py")
print("=" * 70)