"""Markdown Report Generator

Generates comprehensive markdown reports from CSV analysis results.
"""

import pandas as pd
import os


class MarkdownReportGenerator:
    """Generates markdown reports from analysis results."""

    def generate_report(self, data, analysis_results, output_path):
        """Generate comprehensive markdown report.

        Args:
            data (pd.DataFrame): Original DataFrame
            analysis_results (dict): Analysis results dictionary
            output_path (str): Path to save the markdown file
        """
        with open(output_path, 'w', encoding='utf-8') as f:
            self._write_header(f, analysis_results)
            self._write_overview(f, analysis_results)
            self._write_data_structure(f, data, analysis_results)
            self._write_data_quality(f, analysis_results)
            self._write_data_types(f, analysis_results)
            self._write_statistical_summary(f, analysis_results)
            self._write_categorical_summary(f, analysis_results)
            self._write_numeric_summary(f, analysis_results)
            self._write_time_summary(f, analysis_results)
            self._write_duplicates(f, analysis_results)
            self._write_data_preview(f, analysis_results)
            self._write_recommendations(f, analysis_results)
            self._write_footer(f)

        print(f"\n[OK] Markdown report generated: {output_path}")

    def _write_header(self, f, results):
        """Write report header."""
        f.write("# CSV Data Analysis Report\n\n")
        f.write(f"**Generated**: {results['timestamp']}\n\n")
        filename = os.path.basename(results['file_path'])
        f.write(f"**Source File**: `{filename}`\n\n")
        f.write("---\n\n")

    def _write_overview(self, f, results):
        """Write overview section."""
        f.write("## Overview\n\n")
        basic = results['basic_info']
        f.write(f"- **Total Rows**: {basic['total_rows']:,}\n")
        f.write(f"- **Total Columns**: {basic['total_columns']}\n")
        f.write(f"- **Shape**: {basic['shape'][0]:,} × {basic['shape'][1]}\n\n")
        f.write("---\n\n")

    def _write_data_structure(self, f, data, results):
        """Write data structure section."""
        f.write("## Data Structure\n\n")
        f.write("### Columns\n\n")
        f.write("| Column Name | Data Type |\n")
        f.write("|-------------|-----------|\n")

        for col in results['basic_info']['columns']:
            dtype = str(data[col].dtype)
            f.write(f"| {col} | {dtype} |\n")

        f.write("\n")
        f.write("---\n\n")

    def _write_data_quality(self, f, results):
        """Write data quality section."""
        f.write("## Data Quality\n\n")
        quality = results['data_quality']

        f.write(f"**Completeness**: {quality['completeness']:.2f}%\n\n")

        f.write("### Missing Values\n\n")
        missing_df = quality['missing_values']

        if missing_df['missing_count'].sum() > 0:
            f.write("| Column | Missing Count | Missing Percentage |\n")
            f.write("|--------|---------------|--------------------|\n")

            for _, row in missing_df.iterrows():
                if row['missing_count'] > 0:
                    f.write(f"| {row['column']} | {row['missing_count']} | {row['missing_percentage']:.2f}% |\n")
        else:
            f.write("[OK] No missing values found\n")

        f.write("\n")
        f.write("---\n\n")

    def _write_data_types(self, f, results):
        """Write data types section."""
        f.write("## Data Types & Time Detection\n\n")

        if 'data_types' in results:
            dt = results['data_types']

            f.write("| Column | Type | Is Time Column | Time Format |\n")
            f.write("|--------|------|----------------|-------------|\n")

            for _, row in dt.iterrows():
                if pd.notna(row['column']):
                    col = row['column']
                    dtype = str(row['dtype'])
                    is_time = "Yes" if row['is_time_column'] else "No"
                    time_fmt = row['time_format'] if row['time_format'] else "-"
                    f.write(f"| {col} | {dtype} | {is_time} | {time_fmt} |\n")

        f.write("\n")
        f.write("---\n\n")

    def _write_statistical_summary(self, f, results):
        """Write statistical summary section."""
        f.write("## Statistical Summary\n\n")

        if 'statistical_summary' in results and results['statistical_summary']:
            stats = results['statistical_summary']

            f.write("| Column | Count | Min | Max | Missing |\n")
            f.write("|--------|-------|-----|-----|---------|\n")

            for col, stat in stats.items():
                f.write(f"| {col} | {stat.get('count', 'N/A')} | {stat.get('min', 'N/A')} | {stat.get('max', 'N/A')} | {stat.get('missing_count', 'N/A')} |\n")

            f.write("\n\n")
        else:
            f.write("No numeric columns found for statistical summary.\n\n")

        f.write("---\n\n")

    def _write_categorical_summary(self, f, results):
        """Write categorical summary section."""
        f.write("## Categorical Columns Summary\n\n")

        if results['categorical_summary']:
            for col, summary in results['categorical_summary'].items():
                f.write(f"### {col}\n\n")
                f.write(f"- **Unique Values**: {summary['unique_values']}\n")
                f.write(f"- **Sample Values**: {', '.join(map(str, summary.get('sample_values', [])))}\n\n")
        else:
            f.write("No categorical columns found.\n\n")

        f.write("---\n\n")

    def _write_numeric_summary(self, f, results):
        """Write numeric summary section."""
        f.write("## Numeric Columns Summary\n\n")

        if results['numeric_summary']:
            for col, summary in results['numeric_summary'].items():
                f.write(f"### {col}\n\n")
                f.write(f"- **Count**: {summary['count']}\n")
                f.write(f"- **Min**: {summary['min']}\n")
                f.write(f"- **Max**: {summary['max']}\n")
                f.write(f"- **Missing Count**: {summary['missing_count']}\n\n")
        else:
            f.write("No numeric columns found.\n\n")

        f.write("---\n\n")

    def _write_time_summary(self, f, results):
        """Write time summary section."""
        f.write("## Time Columns Summary\n\n")

        if results['time_summary']:
            for col, summary in results['time_summary'].items():
                f.write(f"### {col}\n\n")
                f.write(f"- **Data Type**: {summary['dtype']}\n")
                f.write(f"- **Format**: {summary['format']}\n")

                if 'min_date' in summary:
                    f.write(f"- **Min Date**: {summary['min_date']}\n")
                    f.write(f"- **Max Date**: {summary['max_date']}\n")
                    f.write(f"- **Date Range (days)**: {summary['date_range_days']}\n")
                    f.write(f"- **Unique Dates**: {summary['unique_dates']}\n")

                if 'sample_values' in summary:
                    f.write(f"- **Sample Values**: {summary['sample_values']}\n")

                f.write(f"- **Missing Count**: {summary['missing_count']}\n\n")
        else:
            f.write("No time columns detected.\n\n")

        f.write("---\n\n")

    def _write_duplicates(self, f, results):
        """Write duplicates section."""
        f.write("## Duplicate Analysis\n\n")

        dup = results['duplicates']
        f.write(f"- **Total Duplicate Rows**: {dup['count']}\n")
        f.write(f"- **Percentage**: {dup['percentage']:.2f}%\n\n")

        if dup['count'] > 0:
            f.write("[WARNING] Duplicate rows found. Consider removing them for cleaner analysis.\n\n")
        else:
            f.write("[OK] No duplicate rows found.\n\n")

        f.write("---\n\n")

    def _write_data_preview(self, f, results):
        """Write data preview section."""
        f.write("## Data Preview\n\n")

        f.write("### First 5 Rows\n\n")
        head_df = results['data_preview']['head']
        f.write(head_df.to_markdown(index=True))
        f.write("\n\n")

        f.write("### Last 5 Rows\n\n")
        tail_df = results['data_preview']['tail']
        f.write(tail_df.to_markdown(index=True))
        f.write("\n\n")

        f.write("---\n\n")


    def _write_recommendations(self, f, results):
        """Write recommendations section."""
        f.write("## Recommendations\n\n")

        recommendations = results.get('recommendations', [])

        if recommendations:
            for i, rec in enumerate(recommendations, 1):
                f.write(f"{i}. {rec}\n\n")
        else:
            f.write("No specific recommendations at this time.\n\n")

        f.write("---\n\n")

    def _write_footer(self, f):
        """Write report footer."""
        f.write("## Report Information\n\n")
        f.write("---\n\n")
        f.write("*Report generated by CSV Analysis Agent using EDA Utilities*\n")