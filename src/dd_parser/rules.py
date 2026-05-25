"""Deterministic integrity rules for schema validation and bridge health."""

import re
import pandas as pd
from typing import List, Tuple, Dict, Set

class IntegrityEngine:
    """Evaluates connectivity between the Data Dictionary and Physical Data Headers."""

    @staticmethod
    def normalize(s: str) -> str:
        """Aggressively reduces strings to alphanumeric lowercase for robust matching."""
        return re.sub(r'[^a-z0-9]', '', str(s).lower())

    @classmethod
    def evaluate_bridge(cls, dd_attributes: List[str], raw_headers: List[str]) -> Dict[str, List[str]]:
        """Categorizes attributes into Operational (Bucket A) and Orphans (Bucket B)."""
        raw_norm_map = {cls.normalize(h): h for h in raw_headers}
        
        operational = []
        orphans = []
        
        for attr in dd_attributes:
            attr_str = str(attr).strip()
            # Filter out NaN or empty strings (Step 1: Ingest Filtration)
            if not attr_str or attr_str.lower() == 'nan':
                continue
                
            if cls.normalize(attr_str) in raw_norm_map:
                operational.append(attr_str)
            else:
                orphans.append(attr_str)
                
        return {
            "operational": operational,
            "orphans": orphans,
            "ghosts": [h for h in raw_headers if cls.normalize(h) not in {cls.normalize(a) for a in dd_attributes}]
        }