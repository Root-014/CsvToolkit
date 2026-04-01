"""EDA Functions

Functions for metadata collection from pandas DataFrames.
Focus: Schema, structure, and data characteristics (NOT statistical analysis).
"""

import pandas as pd
import numpy as np
import re
from datetime import datetime


def _is_time_column(col, col_name):
    """Check if a column contains time-like data or has time-related name.

    Args:
        col (pd.Series): Column to check
        col_name (str): Name of the column

    Returns:
        tuple: (bool, str) - (is_time_column, format_description)
    """
    time_keywords = ['time', 'date', 'datetime', 'timestamp', 'clock']
    col_name_lower = str(col_name).lower()

    if any(keyword in col_name_lower for keyword in time_keywords):
        if pd.api.types.is_datetime64_any_dtype(col):
            return True, f"datetime64 (min: {col.min()}, max: {col.max()})"
        else:
            return True, f"Column name suggests time data ({', '.join([k for k in time_keywords if k in col_name_lower])})"

    if pd.api.types.is_datetime64_any_dtype(col):
        return True, f"datetime64 (min: {col.min()}, max: {col.max()})"

    if pd.api.types.is_object_dtype(col) or pd.api.types.is_string_dtype(col):
        sample = col.dropna().head(10)
        if len(sample) == 0:
            return False, None

        patterns = {
            r'\d{4}-\d{2}-\d{2}': 'YYYY-MM-DD',
            r'\d{2}-\d{2}-\d{4}': 'MM-DD-YYYY or DD-MM-YYYY',
            r'\d{4}/\d{2}/\d{2}': 'YYYY/MM/DD',
            r'\d{2}/\d{2}/\d{4}': 'MM/DD/YYYY or DD/MM/YYYY',
            r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}': 'YYYY-MM-DD HH:MM:SS',
            r'\d{2}-\d{2}-\d{4} \d{2}:\d{2}': 'MM-DD-YYYY HH:MM or DD-MM-YYYY HH:MM',
            r'\d{1,2}/\d{1,2}/\d{4} \d{1,2}:\d{2}': 'M/D/YYYY H:MM format',
            r'\d{2}:\d{2}:\d{2}': 'HH:MM:SS',
            r'\d{2}:\d{2}': 'HH:MM',
            r'\d{4}-\d{2}': 'YYYY-MM',
            r'\d{4}': 'YYYY'
        }

        first_val = str(sample.iloc[0])
        for pattern, format_desc in patterns.items():
            if re.match(pattern, first_val):
                return True, format_desc

    return False, None


def get_column_names(df):
    """Get list of column names from DataFrame.

    Args:
        df (pd.DataFrame): Input DataFrame

    Returns:
        list: List of column names
    """
    return df.columns.tolist()


def get_data_shape(df):
    """Get shape of DataFrame (rows, columns).

    Args:
        df (pd.DataFrame): Input DataFrame

    Returns:
        tuple: (number of rows, number of columns)
    """
    return df.shape


def get_data_types(df):
    """Get data types of all columns with time format detection.

    Args:
        df (pd.DataFrame): Input DataFrame

    Returns:
        pd.DataFrame: DataFrame with column names, data types, and time format info
    """
    result = pd.DataFrame({
        'column': df.columns,
        'dtype': df.dtypes,
        'is_time_column': [False] * len(df.columns),
        'time_format': [None] * len(df.columns)
    })

    for idx, col_name in enumerate(df.columns):
        is_time, time_format = _is_time_column(df[col_name], col_name)
        result.at[idx, 'is_time_column'] = is_time
        if is_time:
            result.at[idx, 'time_format'] = time_format

    return result


def get_data_info(df):
    """Get comprehensive info about DataFrame with time format detection.

    Args:
        df (pd.DataFrame): Input DataFrame

    Returns:
        dict: Dictionary containing shape, columns, dtypes, time formats, and memory usage
    """
    info = {
        'shape': df.shape,
        'columns': df.columns.tolist(),
        'dtypes': df.dtypes.to_dict(),
        'time_columns': {},
        'memory_usage': df.memory_usage(deep=True).sum(),
        'total_rows': len(df),
        'total_columns': len(df.columns)
    }

    for col_name in df.columns:
        is_time, time_format = _is_time_column(df[col_name], col_name)
        if is_time:
            info['time_columns'][col_name] = time_format

    return info


def get_missing_values(df):
    """Get count and percentage of missing values per column.

    Args:
        df (pd.DataFrame): Input DataFrame

    Returns:
        pd.DataFrame: DataFrame with missing value counts and percentages
    """
    missing_count = df.isnull().sum()
    missing_percent = (df.isnull().sum() / len(df)) * 100

    result = pd.DataFrame({
        'column': df.columns,
        'missing_count': missing_count.values,
        'missing_percentage': missing_percent.values
    })

    return result


