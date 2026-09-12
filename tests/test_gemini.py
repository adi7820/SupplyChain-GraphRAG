import os
from unittest.mock import MagicMock, patch
import pytest
from src.llm.gemini_service import GeminiService


def test_gemini_missing_api_key(monkeypatch):
    """Test that GeminiService raises ValueError if no API key is provided."""
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)

    with pytest.raises(ValueError, match="Gemini API key is required"):
        GeminiService(api_key=None)


def test_gemini_empty_prompt():
    """Test that empty prompt raises ValueError."""
    with patch("google.generativeai.configure"), patch("google.generativeai.GenerativeModel"):
        service = GeminiService(api_key="test-mock-key")
        with pytest.raises(ValueError, match="Prompt must not be empty"):
            service.generate("   ")


def test_gemini_mocked_generation():
    """Test Gemini text generation using mocked response."""
    mock_response = MagicMock()
    mock_response.text = "GraphRAG enhances LLM reasoning by linking knowledge graph entities with vector retrieval."

    with patch("google.generativeai.configure") as mock_configure:
        with patch("google.generativeai.GenerativeModel") as mock_model_cls:
            mock_model_instance = MagicMock()
            mock_model_instance.generate_content.return_value = mock_response
            mock_model_cls.return_value = mock_model_instance

            service = GeminiService(api_key="test-mock-key", model_name="gemini-1.5-flash")
            mock_configure.assert_called_once_with(api_key="test-mock-key")
            mock_model_cls.assert_called_once_with("gemini-1.5-flash")

            result = service.generate("Explain SupplyChain GraphRAG")
            assert "GraphRAG enhances LLM reasoning" in result
            mock_model_instance.generate_content.assert_called_once_with("Explain SupplyChain GraphRAG")


def test_gemini_supply_chain_disruption_analysis():
    """Test Gemini prompt formatting and response for supply chain disruption."""
    mock_response = MagicMock()
    mock_response.text = "1. Operational Risk: High\n2. Bottlenecks: Tier-2 foundries\n3. Recommendations: Reroute via Rotterdam"

    with patch("google.generativeai.configure"):
        with patch("google.generativeai.GenerativeModel") as mock_model_cls:
            mock_model_instance = MagicMock()
            mock_model_instance.generate_content.return_value = mock_response
            mock_model_cls.return_value = mock_model_instance

            service = GeminiService(api_key="test-mock-key")
            analysis = service.analyze_supply_chain_disruption(
                event_name="Typhoon Singapore Closure",
                affected_entities=["PORT_SINGAPORE", "SUP_TSMC"],
                context="PORT_SINGAPORE -> SHIPS_VIA -> SUP_TSMC"
            )

            assert "Operational Risk: High" in analysis
            called_prompt = mock_model_instance.generate_content.call_args[0][0]
            assert "Typhoon Singapore Closure" in called_prompt
            assert "PORT_SINGAPORE" in called_prompt
            assert "PORT_SINGAPORE -> SHIPS_VIA -> SUP_TSMC" in called_prompt


@pytest.mark.skipif(
    not os.getenv("GEMINI_API_KEY") and not os.getenv("GOOGLE_API_KEY"),
    reason="GEMINI_API_KEY or GOOGLE_API_KEY environment variable not set for live API test"
)
def test_gemini_live_api():
    """Integration test with live Gemini API (only executes if API key is in environment)."""
    service = GeminiService()
    response = service.generate("Reply with 'OK' if you can read this message.")
    assert response is not None
    assert len(response.strip()) > 0
