# --- LLM PROMPT TEMPLATES (Directly copied from baseline config.yaml) ---
PROMPT_TEMPLATES = {
    "parser": {
        "prompts": {
            "entity_classifier": {
                "dataset_type_template": (
                    "Analyze this data dictionary snippet to determine the dataset's structural type.\n"
                    "Data: {sample_fields}\n\n"
                    "CRITERIA:\n"
                    "1. 'panel': Schema contains repeating attribute sets for different time periods in one row.\n"
                    "2. 'cross-sectional': Data represents a single snapshot. A single reference date column "
                    "(like 'asOfDate' or 'ReportDate') indicates a snapshot, NOT a panel.\n\n"
                    "Return a strict JSON object:\n"
                    "{{\"dataset_type\": \"cross-sectional\" | \"panel\"}}"
                ),
                "macro_domain_template": (
                    "You are a master data architect. Scan this snippet of a data dictionary blueprint:\n"
                    "{sample_fields}\n\n"
                    "Identify the macroscopic business domain (e.g., Banking, Healthcare, Insurance).\n"
                    "Then, generate a list of 4 to 6 coarse-grained logical entity concepts suited to house these attributes.\n\n"
                    "CRITICAL RULES:\n"
                    "1. DO NOT lump all attributes into a single catch-all category name.\n"
                    "2. Separate attributes by their intrinsic structural nature (e.g., distinguish between Demographics, "
                    "Risk Profiles, Financial metrics, and Spatial/Temporal metadata).\n"
                    "3. Make sure the entity concepts are granular enough to support target variations.\n\n"
                    "Return a strict JSON object with a single key 'logical_entities' containing a list of strings."
                ),
                "entity_discovery_template": (
                    "Classify this single data schema field:\n"
                    "Field Name: {attr_str}\n"
                    "Description: {desc_str}\n"
                    "Physical Data Profile (Grounding Context): {stats_str}\n\n"
                    "Instructions:\n"
                    "1. Select the best match for 'entity_assignment' from these discovered choices: [{hints_str}].\n"
                    "2. Evaluate dedicated boolean flags for these explicit semantic targets: {targets_str}.\n\n"
                    "Return a strict flat JSON object exactly like this example:\n"
                    "{{\"entity_assignment\": \"YourChoice\", \"is_geographic\": false}}"
                )
            },
            "document_processor": {
                "system": (
                    "You are a logic extraction engine. Your task is to read domain documentation (SOPs, narratives, "
                    "or requirements) and extract thresholds, magic numbers, and validation rules into a strict JSON format."
                ),
                "discovery_template": (
                    "{system_prompt}\n\n"
                    "TASK: Extract domain-specific logic and rules from the provided context.\n"
                    "You may receive a Narrative Document, a Data Dictionary summary, or both.\n\n"
                    "Output ONLY a JSON object that follows this structure:\n"
                    "{{\n"
                    "    \"metadata\": {{ \"domain\": \"string\", \"version\": \"string\", \"authority_source\": \"string\" }},\n"
                    "    \"constants\": {{ \"KEY\": value }},\n"
                    "    \"validation_rules\": [\n"
                    "        {{ \"rule_id\": \"string\", \"description\": \"string\", \"attribute\": \"string\",\n"
                    "           \"operator\": \"gt|lt|ge|le|eq|ne|in|between\", \"value\": any, \"action\": \"flag_warning|quarantine\" }}\n"
                    "    ]\n"
                    "}}\n\n"
                    "CONTEXT:\n"
                    "--- NARRATIVE DOCUMENT ---\n{narrative_context}\n\n"
                    "--- DATA DICTIONARY SUMMARY ---\n{dd_context}\n\n"
                    "Information to extract:\n"
                    "- Numerical thresholds, limits, or caps.\n"
                    "- Business rules requiring specific ratios or data constraints.\n"
                    "- Formatting constants. IMPORTANT: Use the following keys in the \"constants\" object:\n"
                    "    1. \"FORMATTING_PADDING\": A map of column name tokens to their required digit width (e.g., {{\"zip\": 5, \"id\": 10}}).\n"
                    "    2. \"FORMATTING_TITLE_CASE\": A list of column name tokens that should be title-cased (e.g., [\"name\", \"street\", \"city\"]).\n"
                    "- Other business-specific magic numbers should be at the root of the \"constants\" object."
                )
            }
        }
    },
    "cleaner": {
        "missing_values": {
            "prompts": {
                "cleaning_assistant": {
                    "system": (
                        "You are a data engineering assistant specializing in data quality. Analyze distributions "
                        "to provide cleaning recommendations."
                    ),
                    "recommendation_template": (
                        "Analyze the following dataset profile and provide cleaning recommendations in JSON:\n"
                        "{profile}"
                    )
                }
            }
        }
    }
}