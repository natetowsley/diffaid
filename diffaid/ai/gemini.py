import os
import json
import google.generativeai as genai
from diffaid.ai.base import ReviewEngine
from diffaid.models import ReviewResult

# Gemini Prompt
PROMPT = """
You are an automated code review system.

Analyze the following git diff.
Return STRICT JSON matching this schema:

{
  "summary": string,
  "findings": [
    {
      "severity": "error" | "warning" | "note",
      "message": string,
      "file": string | null,
      "lines": string | null
    }
  ]
}

Rules:
- Do not include markdown
- Do not include explanations outside JSON
- Be concise
- Focus on correctness, risk, clarity, and documentation gaps

Git diff:
{diff}
"""

class GeminiEngine(ReviewEngine):
    def __init__(self, model="gemini-1.5-flash"):
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        self.model = genai.GenerativeModel(model)

    def review(self, diff: str) -> ReviewResult:
        # Generate response, inserting diff argument
        response = self.model.generate_content(
            PROMPT.format(diff=diff)
        )

        # Convert text into python dictionary
        data = json.loads(response.text)
        # Enforce response schema (models.py)
        return ReviewResult.model_validate(data)