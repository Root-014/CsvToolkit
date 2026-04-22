"""
Quick Start Guide - AutoGen CSV Analysis System
Run this to see all available options and get started!
"""

import os
import sys

def print_header(title):
    """Print a formatted header."""
    print("\n" + "=" * 70)
    print(title.center(70))
    print("=" * 70)


def print_section(title, items):
    """Print a section with items."""
    print(f"\n{title}")
    print("-" * 70)
    for item in items:
        print(f"  • {item}")


def main():
    """Display quick start guide."""
    print_header("AUTOGEN CSV ANALYSIS SYSTEM - QUICK START")

    print("""
Welcome to the AutoGen CSV Analysis System!

This system allows you to interactively analyze CSV data using natural
language. Simply tell it what you want to analyze, and it will generate
and execute Python code for you!
""")

    print_section("QUICK START OPTIONS", [
        "1. Run menu interface (EASIEST) - python menu_interface.py",
        "2. Run simplified AutoGen - python autogen_simple.py",
        "3. Run advanced multi-agent - python advanced_autogen.py",
        "4. Run basic version - python autogen_main.py",
        "5. Run demo (non-interactive) - python demo_autogen.py"
    ])

    print_section("WHAT YOU CAN DO", [
        "Ask questions in plain English",
        "Generate statistical summaries",
        "Create visualizations (charts, plots, graphs)",
        "Filter and manipulate data",
        "Find correlations and patterns",
        "Export results to files",
        "All without writing code yourself!"
    ])

    print_section("EXAMPLE REQUESTS", [
        "\"Show basic statistics for all columns\"",
        "\"Create a histogram of Location values\"",
        "\"Find correlations between numeric columns\"",
        "\"Group data by Channel and show averages\"",
        "\"Show rows where Location > 5000\"",
        "\"Create a bar chart of forecast values\""
    ])

    print_section("FILES CREATED", [
        "menu_interface.py - Easy menu-driven interface (RECOMMENDED)",
        "autogen_simple.py - Simplified interactive system",
        "advanced_autogen.py - Multi-agent system with code review",
        "autogen_main.py - Basic two-agent setup",
        "demo_autogen.py - Demonstration with 4 examples",
        "AUTOGEN_README.md - Detailed documentation"
    ])

    print_section("REQUIREMENTS", [
        "CSV file: Input/input.csv ✓",
        "Markdown report: s.md ✓ (optional)",
        "Python packages: pandas, numpy, matplotlib, seaborn ✓",
        "AutoGen: pip install autogen ✓",
        "LLM service: Ollama/OpenAI/Anthropic ✓"
    ])

    print_header("RECOMMENDED: RUN MENU INTERFACE")
    print("""
The menu interface is the easiest way to get started:

    python menu_interface.py

It provides:
  1. View CSV information
  2. Run basic analysis (no LLM needed)
  3. Run interactive analysis (with LLM)
  4. See example requests
  5. View generated code

Just run it and follow the prompts!
""")

    # Check if files exist
    print_header("FILE STATUS CHECK")

    files_to_check = {
        'Input/input.csv': 'CSV data file',
        's.md': 'Markdown report',
        'menu_interface.py': 'Menu interface',
        'autogen_simple.py': 'Simplified AutoGen',
        'advanced_autogen.py': 'Advanced AutoGen'
    }

    all_exist = True
    for filepath, description in files_to_check.items():
        exists = os.path.exists(filepath)
        status = "✓" if exists else "✗"
        print(f"  {status} {filepath:<30} - {description}")
        if not exists:
            all_exist = False

    if not all_exist:
        print("\n[WARNING] Some files are missing!")

    print_header("READY TO START?")
    print("""
Choose your option:

OPTION A - Menu Interface (Easiest):
  > python menu_interface.py

OPTION B - Direct AutoGen (Advanced):
  > python autogen_simple.py

OPTION C - View Documentation:
  > cat AUTOGEN_README.md

Enjoy analyzing your data! 🚀
""")

    print("=" * 70)


if __name__ == "__main__":
    main()