"""CSV Analysis Agent

Uses EDA utilities to analyze CSV files and generate comprehensive reports.
"""

import pandas as pd
import os
from datetime import datetime
from eda_utils import (
    get_column_names,
    get_data_shape,
    get_data_types,
    get_data_info,
    get_missing_values,
    get_summary_stats,
    get_value_counts,
    display_head,
    display_tail,
    find_duplicates,
    get_categorical_summary,
    get_numeric_summary,
    get_time_summary,
    quick_eda
)
from .report_generator import MarkdownReportGenerator


class CSVAnalysisAgent:
    """Agent for analyzing CSV files using EDA utilities."""

    def __init__(self):
        """Initialize the CSV Analysis Agent."""
        self.data = None
        self.file_path = None
        self.analysis_results = {}

    def load_csv(self, file_path, **kwargs):
        """Load CSV or Parquet file into DataFrame.

        Args:
            file_path (str): Path to file
            **kwargs: Additional arguments to pass to pandas reader
        """
        try:
            if file_path.endswith('.parquet'):
                self.data = pd.read_parquet(file_path, **kwargs)
            else:
                self.data = pd.read_csv(file_path, **kwargs)
            
            self.file_path = file_path
            print(f"[OK] Successfully loaded data: {file_path}")
            print(f"  Shape: {self.data.shape}")
            return self.data
        except Exception as e:
            print(f"[ERROR] Error loading CSV: {e}")
            raise

    def analyze(self, detailed=True, progress_callback=None):
        """Perform comprehensive EDA on the CSV data.

        Args:
            detailed (bool): Whether to perform detailed analysis (default: True)
            progress_callback (callable): Optional callback for progress updates


        Returns:
            dict: Dictionary containing all analysis results
        """
        if self.data is None:
            raise ValueError("No data loaded. Please load a CSV file first.")

        print("\n" + "=" * 60)
        print("STARTING CSV ANALYSIS")
        print("=" * 60)

        self.analysis_results = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'file_path': self.file_path,
            'basic_info': {},
            'data_quality': {},
            'statistical_summary': {},
            'categorical_summary': {},
            'numeric_summary': {},
            'time_summary': {},
            'duplicates': {},
            'data_preview': {}
        }

        if progress_callback: progress_callback("[1/10] Getting basic information...")
        print("\n[1/10] Getting basic information...")
        self.analysis_results['basic_info'] = {
            'columns': get_column_names(self.data),
            'shape': get_data_shape(self.data),
            'total_rows': len(self.data),
            'total_columns': len(self.data.columns)
        }

        if progress_callback: progress_callback("[2/10] Analyzing data types...")
        print("[2/10] Analyzing data types...")
        self.analysis_results['data_types'] = get_data_types(self.data)

        if progress_callback: progress_callback("[3/10] Checking data quality...")
        print("[3/10] Checking data quality...")
        self.analysis_results['data_quality'] = {
            'missing_values': get_missing_values(self.data),
            'completeness': (1 - self.data.isnull().sum().sum() / (self.data.shape[0] * self.data.shape[1])) * 100
        }

        if progress_callback: progress_callback("[4/10] Generating statistical summary...")
        print("[4/10] Generating statistical summary...")
        self.analysis_results['statistical_summary'] = get_summary_stats(self.data)

        if progress_callback: progress_callback("[5/10] Analyzing categorical columns...")
        print("[5/10] Analyzing categorical columns...")
        self.analysis_results['categorical_summary'] = get_categorical_summary(self.data)

        if progress_callback: progress_callback("[6/10] Analyzing numeric columns...")
        print("[6/10] Analyzing numeric columns...")
        self.analysis_results['numeric_summary'] = get_numeric_summary(self.data)

        if progress_callback: progress_callback("[7/10] Detecting time columns...")
        print("[7/10] Detecting time columns...")
        self.analysis_results['time_summary'] = get_time_summary(self.data)

        if progress_callback: progress_callback("[8/10] Checking for duplicates...")
        print("[8/10] Checking for duplicates...")
        dup_count = find_duplicates(self.data).shape[0]
        self.analysis_results['duplicates'] = {
            'count': dup_count,
            'percentage': (dup_count / len(self.data)) * 100
        }

        if progress_callback: progress_callback("[9/10] Generating data preview...")
        print("[9/10] Generating data preview...")
        self.analysis_results['data_preview'] = {
            'head': display_head(self.data, 5),
            'tail': display_tail(self.data, 5)
        }

        if progress_callback: progress_callback("[10/10] Analysis complete!")
        print("[10/10] Analysis complete!")
        print("=" * 60)

        return self.analysis_results

    def get_column_analysis(self, column_name):
        """Analyze a specific column in detail.

        Args:
            column_name (str): Name of column to analyze

        Returns:
            dict: Column analysis results
        """
        if self.data is None:
            raise ValueError("No data loaded.")

        if column_name not in self.data.columns:
            raise ValueError(f"Column '{column_name}' not found in data.")

        col_data = self.data[column_name]
        dtype = str(col_data.dtype)

        analysis = {
            'name': column_name,
            'dtype': dtype,
            'null_count': col_data.isnull().sum(),
            'null_percentage': (col_data.isnull().sum() / len(col_data)) * 100,
            'unique_values': col_data.nunique(),
            'value_counts': get_value_counts(self.data, column_name)
        }

        if pd.api.types.is_numeric_dtype(col_data):
            analysis['stats'] = {
                'mean': col_data.mean(),
                'median': col_data.median(),
                'std': col_data.std(),
                'min': col_data.min(),
                'max': col_data.max()
            }
        else:
            analysis['most_frequent'] = col_data.mode().iloc[0] if not col_data.mode().empty else None

        return analysis


    def get_recommendations(self):
        """Generate data quality and analysis recommendations.

        Returns:
            list: List of recommendations
        """
        if not self.analysis_results:
            return ["Run analysis first using analyze() method"]

        recommendations = []

        # Check completeness
        if self.analysis_results['data_quality']['completeness'] < 95:
            recommendations.append(
                f"Data completeness is {self.analysis_results['data_quality']['completeness']:.1f}%. "
                "Consider handling missing values."
            )

        # Check duplicates
        dup_pct = self.analysis_results['duplicates']['percentage']
        if dup_pct > 0:
            recommendations.append(
                f"Found {self.analysis_results['duplicates']['count']} duplicate rows ({dup_pct:.1f}%). "
                "Consider removing duplicates."
            )

        # Check for time columns
        if self.analysis_results['time_summary']:
            recommendations.append(
                "Time columns detected. Consider temporal analysis and time-based features."
            )

        # Check categorical columns
        if self.analysis_results['categorical_summary']:
            cat_cols = list(self.analysis_results['categorical_summary'].keys())
            recommendations.append(
                f"Found {len(cat_cols)} categorical columns: {', '.join(cat_cols)}. "
                "Consider encoding for machine learning."
            )

        # Check numeric columns
        if self.analysis_results['numeric_summary']:
            num_cols = list(self.analysis_results['numeric_summary'].keys())
            recommendations.append(
                f"Found {len(num_cols)} numeric columns: {', '.join(num_cols)}. "
                "Consider correlation analysis and outlier detection."
            )

        return recommendations

    def generate_report(self, output_path=None, format='markdown'):
        """Generate analysis report.

        Args:
            output_path (str): Path to save the report (default: auto-generated)
            format (str): Report format - 'markdown' or 'json' (default: 'markdown')

        Returns:
            str: Path to generated report
        """
        if not self.analysis_results:
            self.analyze()

        if format == 'markdown':
            return self._generate_markdown_report(output_path)
        elif format == 'json':
            return self._generate_json_report(output_path)
        else:
            raise ValueError("Format must be 'markdown' or 'json'")

    def _generate_markdown_report(self, output_path=None):
        """Generate markdown report."""
        generator = MarkdownReportGenerator()
        if output_path is None:
            filename = os.path.basename(self.file_path).replace('.csv', '')
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_path = f"{filename}_analysis_{timestamp}.md"

        generator.generate_report(self.data, self.analysis_results, output_path)
        return output_path

    def _generate_json_report(self, output_path=None):
        """Generate JSON report."""
        import json

        if output_path is None:
            filename = os.path.basename(self.file_path).replace('.csv', '')
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_path = f"{filename}_analysis_{timestamp}.json"

        report_data = self.analysis_results.copy()

        # Convert DataFrames to dictionaries for JSON serialization
        for key, value in report_data.items():
            if isinstance(value, pd.DataFrame):
                report_data[key] = value.to_dict('records')
            elif isinstance(value, pd.Series):
                report_data[key] = value.to_dict()

        with open(output_path, 'w') as f:
            json.dump(report_data, f, indent=2, default=str)

        return output_path

    def summary(self):
        """Print a summary of the analysis."""
        if not self.analysis_results:
            print("No analysis results. Run analyze() first.")
            return

        print("\n" + "=" * 60)
        print("CSV ANALYSIS SUMMARY")
        print("=" * 60)
        print(f"File: {self.file_path}")
        print(f"Shape: {self.analysis_results['basic_info']['shape']}")
        print(f"Completeness: {self.analysis_results['data_quality']['completeness']:.1f}%")
        print(f"Duplicates: {self.analysis_results['duplicates']['count']} ({self.analysis_results['duplicates']['percentage']:.1f}%)")

        print("\nColumns:")
        for col in self.analysis_results['basic_info']['columns']:
            print(f"  - {col}")

        print("\nRecommendations:")
        for rec in self.get_recommendations():
            print(f"  - {rec}")

        print("=" * 60)