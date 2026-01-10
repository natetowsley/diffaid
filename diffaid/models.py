from pydantic import BaseModel
from typing import List, Literal

# Severity must be given as one of three strings
Severity = Literal["error", "warning", "note"]

# Structure required rather than raw AI output
class Finding(BaseModel):
    severity: Severity
    message: str
    file: str | None = None

class ReviewResult(BaseModel):
    summary: str
    findings: List[Finding]