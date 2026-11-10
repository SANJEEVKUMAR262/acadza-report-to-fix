
from typing import Any, Dict, List, Optional, TypedDict


class TriageResult(TypedDict):
    reportId: str
    questionId: str
    verdict: str
    repair: Optional[str]
    edit: Optional[Dict[str, Any]]
    route: str
    confidence: float
    evidence: List[str]
    student_reply: str


def create_pending_result(report: Dict[str, Any]) -> TriageResult:
    """Create a safe placeholder without inventing a verdict."""

    return {
        "reportId": report["reportId"],
        "questionId": report["questionId"],
        "verdict": "not_actionable",
        "repair": None,
        "edit": None,
        "route": "faculty_review",
        "confidence": 0.0,
        "evidence": [
            "Analysis has not been performed.",
            "The API is unavailable; this is a placeholder, not a verified verdict.",
        ],
        "student_reply": (
            "Thank you for reporting this question. "
            "Your report has been forwarded for review."
        ),
    }