def get_min_max_values(df):
    """Get min and max values for numeric columns only.

    Args:
        df (pd.DataFrame): Input DataFrame

    Returns:
        pd.DataFrame: Min and Max values for numeric columns
    """
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    if len(numeric_cols) == 0:
        return pd.DataFrame()

    result = pd.DataFrame({
        'column': numeric_cols,
        'min': [df[col].min() for col in numeric_cols],
        'max': [df[col].max() for col in numeric_cols]
    })

    return result


def get_summary_stats(df):
    """Get comprehensive statistical summary for numeric columns.

    Args:
        df (pd.DataFrame): Input DataFrame

    Returns:
        dict: Dictionary with statistical summary for numeric columns
    """
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    summary = {}

    for col in numeric_cols:
        summary[col] = {
            'count': df[col].count(),
            'missing_count': df[col].isnull().sum()
        }

    return summary


def get_value_counts(df, column, limit=5):
    """Get value counts for a specific column.

    Args:
        df (pd.DataFrame): Input DataFrame
        column (str): Column name to get value counts for
        limit (int): Maximum number of unique values to show (default: 5)

    Returns:
        pd.Series: Value counts for the column (limited to top 'limit' values)
    """
    return df[column].value_counts().head(limit)


def display_head(df, n=5):
    """Display first n rows of DataFrame.

    Args:
        df (pd.DataFrame): Input DataFrame
        n (int): Number of rows to display (default: 5)

    Returns:
        pd.DataFrame: First n rows of DataFrame
    """
    return df.head(n)


def display_tail(df, n=5):
    """Display last n rows of DataFrame.

    Args:
        df (pd.DataFrame): Input DataFrame
        n (int): Number of rows to display (default: 5)

    Returns:
        pd.DataFrame: Last n rows of DataFrame
    """
    return df.tail(n)


def find_duplicates(df):
    """Find duplicate rows in DataFrame.

    Args:
        df (pd.DataFrame): Input DataFrame

    Returns:
        pd.DataFrame: DataFrame containing duplicate rows
    """
    return df[df.duplicated()]


def get_categorical_summary(df):
    """Get summary for categorical columns.

    Args:
        df (pd.DataFrame): Input DataFrame

    Returns:
        dict: Dictionary with unique value counts for each categorical column
    """
    categorical_cols = df.select_dtypes(include=['object', 'category']).columns
    summary = {}

    for col in categorical_cols:
        summary[col] = {
            'unique_values': df[col].nunique(),
            'sample_values': df[col].dropna().unique()[:5].tolist()
        }

    return summary


def get_time_summary(df):
    """Get detailed summary for time-like columns.

    Args:
        df (pd.DataFrame): Input DataFrame

    Returns:
        dict: Dictionary with summary for each time column
    """
    time_cols = []
    for col_name in df.columns:
        is_time, _ = _is_time_column(df[col_name], col_name)
        if is_time:
            time_cols.append(col_name)

    summary = {}

    for col in time_cols:
        if pd.api.types.is_datetime64_any_dtype(df[col]):
            summary[col] = {
                'dtype': str(df[col].dtype),
                'min_date': df[col].min(),
                'max_date': df[col].max(),
                'date_range_days': (df[col].max() - df[col].min()).days,
                'unique_dates': df[col].nunique(),
                'missing_count': df[col].isnull().sum(),
                'format': 'datetime64'
            }
        else:
            summary[col] = {
                'dtype': str(df[col].dtype),
                'unique_values': df[col].nunique(),
                'sample_values': df[col].dropna().head(5).tolist(),
                'missing_count': df[col].isnull().sum(),
                'format': 'string/object (time-like)'
            }

    return summary


def get_numeric_summary(df):
    """Get summary for numeric columns (min, max, count only).

    Args:
        df (pd.DataFrame): Input DataFrame

    Returns:
        dict: Dictionary with basic info for each numeric column
    """
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    summary = {}

    for col in numeric_cols:
        summary[col] = {
            'count': df[col].count(),
            'min': df[col].min(),
            'max': df[col].max(),
            'missing_count': df[col].isnull().sum()
        }

    return summary


def quick_eda(df):
    """Run a quick metadata collection on DataFrame.

    Args:
        df (pd.DataFrame): Input DataFrame

    Returns:
        dict: Dictionary containing metadata information (NO statistical analysis)
    """
    return {
        'shape': get_data_shape(df),
        'columns': get_column_names(df),
        'data_types': get_data_types(df),
        'time_columns': get_time_summary(df),
        'missing_values': get_missing_values(df),
        'min_max': get_min_max_values(df),
        'duplicates': find_duplicates(df).shape[0]
    }