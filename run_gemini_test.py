"""
Standalone runner script demonstrating Gemini model usage in SupplyChain-GraphRAG.
Usage:
    python run_gemini_test.py
"""

import os
import sys
from unittest.mock import MagicMock, patch
from dotenv import load_dotenv

load_dotenv()


def run_mock_demo():
    print("\n--- [Demo Mode: Mocked Gemini Test] ---")
    from src.llm.gemini_service import GeminiService

    mock_response = MagicMock()
    mock_response.text = (
        "### Gemini Supply Chain Impact Assessment\n"
        "- **Immediate Risk**: Critical bottleneck detected at Port of Singapore.\n"
        "- **Cascading Impact**: Tier-1 chip assembly delayed by 14 business days.\n"
        "- **Action Item**: Divert sea freight to Port of Tanjung Pelepas or air freight high-value SKUs."
    )

    with patch("google.generativeai.configure"), patch("google.generativeai.GenerativeModel") as mock_model:
        mock_instance = MagicMock()
        mock_instance.generate_content.return_value = mock_response
        mock_model.return_value = mock_instance

        service = GeminiService(api_key="mock-key-for-local-demo", model_name="gemini-1.5-flash")
        result = service.analyze_supply_chain_disruption(
            event_name="Port of Singapore Congestion",
            affected_entities=["PORT_SINGAPORE", "SUP_TSMC", "PROD_ALPHA_SMARTPHONE"],
            context="PROD_ALPHA_SMARTPHONE depends on PART_AI_CHIPSET supplied by SUP_TSMC shipping via PORT_SINGAPORE."
        )

        print(result)
        print("\nMocked Gemini test completed successfully!")


def run_live_test(api_key: str):
    print("\n--- [Live Mode: Calling Google Gemini API] ---")
    from src.llm.gemini_service import GeminiService

    model_name = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
    print(f"Connecting to model: {model_name}...")
    service = GeminiService(api_key=api_key, model_name=model_name)

    prompt = (
        "In 2 sentences, explain how a Graph-based Retrieval-Augmented Generation (GraphRAG) system "
        "improves supply chain vulnerability detection compared to standard vector search."
    )
    print(f"\nPrompt: {prompt}\n")
    response = service.generate(prompt)
    print("Gemini Response:\n" + "-" * 50)
    print(response)
    print("-" * 50)
    print("Live Gemini test completed successfully!")


if __name__ == "__main__":
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")

    if api_key:
        print("Found GEMINI_API_KEY / GOOGLE_API_KEY in environment or .env.")
        try:
            run_live_test(api_key)
        except Exception as e:
            print(f"Live call failed: {e}")
            print("Falling back to verified mock demonstration...")
            run_mock_demo()
    else:
        print("No GEMINI_API_KEY found in environment or .env.")
        print("Running mock demonstration test (add GEMINI_API_KEY to .env to run live).")
        run_mock_demo()
