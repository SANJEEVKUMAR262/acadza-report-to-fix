
import json
from collections import defaultdict
from pathlib import Path

from engine.prepare_reports import prepare_reports

ROOT = Path(__file__).resolve().parent.parent
OUTPUT = ROOT / "data" / "grouped_reports.json"


def group_reports():
    reports = prepare_reports()
    groups = defaultdict(list)

    for report in reports:
        groups[report["questionId"]].append(report)

    result = []

    for question_id, items in groups.items():
        first = items[0]

        result.append({
            "questionId": question_id,
            "subject": first["subject"],
            "chapter": first["chapter"],
            "questionType": first["questionType"],
            "question": first["question"],
            "solution": first["solution"],
            "answer": first["answer"],
            "errorHistory": first["errorHistory"],
            "reportCount": len(items),
            "reports": [
                {
                    "reportId": item["reportId"],
                    "comment": item["student_comment"],
                }
                for item in items
            ],
        })

    return result


def main():
    groups = group_reports()

    OUTPUT.write_text(
        json.dumps(groups, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    report_count = sum(group["reportCount"] for group in groups)
    multi_report_groups = [
        group for group in groups if group["reportCount"] > 1
    ]

    print("Unique questions:", len(groups))
    print("Total reports:", report_count)
    print("Questions with multiple reports:", len(multi_report_groups))
    print("Output:", OUTPUT.relative_to(ROOT))

    assert len(groups) == 39
    assert report_count == 44
    assert len(multi_report_groups) == 4

    print("QUESTION GROUPING PASSED")


if __name__ == "__main__":
    main()
