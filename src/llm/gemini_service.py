import os
from typing import List, Optional
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()


class GeminiService:
    """Service to interact with Google Gemini models for Supply Chain GraphRAG analysis."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model_name: Optional[str] = None
    ):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        self.model_name = model_name or os.getenv("GEMINI_MODEL", "gemini-1.5-flash")

        if not self.api_key:
            raise ValueError(
                "Gemini API key is required. Set GEMINI_API_KEY or GOOGLE_API_KEY in your environment or .env file."
            )

        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(self.model_name)

    def generate(self, prompt: str) -> str:
        """Generate response from Gemini for a given prompt."""
        if not prompt or not prompt.strip():
            raise ValueError("Prompt must not be empty.")

        response = self.model.generate_content(prompt)
        if not response or not hasattr(response, "text"):
            return ""
        return response.text

    def analyze_supply_chain_disruption(
        self,
        event_name: str,
        affected_entities: List[str],
        context: Optional[str] = None
    ) -> str:
        """Specialized prompt for analyzing supply chain disruption impact."""
        prompt = (
            f"You are an expert supply chain risk and resilience analyst.\n\n"
            f"Disruption Event: {event_name}\n"
            f"Directly Affected Entities: {', '.join(affected_entities)}\n"
        )
        if context:
            prompt += f"Graph Context:\n{context}\n\n"
        prompt += (
            "Provide a concise impact assessment covering:\n"
            "1. Immediate operational risk to production\n"
            "2. Potential cascading bottlenecks in Tier-1 and Tier-2 suppliers\n"
            "3. Recommended mitigation actions\n"
        )
        return self.generate(prompt)
