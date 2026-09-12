from unittest.mock import MagicMock, patch
from scripts.pr_reviewer import generate_fallback_review, review_diff


def test_fallback_review_generation():
    diff_text = (
        "diff --git a/test.py b/test.py\n"
        "--- a/test.py\n"
        "+++ b/test.py\n"
        "+print('hello world')\n"
        "-print('old world')\n"
    )
    review = generate_fallback_review(diff_text)
    assert "Automated Code Review Summary" in review
    assert "Lines Added" in review
    assert "Lines Deleted" in review
    assert "test.py" in review


def test_empty_diff_review():
    review = review_diff("")
    assert "No substantive code changes detected" in review


def test_gemini_review_invoked_when_key_present():
    mock_response = MagicMock()
    mock_response.text = "### 🤖 Gemini AI Code Review\n\nCode looks clean and modular."

    with patch("google.generativeai.configure"), patch("google.generativeai.GenerativeModel") as mock_model_cls:
        mock_instance = MagicMock()
        mock_instance.generate_content.return_value = mock_response
        mock_model_cls.return_value = mock_instance

        diff = "diff --git a/app.py b/app.py\n+def foo(): return 42"
        review = review_diff(diff, api_key="test-gemini-key")

        assert "Gemini AI Code Review" in review
        assert "Code looks clean and modular" in review
