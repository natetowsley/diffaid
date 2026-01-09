import os
import json
from google import genai
from diffaid.ai.base import ReviewEngine
from diffaid.models import ReviewResult
from pydantic import ValidationError
from dotenv import load_dotenv

load_dotenv()

PROMPT = """
You are an automated code review system.

Analyze the following git diff.

You MUST review all logical changes in the diff. The presence of errors or warnings
must NOT prevent you from providing notes or suggestions on other parts of the change.

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

Review rules:
- Consider each modified file and each logical change independently
- Continue reviewing after identifying errors or warnings
- Provide notes for improvements or observations even when errors exist
- If a change has no issues, you may still include a note acknowledging correctness
- Do NOT omit feedback simply because higher-severity findings exist

Output rules:
- Output JSON only
- No markdown
- No commentary
"""

class GeminiEngine(ReviewEngine):
    def __init__(self, model="gemini-2.5-flash"):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise RuntimeError("GEMINI_API_KEY is not set.\n"
                "Create a .env file in root with: GEMINI_API_KEY=your-key-here\n"
                "Or get a free key at: https://aistudio.google.com/apikey"
            )

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
        