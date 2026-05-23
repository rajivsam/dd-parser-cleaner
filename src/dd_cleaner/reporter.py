"""Generates audit summaries and serializes transformation metadata handshakes."""

import json
import hashlib
import pandas as pd
from pathlib import Path


class CleaningReportManager:
    """Handles operational logging, metadata serialization, and integrity assertions."""

    def __init__(self, output_file_path: Path) -> None:
        """Binds the manager to the authoritative output location tracking target."""
        self.output_file_path = Path(output_file_path)

    def write_cleaned_dataset(self, df: pd.DataFrame) -> None:
        """Writes the scrubbed matrix table and constructs a sidecar audit file."""
        self.output_file_path.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(self.output_file_path, index=False)
        
        csv_bytes = df.to_csv(index=False).encode("utf-8")
        hash_sig = hashlib.sha256(csv_bytes).hexdigest()
        
        sidecar_path = self.output_file_path.with_suffix(".signature")
        audit_payload = {
            "sha256": hash_sig,
            "total_records_processed": len(df),
            "total_columns_scrubbed": len(df.columns)
        }
        
        with open(sidecar_path, "w", encoding="utf-8") as sf:
            sf.write(json.dumps(audit_payload, indent=2))
