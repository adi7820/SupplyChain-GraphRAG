"""
Automated PR Code Reviewer Script.
Reviews git diffs using Google Gemini (if API key available) or automated static checks,
and outputs a structured markdown review for posting as a PR comment.
"""

import argparse
import os
import sys
from typing import Optional


def get_supported_model(preferred_name: str = "gemini-1.5-flash") -> str:
    """Finds the best available model supporting generateContent from the API."""
    import google.generativeai as genai
    try:
        available = [
            m.name for m in genai.list_models()
            if "generateContent" in m.supported_generation_methods
        ]
        # Match candidate in model names (e.g. 'models/gemini-1.5-flash')
        for candidate in [preferred_name, "gemini-1.5-flash", "gemini-1.5-pro", "gemini-pro"]:
            for m in available:
                if candidate in m:
                    return m
        if available:
            return available[0]
    except Exception as e:
        print(f"Model listing fallback notice: {e}")
    return preferred_name


def generate_gemini_review(diff_text: str, api_key: str, model_name: str = "gemini-1.5-flash") -> str:
    """Uses Google Gemini model to review the code changes in the PR diff."""
    import google.generativeai as genai

    genai.configure(api_key=api_key)
    resolved_model = get_supported_model(model_name)
    model = genai.GenerativeModel(resolved_model)

    prompt = (
        "You are an expert senior software engineer and code reviewer.\n"
        "Please review the following Pull Request git diff and provide a thorough, constructive code review.\n\n"
        "Structure your review using the following markdown sections:\n"
        "### 🤖 Gemini AI Code Review\n\n"
        "#### 📌 Summary of Changes\n"
        "(Concise overview of what this PR introduces)\n\n"
        "#### 🔍 Code Quality & Best Practices\n"
        "(Observations on readability, patterns, modularity, naming)\n\n"
        "#### ⚠️ Potential Issues & Edge Cases\n"
        "(Any risks, bugs, unhandled errors, or security concerns)\n\n"
        "#### 💡 Recommendations\n"
        "(Concrete, actionable suggestions or test improvements)\n\n"
        "Here is the diff:\n"
        "```diff\n"
        f"{diff_text[:12000]}\n"
        "```"
    )

    response = model.generate_content(prompt)
    if response and hasattr(response, "text") and response.text:
        return response.text
    return "### 🤖 Gemini AI Code Review\n\n*Review completed, but no detailed suggestions were generated.*"


def generate_fallback_review(diff_text: str) -> str:
    """Generates automated structural review when Gemini API key is not configured."""
    lines = diff_text.splitlines()
    additions = sum(1 for line in lines if line.startswith("+") and not line.startswith("+++"))
    deletions = sum(1 for line in lines if line.startswith("-") and not line.startswith("---"))
    files_changed = [line[6:] for line in lines if line.startswith("diff --git")]

    file_list_md = "\n".join(f"- `{f.split()[-1]}`" for f in files_changed[:15]) if files_changed else "- *No modified files detected*"

    return (
        "### 🔍 Automated Code Review Summary\n\n"
        f"- **Files Modified**: {len(files_changed)}\n"
        f"- **Lines Added**: `+{additions}`\n"
        f"- **Lines Deleted**: `-{deletions}`\n\n"
        "#### 📁 Modified Files\n"
        f"{file_list_md}\n\n"
        "#### 📋 Automated Quality Checklist\n"
        "- [x] Diff extracted and inspected successfully\n"
        "- [ ] Ensure corresponding unit tests are included\n"
        "- [ ] Confirm secrets/credentials are not committed\n\n"
        "> [!TIP]\n"
        "> **Unlock Gemini AI Code Reviews**:\n"
        "> Add `GEMINI_API_KEY` under **GitHub Repository Settings > Secrets and variables > Actions** "
        "> to have Google Gemini automatically analyze every PR diff with detailed inline suggestions."
    )


def review_diff(diff_text: str, api_key: Optional[str] = None, model_name: Optional[str] = None) -> str:
    """Entry point to review diff either with Gemini or fallback static review."""
    key = api_key or os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    model = model_name or os.getenv("GEMINI_MODEL", "gemini-1.5-flash")

    if not diff_text or not diff_text.strip():
        return (
            "### 🔍 Automated Code Review\n\n"
            "*No substantive code changes detected in this pull request.*"
        )

    if key and key.strip() and not key.startswith("dummy"):
        try:
            return generate_gemini_review(diff_text=diff_text, api_key=key, model_name=model)
        except Exception as e:
            fallback = generate_fallback_review(diff_text)
            return (
                f"{fallback}\n\n"
                f"> [!WARNING]\n"
                f"> *Gemini review could not complete ({e}). Displaying fallback review.*"
            )

    return generate_fallback_review(diff_text)


def main():
    parser = argparse.ArgumentParser(description="Automated PR Code Reviewer")
    parser.add_argument("--diff-file", default="pr_diff.txt", help="Path to git diff file")
    parser.add_argument("--output-file", default="pr_review.md", help="Path to write markdown review")
    args = parser.parse_args()

    diff_content = ""
    if os.path.exists(args.diff_file):
        with open(args.diff_file, "r", encoding="utf-8", errors="replace") as f:
            diff_content = f.read()

    review_md = review_diff(diff_content)

    with open(args.output_file, "w", encoding="utf-8") as f:
        f.write(review_md)

    print(f"Code review written to {args.output_file}")


if __name__ == "__main__":
    main()
