"""Module for ingesting domain documentation (PDF/SOPs) and generating Policy Manifests."""

import logging
import json
from pathlib import Path
from typing import Dict, Any
import httpx

class DocumentProcessor:
    """Orchestrates LLM-based extraction of rules from unstructured text documents."""

    def __init__(self, model_name: str = "llama3.2"):
        self.logger = logging.getLogger(__name__)
        self.model_name = model_name
        self.system_prompt = (
            "You are a logic extraction engine. Your task is to read domain documentation (SOPs, narratives, or requirements) "
            "and extract thresholds, magic numbers, and validation rules into a strict JSON format."
        )

    def extract_policy_manifest(self, doc_path: Path = None, dd_context: str = "") -> Dict[str, Any]:
        """
        Ingests domain documentation and Data Dictionary context to produce a JSON manifest.
        Supports KMDS-style narrative-free discovery by relying on DD semantics.
        """
        content = ""
        if doc_path and doc_path.exists():
            if doc_path.suffix.lower() == ".pdf":
                self.logger.warning(f"⚠️ PDF detected: {doc_path.name}. Text extraction for PDFs requires additional dependencies. Skipping narrative content.")
            else:
                self.logger.info(f"📄 Processing narrative document: {doc_path}")
                content = doc_path.read_text(encoding="utf-8")
        else:
            self.logger.info("⚠️ No narrative documentation provided. Discovery limited to Data Dictionary context.")

        # 2. Build the extraction prompt
        prompt = f"""
        {self.system_prompt}

        TASK: Extract domain-specific logic and rules from the provided context. 
        You may receive a Narrative Document, a Data Dictionary summary, or both.

        Output ONLY a JSON object that follows this structure:
        {{
            "metadata": {{ "domain": "string", "version": "string", "authority_source": "string" }},
            "constants": {{ "KEY": value }},
            "validation_rules": [
                {{ "rule_id": "string", "description": "string", "attribute": "string", 
                   "operator": "gt|lt|ge|le|eq|ne|in|between", "value": any, "action": "flag_warning|quarantine" }}
            ]
        }}

        CONTEXT:
        --- NARRATIVE DOCUMENT ---
        {content[:4000] if content else "No narrative documentation provided."}

        --- DATA DICTIONARY SUMMARY ---
        {dd_context[:2000] if dd_context else "No data dictionary context provided."}

        Information to extract:
        - Numerical thresholds, limits, or caps.
        - Business rules requiring specific ratios or data constraints.
        - Formatting constants. IMPORTANT: Use the following keys in the "constants" object:
            1. "FORMATTING_PADDING": A map of column name tokens to their required digit width (e.g., {{"zip": 5, "id": 10}}).
            2. "FORMATTING_TITLE_CASE": A list of column name tokens that should be title-cased (e.g., ["name", "street", "city"]).
        - Other business-specific magic numbers should be at the root of the "constants" object.
        """
        # 3. Call Local LLM (Ollama implementation)
        try:
            result = self._call_llm(prompt)
            # Basic JSON cleanup in case the LLM includes markdown backticks
            if "```json" in result:
                result = result.split("```json")[1].split("```")[0]
            elif "```" in result:
                result = result.split("```")[1].split("```")[0]
            
            manifest = json.loads(result.strip())
            self.logger.info(f"✅ Successfully extracted manifest for domain: {manifest.get('metadata', {}).get('domain')}")
            return manifest
        except Exception as e:
            self.logger.error(f"❌ Failed to extract policy manifest: {e}")
            return {}

    def _call_llm(self, prompt: str) -> str:
        """Executes a local inference call via Ollama API (HTTP)."""
        response = httpx.post(
            "http://localhost:11434/api/generate",
            json={
                "model": self.model_name,
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": 0.0},
                "format": "json"
            },
            timeout=60.0
        )
        if response.status_code != 200:
            raise RuntimeError(f"Ollama API error: {response.text}")
        return response.json().get("response", "{}")