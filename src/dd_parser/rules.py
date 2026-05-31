"""Deterministic integrity rules for schema validation and bridge health."""

import re
import pandas as pd
from typing import List, Dict

class IntegrityEngine:
    """Evaluates connectivity between the Data Dictionary and Physical Data Headers."""

    @staticmethod
    def normalize(s: str) -> str:
        """
        Aggressively reduces strings to alphanumeric lowercase for robust matching.

        Args:
            s (str): The input string to normalize.

        Returns:
            str: A normalized string containing only lowercase alphanumeric characters.
        """
        if not s or pd.isna(s):
            return ""
        return re.sub(r'[^a-z0-9]', '', str(s).lower())

    @classmethod
    def evaluate_bridge(cls, dd_attributes: List[str], raw_headers: List[str]) -> Dict[str, List[str]]:
        """
        Categorizes attributes into Operational (Bucket A), Orphans (Bucket B), and Ghosts (Bucket C).

        Args:
            dd_attributes (List[str]): List of attributes defined in the Data Dictionary.
            raw_headers (List[str]): List of column headers present in the raw data file.

        Returns:
            Dict[str, List[str]]: A dictionary containing lists for 'operational', 'orphans', and 'ghosts'.
        """
        raw_norm_map = {cls.normalize(h): h for h in raw_headers}
        dd_norm_set = {cls.normalize(str(a)) for a in dd_attributes}
        
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
            "ghosts": [h for h in raw_headers if cls.normalize(h) not in dd_norm_set]
        }