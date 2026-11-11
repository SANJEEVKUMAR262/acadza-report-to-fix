"""Additional quality checks for AI-generated report assessments."""

import re

REQUIRED_FIELDS = {
    "reportId", "questionId", "verdict", "repair",
    "edit", "route", "confidence", "evidence", "student_reply"
}


def check_ai_quality(report, proposal):
    errors = []

    if not isinstance(proposal, dict):
        return ["AI response must be a JSON object"]

    missing = sorted(REQUIRED_FIELDS - set(proposal))
    if missing:
        errors.append("Missing fields: " + ", ".join(missing))

    if proposal.get("reportId") != report.get("reportId"):
        errors.append("Report ID mismatch")

    if proposal.get("questionId") != report.get("questionId"):
        errors.append("Question ID mismatch")

    confidence = proposal.get("confidence")
    if (
        isinstance(confidence, bool)
        or not isinstance(confidence, (int, float))
        or not 0 <= confidence <= 1
    ):
        errors.append("Invalid confidence")

    evidence = proposal.get("evidence")
    if (
        not isinstance(evidence, list)
        or not evidence
        or any(not isinstance(item, str) or not item.strip()
               for item in evidence)
    ):
        errors.append("Evidence must be a non-empty list of strings")

    reply = proposal.get("student_reply")
    if not isinstance(reply, str) or not reply.strip():
        errors.append("Student reply is missing or empty")

    if proposal.get("route") == "auto_apply":
        errors.append("AI corrections require faculty review")

    combined = " ".join(
        item for item in evidence or [] if isinstance(item, str)
    ).lower()

    solution = str(report.get("solution", ""))

    subtraction_present = (
        "&#x02212;" in solution
        or "−" in solution
        or "V_L - V_C" in solution
    )

    false_product_claim = bool(
        re.search(
            r"solution.{0,60}(incorrectly|wrongly).{0,50}product",
            combined
        )
    )

    if subtraction_present and false_product_claim:
        errors.append(
            "Unsupported claim: solution uses a product instead of subtraction"
        )

    return errors
