import json
from datetime import datetime, timezone
from pathlib import Path

from engine.prepare_reports import prepare_reports

ROOT = Path(__file__).resolve().parent.parent
OUTPUT = ROOT / "data" / "pending_analysis.json"


def build_pending_queue():
    reports = prepare_reports()

    report_ids = [report["reportId"] for report in reports]

    if len(report_ids) != len(set(report_ids)):
        raise ValueError("Duplicate report IDs detected.")

    queue = []

    for report in reports:
        queue.append({
            "reportId": report["reportId"],
            "questionId": report["questionId"],
            "status": "pending_analysis",
            "verdict": None,
            "repair": None,
            "edit": None,
            "route": "faculty_review",
            "confidence": None,
            "evidence": [],
            "student_reply": None,
        })

    return queue


def main():
    queue = build_pending_queue()

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)

    document = {
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "mode": "offline",
        "analysisCompleted": False,
        "reports": queue,
    }

    OUTPUT.write_text(
        json.dumps(document, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    print("Total reports:", len(queue))
    print("Pending analysis:", len(queue))
    print("Final AI verdicts:", 0)
    print("Output:", OUTPUT.relative_to(ROOT))

    assert len(queue) == 44
    assert all(item["verdict"] is None for item in queue)

    print("BATCH PROCESSOR TEST PASSED")


if __name__ == "__main__":
    main()
