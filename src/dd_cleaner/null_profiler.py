"""Executes structural data profiling and quality metrics reporting on operational datasets."""

import pandas as pd
from pathlib import Path


class DatasetDataProfiler:
    """Computes column null metrics and outputs structured Markdown quality reports."""

    def __init__(self, output_report_path: Path) -> None:
        """Initializes the profiling component with its target path destination."""
        self.output_report_path = Path(output_report_path)

    def generate_null_quality_report(self, df: pd.DataFrame) -> Path:
        """Calculates null percentages for each column and serializes a Markdown report."""
        total_rows = len(df)
        
        # Ensure destination directory structure exists safely
        self.output_report_path.parent.mkdir(parents=True, exist_ok=True)
        
        markdown_lines = [
            "# 📊 Raw Dataset Quality Profiling Report",
            f"\n* **Total Records Analyzed:** {total_rows:,}",
            f"* **Total Column Fields:** {len(df.columns)}",
            "\n## 🔍 Column Missingness & Null Matrix\n",
            "| Column Name | Missing Records (Count) | Null Percentage (%) | Status Check |",
            "| :--- | :---: | :---: | :--- |"
        ]

        for col in df.columns:
            null_count = int(df[col].isnull().sum())
            null_pct = (null_count / total_rows * 100) if total_rows > 0 else 0.0
            
            # Context-aware alert status string
            if null_pct == 0:
                status = "🟩 Pristine (Complete)"
            elif null_pct < 5.0:
                status = "🟨 Low Warning"
            else:
                status = "🟥 High Missingness Alert"
                
            markdown_lines.append(
                f"| `{col}` | {null_count:,} | {null_pct:.2f}% | {status} |"
            )

        # Append execution trailer
        markdown_lines.append("\n\n*Report automatically compiled prior to cleaner scrub operations.*")

        # Write file cleanly to the authorized location
        with open(self.output_report_path, "w", encoding="utf-8") as f:
            f.write("\n".join(markdown_lines))

        return self.output_report_path
