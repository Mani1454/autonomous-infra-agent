import json
import re
from google import genai


class AIBrain:
    """
    AI-powered system health analyzer using Google Gemini.

    Uses the Gemini 2.0 Flash model to provide SRE-level diagnostics
    when system resource thresholds are exceeded.
    """

    def __init__(self, api_key: str) -> None:
        """
        Initializes the Gemini client with the provided API key.

        Args:
            api_key: A valid Google Gemini API key from Google AI Studio.
        """
        self.client = genai.Client(api_key=api_key)

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
            response = self.client.models.generate_content(
                model="gemini-2.0-flash",
                contents=prompt
            )
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
                    result = {
                        "diagnosis": raw,
                        "recommended_action": {"target_pid": None}
                    }

            # Validate and ensure schema integrity
            if "diagnosis" not in result:
                result["diagnosis"] = raw
            if "recommended_action" not in result:
                result["recommended_action"] = {"target_pid": None}
            if "target_pid" not in result["recommended_action"]:
                result["recommended_action"]["target_pid"] = None

            return result

        except Exception as e:
            error_msg = str(e)
            if "429" in error_msg or "quota" in error_msg.lower() or "rate" in error_msg.lower():
                friendly = (
                    "⚠️ Gemini API rate limit reached. "
                    "The free tier allows 15 requests/minute. "
                    "Analysis will resume automatically after the cooldown."
                )
            elif "403" in error_msg or "API_KEY" in error_msg.upper() or "invalid" in error_msg.lower():
                friendly = "❌ Invalid Gemini API key. Please check the key entered in the sidebar."
            else:
                friendly = f"⚠️ AI Analysis temporarily unavailable: {e}"

            return {
                "diagnosis": friendly,
                "recommended_action": {"target_pid": None}
            }