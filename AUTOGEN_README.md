# AutoGen CSV Analysis System

An intelligent, interactive CSV data analysis system powered by AutoGen and LLM.

## Overview

This system allows users to interactively analyze CSV data using natural language requests. It uses AutoGen agents to:
1. Understand user requests in plain English
2. Generate Python code automatically
3. Execute the code and show results
4. Learn from the CSV metadata for context-aware analysis

## System Architecture

### Components

1. **CoderAgent**: Generates and executes Python code for data analysis
2. **UserProxy**: Handles user interaction and coordinates the conversation
3. **Data Loader**: Loads CSV data and metadata for context

### Key Features

- **Natural Language Interface**: Ask questions in plain English
- **Automatic Code Generation**: LLM writes Python code based on your requests
- **Metadata-Aware**: Uses CSV metadata to understand data structure
- **Interactive Execution**: Run code and see results immediately
- **Multiple Output Formats**: Saves code, results, and visualizations

## Files

### Core System Files

1. **autogen_simple.py** - Simplified interactive system (Recommended)
   - Easy to use
   - Clear error handling
   - Interactive shell interface

2. **advanced_autogen.py** - Advanced multi-agent system
   - Multiple specialized agents (Coder, Analyst, Reviewer)
   - Group chat functionality
   - Code review and validation

3. **autogen_main.py** - Basic AutoGen implementation
   - Simple two-agent setup
   - Direct user-coder interaction

4. **demo_autogen.py** - Demonstration script
   - Shows 4 example analyses
   - Non-interactive demo

### Data Files

- **Input/input.csv** - Your CSV data file
- **s.md** - Markdown report with CSV metadata
- **generated_code/** - Directory for all generated code files

## Usage

### Quick Start

```bash
# Run the simplified interactive system
python autogen_simple.py

# Or run the advanced system
python advanced_autogen.py

# Run the demo
python demo_autogen.py
```

### Example Requests

Once the system is running, you can ask questions like:

```
# Statistics
Show basic statistics for all numeric columns
What is the mean of the Location column?

# Visualizations
Create a histogram for the Final_Merge column
Show a bar chart of Channel distribution
Create a correlation heatmap

# Data Exploration
Show me the first 10 rows
Group data by Channel and show summary
Find unique values in Demand Domain

# Filtering
Show rows where Location > 5000
Filter data for Channel = 'O9_L4_RET_BM_FP'

# Advanced Analysis
Find correlations between numeric columns
Show trends over time
Create a scatter plot of Location vs Forecast
```

## How It Works

### Step-by-Step Process

1. **Data Loading**
   - System loads your CSV from `Input/input.csv`
   - Generates metadata report if not exists
   - Prepares context about columns, types, and samples

2. **User Input**
   - You enter a request in natural language
   - System captures your intent

3. **Context Preparation**
   - CSV metadata is attached to your request
   - Column information, data types, and samples are included
   - LLM understands the data structure

4. **Code Generation**
   - CoderAgent generates Python code
   - Uses pandas, numpy, matplotlib, seaborn
   - Saves code to file in `generated_code/` directory

5. **Execution**
   - Code is executed automatically
   - Results are displayed
   - Files are saved for later review

6. **Iteration**
   - Ask follow-up questions
   - Build on previous results
   - Refine analysis

### Example Workflow

```
User: "Show me basic statistics for numeric columns"
↓
System: Generates code with df.describe() and df.info()
↓
Code: Saved as `numeric_stats.py` and executed
↓
Output: Statistics table displayed with explanation
↓
User: "Create a visualization of these statistics"
↓
System: Generates code for histograms and box plots
↓
Output: Charts saved and displayed
```

## Configuration

### LLM Configuration

Edit the config section in any of the Python files:

```python
config_list = {
    'model': 'minimax-m2:cloud',  # or 'gpt-4', 'claude-3', etc.
    'base_url': 'http://localhost:11434/v1',  # Your LLM endpoint
    'api_key': 'ollama',  # Your API key
    'api_type': 'openai',  # API type
}
```

### Parameters

Adjust these in `llm_config`:

- **temperature**: 0.0-1.0 (lower = more precise, higher = more creative)
- **max_tokens**: Maximum response length
- **timeout**: Code execution timeout (default: 60 seconds)

## Output Directory Structure

```
generated_code/
  ├── analysis_001.py        # Generated Python code
  ├── analysis_002.py
  ├── results_001.txt        # Output results
  ├── chart_001.png          # Generated visualizations
  └── ...
```

## Features

### What the System Can Do

✓ **Data Exploration**
- Load and inspect CSV files
- Show basic statistics
- Display data structure
- Identify data types

✓ **Statistical Analysis**
- Descriptive statistics
- Correlation analysis
- Groupby operations
- Aggregations

✓ **Visualizations**
- Histograms
- Box plots
- Bar charts
- Scatter plots
- Heatmaps
- Time series plots

✓ **Data Manipulation**
- Filtering rows
- Selecting columns
- Sorting data
- Grouping and aggregating
- Merging datasets

✓ **Export**
- Save results to CSV
- Export visualizations as PNG
- Write reports to text files
- Generate HTML summaries

### Safety Features

- **Error Handling**: Gracefully handles errors
- **Input Validation**: Validates file paths and data
- **Timeout Protection**: Prevents long-running code
- **Sandbox Execution**: Code runs in isolated directory

## Troubleshooting

### Common Issues

**Error: "Markdown report not found"**
- Run `python main.py` first to generate the report
- Or the system will work without it

**Error: "CSV file not found"**
- Ensure `Input/input.csv` exists
- Check file path is correct

**LLM Connection Error**
- Verify your LLM endpoint is running
- Check API key and base_url in config

**Unicode Errors**
- Use the simplified version (`autogen_simple.py`)
- Or set environment variable: `PYTHONIOENCODING=utf-8`

### Getting Help

If you encounter issues:

1. Check the error message
2. Verify CSV file exists and is readable
3. Ensure LLM service is running
4. Try running `python autogen_simple.py` for simpler interface

## Advanced Usage

### Custom Analysis

You can request complex analyses:

```
# Multi-step analysis
Analyze the correlation between Location and Forecast values,
then create a regression plot and show the R-squared value

# Custom transformations
Create a new column 'Location_Category' based on Location values
( <4000: Low, 4000-6000: Medium, >6000: High )

# Time series analysis
Group data by Planning Month and show trend of forecast values
```

### Batch Processing

For automated analysis:

```python
# In demo_autogen.py, modify the demo_requests list
demo_requests = [
    "Your request 1",
    "Your request 2",
    "Your request 3",
]
```

Then run:
```bash
python demo_autogen.py
```

## Requirements

- Python 3.7+
- pandas
- numpy
- matplotlib
- seaborn
- autogen
- LLM service (Ollama, OpenAI, Anthropic, etc.)

Install requirements:
```bash
pip install pandas numpy matplotlib seaborn autogen
```

## License

This system is provided as-is for educational and analysis purposes.

## Support

For issues or questions, check:
1. This README
2. Error messages in the console
3. Generated code files for reference
4. CSV metadata in `s.md`

---

**Happy Analyzing!** 📊✨