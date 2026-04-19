import json
import re
import google.generativeai as genai


class AIBrain:
    """
    AI-powered system health analyzer using Google Gemini.

    Uses the Gemini Flash model to provide SRE-level diagnostics
    when system resource thresholds are exceeded.
    """

    def __init__(self, api_key: str) -> None:
        """
        Configures the Gemini API and initializes the Flash model.

        Args:
            api_key: A valid Google Gemini API key.
        """
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel("gemini-2.0-flash")

    def analyze_health(self, cpu_usage: float, mem_usage: float, top_processes: list) -> dict:
        """
        Sends system metrics to Gemini for root-cause analysis.

        Args:
            cpu_usage: Current CPU utilization percentage.
            mem_usage: Current memory utilization percentage.
            top_processes: List of dicts with 'PID', 'Name', 'CPU %' keys.

        Returns:
            A dict with keys 'diagnosis' (str) and 'recommended_action'
            (dict with 'target_pid' as int or None).
        """
        prompt = (
            f"You are a Senior SRE. "
            f"System Status: CPU {cpu_usage}%, RAM {mem_usage}%. "
            f"Top Processes: {top_processes}. "
            f"Analyze the root cause in 2 sentences. "
            f"Respond ONLY with a valid JSON object, no markdown, no extra text. "
            f"Use this exact schema: "
            f'{{"diagnosis": "<your 2-sentence analysis>", '
            f'"recommended_action": {{"target_pid": <integer PID of the rogue process or null>}}}}'
        )

        try:
            response = self.model.generate_content(prompt)
            raw = response.text.strip()

            # Try direct JSON parse first
            try:
                result = json.loads(raw)
            except json.JSONDecodeError:
                # Fallback: extract JSON from markdown code fences
                match = re.search(r'```(?:json)?\s*({.*?})\s*```', raw, re.DOTALL)
                if match:
                    result = json.loads(match.group(1))
                else:
                    # Last resort: return as plain diagnosis with no action
                    result = {
                        "diagnosis": raw,
                        "recommended_action": {"target_pid": None}
                    }

            # Validate structure
            if "diagnosis" not in result:
                result["diagnosis"] = raw
            if "recommended_action" not in result:
                result["recommended_action"] = {"target_pid": None}
            if "target_pid" not in result["recommended_action"]:
                result["recommended_action"]["target_pid"] = None

            return result

        except Exception as e:
            return {
                "diagnosis": f"⚠️ AI Analysis Failed: {e}",
                "recommended_action": {"target_pid": None}
            }






# import json
# import re
# import google.generativeai as genai

# class AIBrain:
#     """
#     AI-powered system health analyzer using Google Gemini.
#     """

#     def __init__(self, api_key: str) -> None:
#         """
#         Configures the Gemini API and initializes the Flash model.
#         """
#         genai.configure(api_key=api_key)
#         self.model = genai.GenerativeModel("gemini-2.0-flash")

#     def analyze_health(self, cpu_usage: float, mem_usage: float, top_processes: list) -> dict:
#         """
#         Sends system metrics to Gemini for root-cause analysis.
#         """
#         try:
#             # --- TEMPORARY MOCK FOR PHASE 3 TESTING ---
#             # This directly returns a hardcoded response to bypass the 429 Quota Error.
#             return {
#                 "diagnosis": "API is rate-limited, but simulated analysis shows Antigravity.exe is causing a memory leak.",
#                 "recommended_action": {
#                     "target_pid": 20392 
#                 }
#             }
            
#         except Exception as e:
#             return {
#                 "diagnosis": f"⚠️ AI Analysis Failed: {e}",
#                 "recommended_action": {"target_pid": None}
#             }