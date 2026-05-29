"""Module for ingesting domain documentation (PDF/SOPs) and generating Policy Manifests."""

import logging
import json
from pathlib import Path
from typing import Dict, Any
import httpx

class DocumentProcessor:
    """Orchestrates LLM-based extraction of rules from unstructured text documents."""

    def __init__(self, model_name: str = "llama3.2", prompts: Dict[str, Any] = None):
        self.logger = logging.getLogger(__name__)
        self.model_name = model_name
        self.prompts = prompts or {}
        self.system_prompt = self.prompts.get("system", 
            "You are a logic extraction engine. Your task is to read domain documentation (SOPs, narratives, or requirements) "
            "and extract thresholds, magic numbers, and validation rules into a strict JSON format.")
        self.discovery_template = self.prompts.get("discovery_template")

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

        # 2. Assemble Prompt (Reading Phase)
        prompt = self._assemble_discovery_prompt(content, dd_context)
        
        # 3. Execution and Processing Phase
        try:
            result = self._call_llm(prompt)
            return self._process_discovery_result(result)
        except Exception as e:
            self.logger.error(f"❌ Failed to extract policy manifest: {e}")
            return {}

    def _assemble_discovery_prompt(self, content: str, dd_context: str) -> str:
        """Handles prompt construction using templates from configuration."""
        narrative_snippet = content[:4000] if content else "No narrative documentation provided."
        dd_snippet = dd_context[:2000] if dd_context else "No data dictionary context provided."

        if self.discovery_template:
            return self.discovery_template.format(
                system_prompt=self.system_prompt,
                narrative_context=narrative_snippet,
                dd_context=dd_snippet
            )
        
        # Fallback to hardcoded template if config is missing or incomplete
        return f"""
        {self.system_prompt}

        TASK: Extract domain-specific logic and rules from the provided context. 

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
        {narrative_snippet}

        --- DATA DICTIONARY SUMMARY ---
        {dd_snippet}
        """

    def _process_discovery_result(self, result: str) -> Dict[str, Any]:
        """Handles cleaning and parsing of the LLM JSON response."""
        # Basic JSON cleanup in case the LLM includes markdown backticks
        if "```json" in result:
            result = result.split("```json")[1].split("```")[0]
        elif "```" in result:
            result = result.split("```")[1].split("```")[0]
        
        manifest = json.loads(result.strip())
        self.logger.info(f"✅ Successfully extracted manifest for domain: {manifest.get('metadata', {}).get('domain')}")
        return manifest

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