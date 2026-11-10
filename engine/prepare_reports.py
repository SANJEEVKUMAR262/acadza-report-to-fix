
import json
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def load_json(filename):
    with (DATA_DIR / filename).open(
        "r", encoding="utf-8"
    ) as file:
        return json.load(file)


def prepare_reports():
    questions = load_json("questions.json")
    reports = load_json("reports.json")

    question_lookup = {
        str(question["_id"]): question
        for question in questions
    }

    prepared = []

    for report in reports:
        question_id = str(report["questionId"])
        question = question_lookup.get(question_id)

        if question is None:
            raise ValueError(
                f"Question missing for report {report['reportId']}"
            )

        question_type = question["questionType"]
        payload = question[question_type]

        prepared.append({
            "reportId": report["reportId"],
            "questionId": question_id,
            "student_comment": report.get("comment", ""),
            "questionType": question_type,
            "subject": question.get("subject"),
            "chapter": question.get("chapter"),
            "question": payload.get("question"),
            "solution": payload.get("solution"),
            "answer": payload.get("answer"),
            "errorHistory": question.get("errorHistory", []),
        })

    return prepared


if __name__ == "__main__":
    prepared = prepare_reports()

    print("Total prepared reports:", len(prepared))
    print("First report ID:", prepared[0]["reportId"])
    print("First question ID:", prepared[0]["questionId"])
    print("First question type:", prepared[0]["questionType"])

    assert len(prepared) == 44

    print("REPORT PREPARATION PASSED")
