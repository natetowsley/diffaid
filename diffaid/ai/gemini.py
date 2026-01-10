import os
import json
from google import genai
from diffaid.ai.base import ReviewEngine
from diffaid.models import ReviewResult
from pydantic import ValidationError
from dotenv import load_dotenv

load_dotenv()

SEVERITY_GUIDELINES = """
Severity definitions (use these consistently):

ERROR - Issues that will cause:
- Runtime crashes or exceptions
- Data loss or corruption
- Security vulnerabilities (SQL injection, XSS, auth bypass, etc.)
- Breaking API changes
- Logic errors that produce wrong results
- Syntax errors or type errors

WARNING - Issues that may cause problems:
- Performance issues (N+1 queries, inefficient algorithms)
- Deprecated API usage
- Missing error handling for edge cases
- Code smells that could lead to bugs
- Potential race conditions
- Missing input validation (non-security)
- TODO/FIXME comments in critical code

NOTE - Suggestions and observations:
- Code style improvements
- Better variable/function naming
- Opportunities to refactor for clarity
- Missing documentation
- Best practice suggestions
- Potential optimizations (minor)
- Code duplication (minor)
"""

PROMPT_DEFAULT = f"""
You are an automated code review system.

Analyze the following git diff and provide a HIGH-LEVEL review.

{SEVERITY_GUIDELINES}

Provide one finding containing a brief summary of changes per file (1-2 sentences) and 
only flag IMPORTANT issues. If IMPORTANT issues arise, there can be multiple findings per file,
 one for each IMPORTANT issue. Do NOT provide minor style suggestions, nitpicks, or obvious observations.

Return STRICT JSON matching this schema:

{{
  "summary": string,
  "findings": [
    {{
      "severity": "error" | "warning" | "note",
      "message": string,
      "file": string | null
    }}
  ]
}}

CRITICAL: The severity field MUST be one of these exact lowercase strings:
- "error" (not "Error" or "ERROR")
- "warning" (not "Warning" or "WARNING")  
- "note" (not "Note" or "NOTE")

IMPORTANT: Make your messages descriptive and searchable. Include:
- Function/class/variable names when relevant
- The specific issue (not just "error here")
- What to look for in the file

Examples of GOOD messages:
- "SQL injection risk in execute_query() function - user input not sanitized"
- "Unhandled exception in async process_payment() - missing try/catch"
- "Unused import 'pandas' at top of file"

Examples of BAD messages:
- "Error on this line"
- "Fix this"
- "Problem detected"

Review rules:
- Provide one brief summary note per file (1-2 sentences) for overall changes
- Flag IMPORTANT issues as separate findings (errors/warnings)
- Do NOT provide minor style suggestions, nitpicks, or obvious observations
- Prioritize critical issues over minor improvements
- Limit to the most impactful findings (aim for 5-10 total findings max)

Output rules:
- Output JSON only
- No markdown
- No commentary
"""

PROMPT_DETAILED = f"""
You are an automated code review system.

Analyze the following git diff in DETAIL.

{SEVERITY_GUIDELINES}

You MUST review all logical changes in the diff. The presence of errors or warnings
must NOT prevent you from providing notes or suggestions on other parts of the change.

Return STRICT JSON matching this schema:

{{
  "summary": string,
  "findings": [
    {{
      "severity": "error" | "warning" | "note",
      "message": string,
      "file": string | null
    }}
  ]
}}

CRITICAL: The severity field MUST be one of these exact lowercase strings:
- "error" (not "Error" or "ERROR")
- "warning" (not "Warning" or "WARNING")  
- "note" (not "Note" or "NOTE")

IMPORTANT: Make your messages descriptive and searchable. Include:
- Function/class/variable names when relevant  
- The specific issue (not just "error here")
- What to look for in the file

Examples of GOOD messages:
- "SQL injection risk in execute_query() function - user input not sanitized"
- "Unhandled exception in async process_payment() - missing try/catch"
- "Consider extracting data validation logic into separate validator class"

Examples of BAD messages:
- "Error on this line"
- "Fix this"
- "Problem detected"

Review rules:
- Consider each modified file and each logical change independently
- Continue reviewing after identifying errors or warnings
- Provide notes for improvements or observations even when errors exist
- Include style suggestions, best practices, and optimization opportunities
- Apply severity levels consistently according to the definitions above
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

    def review(self, diff: str, detailed: bool = False) -> ReviewResult:
        # Choose prompt based on value of detailed
        prompt_template = PROMPT_DETAILED if detailed else PROMPT_DEFAULT

        # Insert diff into prompt
        prompt = f"""{prompt_template}

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
        