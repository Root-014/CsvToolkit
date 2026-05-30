import os
import pandas as pd
from eda_utils import (
    get_data_info,
    get_missing_values,
    get_categorical_summary,
    get_numeric_summary,
    get_time_summary,
    quick_eda,
)


class MarkdownReportGenerator:
    def generate(self, file_path: str, analysis: dict) -> str:
        df_info = analysis.get("info", {})
        shape = df_info.get("shape", (0, 0))
        columns = df_info.get("columns", [])
        dtypes = df_info.get("dtypes", {})
        memory = df_info.get("memory_usage", 0)

        lines = [
            f"**Source File**: `{os.path.basename(file_path)}`",
            f"**Rows**: {shape[0]:,} | **Columns**: {shape[1]}",
            f"**Memory Usage**: {memory / 1024:.1f} KB",
            "",
            "## Columns & Data Types",
            "",
            "| Column | Type | Notes |",
            "|--------|------|-------|",
        ]

        time_cols = analysis.get("time_summary", {})
        numeric_cols = analysis.get("numeric_summary", {})
        categorical_cols = analysis.get("categorical_summary", {})

        for col in columns:
            dtype = str(dtypes.get(col, ""))
            notes = ""
            if col in time_cols:
                notes = "time"
            elif col in numeric_cols:
                info = numeric_cols[col]
                notes = f"min={info['min']}, max={info['max']}, missing={info['missing_count']}"
            elif col in categorical_cols:
                info = categorical_cols[col]
                samples = ", ".join(str(v) for v in info["sample_values"][:3])
                notes = f"{info['unique_values']} unique (e.g. {samples})"
            lines.append(f"| {col} | {dtype} | {notes} |")

        missing_df = analysis.get("missing_values")
        if missing_df is not None and not missing_df.empty:
            cols_with_missing = missing_df[missing_df["missing_count"] > 0]
            if not cols_with_missing.empty:
                lines += [
                    "",
                    "## Missing Values",
                    "",
                    "| Column | Missing Count | Missing % |",
                    "|--------|--------------|-----------|",
                ]
                for _, row in cols_with_missing.iterrows():
                    lines.append(
                        f"| {row['column']} | {int(row['missing_count'])} | {row['missing_percentage']:.1f}% |"
                    )

        if time_cols:
            lines += ["", "## Time Columns", ""]
            for col, info in time_cols.items():
                lines.append(f"- **{col}**: {info.get('format', '')} — {info.get('unique_values', info.get('unique_dates', ''))} unique values")

        lines.append("")
        return "\n".join(lines)


class CSVAnalysisAgent:
    def __init__(self):
        self._file_path = None
        self._df = None
        self._analysis = None
        self._report_gen = MarkdownReportGenerator()

    def load_csv(self, file_path: str):
        self._file_path = file_path
        ext = os.path.splitext(file_path)[1].lower()
        if ext == ".parquet":
            self._df = pd.read_parquet(file_path)
        else:
            self._df = pd.read_csv(file_path)

    def analyze(self, detailed: bool = True, progress_callback=None) -> dict:
        if self._df is None:
            raise RuntimeError("No file loaded. Call load_csv() first.")

        def _progress(msg):
            if progress_callback:
                progress_callback(msg)

        _progress("Collecting data info...")
        info = get_data_info(self._df)

        _progress("Checking missing values...")
        missing = get_missing_values(self._df)

        _progress("Analyzing numeric columns...")
        numeric = get_numeric_summary(self._df)

        _progress("Analyzing categorical columns...")
        categorical = get_categorical_summary(self._df)

        _progress("Analyzing time columns...")
        time = get_time_summary(self._df)

        self._analysis = {
            "info": info,
            "missing_values": missing,
            "numeric_summary": numeric,
            "categorical_summary": categorical,
            "time_summary": time,
        }

        _progress("Analysis complete.")
        return self._analysis

    def generate_report(self, output_path: str):
        if self._analysis is None:
            raise RuntimeError("No analysis available. Call analyze() first.")
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        report = self._report_gen.generate(self._file_path, self._analysis)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(report)
