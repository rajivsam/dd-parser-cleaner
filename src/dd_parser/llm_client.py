"""Local LLM interaction abstraction for domain discovery classification."""

import json
import httpx
import pandas as pd
from typing import Dict, Any, List


class LLMEntityClassifier:
    """Manages Ollama API contexts and matches fallback heuristics semantically."""

    def __init__(self, global_config: Dict[str, Any], parser_config: Dict[str, Any]) -> None:
        """Hydrates runtime configurations for model routing queries."""
        self.update_config(global_config, parser_config)

    def update_config(self, global_config: Dict[str, Any], parser_config: Dict[str, Any]) -> None:
        """Dynamically refreshes active structural settings fields."""
        self.global_config = global_config
        self.parser_config = parser_config
        self.model_name = self.global_config.get("model_name", "llama3.2")
        self.system_prompt = self.global_config.get("system_prompt", "Respond strictly in JSON.")

    def discover_entities(
        self, attributes: pd.Series, descriptions: pd.Series, explicit_targets: List[str]
    ) -> Dict[str, Dict[str, Any]]:
        """Queries local Llama 3.2 model to group and semantically tag attributes dynamically."""
        assignments = {}
        schema_summary = [
            {"attribute": str(attr), "description": str(desc)} 
            for attr, desc in zip(attributes, descriptions)
        ]
        
        # Format the targets description for the prompt dynamically
        targets_str = ", ".join([f"'is_{t}' (boolean)" for t in explicit_targets])
            
        user_prompt = (
            f"Analyze these fields and group them into logical coarse-grained Domain Entities "
            f"(e.g., Borrower, Lender, Loan, Temporal, Bank, Location).\n"
            f"For each field, return an object containing:\n"
            f"1. 'entity_assignment': The coarse-grained domain string label.\n"
            f"2. Dedicated boolean flags for these explicit semantic targets: {targets_str}.\n\n"
            f"Return a single flat JSON object where the keys are the exact attribute names.\n"
            f"Example format:\n"
            f'{{"borrzip": {{"entity_assignment": "Borrower", "is_geographic": true}}}}\n\n'
            f"Fields to analyze:\n{json.dumps(schema_summary)}"
        )

        try:
            response = httpx.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": self.model_name,
                    "prompt": f"{self.system_prompt}\n\n{user_prompt}",
                    "stream": False,
                    "options": {"temperature": 0.0},
                    "format": "json"
                },
                timeout=30.0
            )
            if response.status_code == 200:
                raw_json = response.json().get("response", "{}")
                assignments = json.loads(raw_json)
        except Exception:
            # Fallback heuristic loop if local Ollama server is unreachable
            for attr in attributes:
                attr_lower = str(attr).lower()
                
                # Baseline guess mapping logic
                if "borr" in attr_lower: domain = "Borrower"
                elif "bank" in attr_lower: domain = "Bank"
                elif "lender" in attr_lower: domain = "Lender"
                elif "date" in attr_lower: domain = "Temporal"
                else: domain = "Loan"
                
                assignments[attr] = {"entity_assignment": domain}
                
                # Fallback primitive containment sweep for safety
                for target in explicit_targets:
                    is_match = False
                    if target == "geographic":
                        is_match = any(k in attr_lower for k in ["city", "zip", "state", "street", "address"])
                    assignments[attr][f"is_{target}"] = is_match
                
        return assignments
