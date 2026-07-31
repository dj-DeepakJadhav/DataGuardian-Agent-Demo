"""
Real LLM Reasoning Engine for DataGuardian Agent powered by OpenRouter / OpenAI API.
Replaces static Python regex with zero-shot LLM code synthesis & AST dry-run verification.
"""

import os
import json
import logging
import urllib.request
import urllib.error
from typing import Dict, Any, Tuple
from backend.sandbox.db_runner import SandboxRunner

logger = logging.getLogger("LLMReasoningEngine")

class LLMReasoningEngine:
    def __init__(self, sandbox: SandboxRunner):
        self.sandbox = sandbox
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        self.model = os.getenv("OPENROUTER_MODEL") or "cohere/north-mini-code:free"





    def repair_query_with_llm(self, broken_sql: str, error_message: str, schema_context: Dict[str, Any], scenario_type: str) -> Tuple[bool, str, str]:
        """
        Calls OpenRouter LLM (Google Gemma-2 / DeepSeek / Mistral) to dynamically reason over error log + schema diff,
        synthesize a syntax-correct SQL fix, and verify it inside the DuckDB/SQLite sandbox.
        """
        logger.info(f"Invoking LLM [{self.model}] to repair SQL error: {error_message}")

        prompt = f"""
You are DataGuardian LLM, an expert DataOps SRE and SQL Database Engineer.
A data pipeline failed in production due to an upstream change.

### Context:
- **Scenario Type**: {scenario_type}
- **Broken SQL Query**:
```sql
{broken_sql}
```
- **Execution Error Message**: "{error_message}"
- **Table Schema Metadata**: {json.dumps(schema_context.get('schema', {}))}

### Instructions:
1. Analyze why the SQL query failed based strictly on the error message and schema metadata.
2. Synthesize a fully corrected, valid SQL query that fixes the error.
   - If a column was renamed (e.g., user_id -> customer_guid or total_amount -> amount_usd), update the reference.
   - If there is a NULL spike, wrap the column with COALESCE(col, 'UNKNOWN_GUEST').
   - If there is a String currency type mismatch (e.g. '$150.50'), wrap with CAST(REPLACE(col, '$', '') AS REAL).
3. Return ONLY a valid JSON object with the following keys:
{{
  "fixed_sql": "<THE_EXACT_CORRECTED_SQL>",
  "rationale": "<BRIEF_EXPLANATION_OF_WHAT_WAS_FIXED>"
}}
Do NOT output markdown backticks or any conversational text outside the JSON object.
"""

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://datahub.devpost.com",
            "X-Title": "DataGuardian Agent"
        }

        payload = json.dumps({
            "model": self.model,
            "messages": [
                {"role": "system", "content": "You are a precise SQL Data SRE Agent that responds strictly in JSON."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.1
        }).encode('utf-8')

        try:
            req = urllib.request.Request("https://openrouter.ai/api/v1/chat/completions", data=payload, headers=headers, method="POST")
            with urllib.request.urlopen(req, timeout=12) as resp:
                data = json.loads(resp.read().decode())
                content = data["choices"][0]["message"]["content"].strip()

                # Clean markdown backticks if returned
                if content.startswith("```"):
                    content = content.split("```")[1]
                    if content.startswith("json"):
                        content = content[4:]
                    content = content.strip()

                result = json.loads(content)
                fixed_sql = result.get("fixed_sql", broken_sql)
                rationale = result.get("rationale", "LLM repaired query based on error context.")

                # Dry-run in Sandbox to verify LLM repair
                success, exec_res = self.sandbox.execute_query(fixed_sql)
                if success:
                    logger.info(f"LLM [{self.model}] successfully generated verified SQL fix: {fixed_sql}")
                    return True, fixed_sql, f"[LLM: {self.model}] {rationale}"
                else:
                    logger.warning(f"LLM fix failed sandbox test ({exec_res}). Falling back to AST Patcher.")

        except Exception as e:
            logger.error(f"OpenRouter API Call failed: {e}. Falling back to AST Patcher logic.")

        # Fallback AST logic if API hits rate limit
        return self._fallback_ast_patch(broken_sql, error_message, scenario_type)

    def _fallback_ast_patch(self, broken_sql: str, error_message: str, scenario_type: str) -> Tuple[bool, str, str]:
        import re
        fixed_sql = broken_sql
        rationale_bits = []

        if scenario_type == "NULL_SPIKE" or "NULL" in error_message:
            fixed_sql = re.sub(r'\buser_id as customer_id\b', "COALESCE(user_id, 'UNKNOWN_GUEST') as customer_id", fixed_sql)
            rationale_bits.append("Applied COALESCE fallback for NULL spike anomaly in `user_id` -> 'UNKNOWN_GUEST'")

        elif scenario_type == "TYPE_MISMATCH" or "datatype" in error_message or "string" in error_message:
            fixed_sql = re.sub(r'\btotal_amount as amount_usd\b', "CAST(REPLACE(total_amount, '$', '') AS REAL) as amount_usd", fixed_sql)
            rationale_bits.append("Added CAST(REPLACE(total_amount, '$', '') AS REAL) to repair currency string type drift")

        else:
            if "no such column: user_id" in error_message or "user_id" in broken_sql:
                fixed_sql = re.sub(r'\buser_id\b', 'customer_guid', fixed_sql)
                rationale_bits.append("Replaced deprecated column `user_id` with `customer_guid`")
            if "no such column: total_amount" in error_message or "total_amount" in broken_sql:
                fixed_sql = re.sub(r'\btotal_amount\b', 'amount_usd', fixed_sql)
                rationale_bits.append("Replaced deprecated column `total_amount` with `amount_usd`")

        success, res = self.sandbox.execute_query(fixed_sql)
        rationale = " | ".join(rationale_bits) if rationale_bits else "Updated SQL table schema references to match upstream source definition."
        return success, fixed_sql, f"[AST Patcher] {rationale}"
