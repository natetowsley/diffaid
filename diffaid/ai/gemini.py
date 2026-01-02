import os
import json
from google import genai
from diffaid.ai.base import ReviewEngine
from diffaid.models import ReviewResult
from pydantic import ValidationError

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
- Output JSON only
- No markdown
- No commentary
"""

class GeminiEngine(ReviewEngine):
    def __init__(self, model="gemini-2.5-flash"):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise RuntimeError("GEMINI_API_KEY is not set")

        self.client = genai.Client(
            http_options={'api_version': 'v1'},
            api_key=api_key
        )
        self.model = model

    def review(self, diff: str) -> ReviewResult:
        # Insert diff into prompt
        prompt = f"""{PROMPT}

        Git diff:
        {diff}
        """

        try:
          response = self.client.models.generate_content(
              model=self.model,
              contents=prompt,
          )
          data = json.loads(response.text)
          # Enforce response schema (models.py)
          return ReviewResult.model_validate(data)
        except ValidationError as error:
            raise RuntimeError(f"AI returned invalid schema: {error}") from error
        
        except json.JSONDecodeError as error:
            raise RuntimeError(f"AI returned malformed JSON: {error}") from error
        