"""Run bounded Groq experiments without modifying question-bank data."""

import argparse
import json
import os
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv
from groq import Groq

from engine.ai_quality_gate import check_ai_quality
from engine.proposal_validator import validate_full_proposal

ROOT = Path(__file__).resolve().parent.parent
EXPERIMENT_DIR = ROOT / "data" / "ai_experiments"


def load_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=3)
    args = parser.parse_args()

    if not 1 <= args.limit <= 5:
        raise ValueError("Limit must be between 1 and 5")

    load_dotenv(dotenv_path=ROOT / ".env")

    reports = load_json(ROOT / "data/prepared_reports.json")
    if isinstance(reports, dict):
        reports = reports["reports"]

    taxonomy = load_json(ROOT / "data/taxonomy.json")

    baseline = load_json(
        EXPERIMENT_DIR / "R001_groq_iteration2_retry.json"
    )
    system_prompt = baseline["system_prompt"]

    client = Groq(api_key=os.environ["GROQ_API_KEY"])
    EXPERIMENT_DIR.mkdir(parents=True, exist_ok=True)

    completed = {"R001", "R002"}
    pending = [
        r for r in reports
        if r["reportId"] not in completed
        and not (
            EXPERIMENT_DIR / f"{r['reportId']}_groq_batch.json"
        ).exists()
    ]

    print("=== GROQ BATCH ===")
    print("Requested reports:", args.limit)

    for report in pending[:args.limit]:
        report_id = report["reportId"]
        output_path = EXPERIMENT_DIR / f"{report_id}_groq_batch.json"

        if output_path.exists():
            print(report_id, "SKIPPED: experiment already exists")
            continue

        user_prompt = json.dumps({
            "report": report,
            "allowed_verdicts": list(taxonomy["verdicts"].keys()),
            "allowed_repairs": list(taxonomy["repairs"].keys())
        }, ensure_ascii=False)

        record = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "provider": "Groq",
            "model": "openai/gpt-oss-20b",
            "reportId": report_id,
            "system_prompt": system_prompt,
            "user_prompt": user_prompt
        }

        try:
            response = client.chat.completions.create(
                model="openai/gpt-oss-20b",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0,
                max_tokens=1600
            )

            raw = response.choices[0].message.content or ""
            record["raw_model_output"] = raw

            proposal = json.loads(raw)

            if not isinstance(proposal, dict):
                raise ValueError(
                    "AI response must be a JSON object"
                )

            edit = proposal.get("edit")
            if edit is not None and not isinstance(edit, dict):
                raise ValueError(
                    "AI edit must be an object or null"
                )

            question = {
                "questionType": report["questionType"],
                "payload": {
                    "question": report.get("question"),
                    "solution": report.get("solution"),
                    "answer": report.get("answer")
                }
            }

            structural_errors = validate_full_proposal(
                question, proposal
            )
            quality_errors = check_ai_quality(
                report, proposal
            )

            record["structural_errors"] = structural_errors
            record["quality_errors"] = quality_errors
            record["automated_pass"] = (
                not structural_errors and not quality_errors
            )
            record["human_review_status"] = "pending"

            print(
                report_id,
                "PASS" if record["automated_pass"]
                else "REVIEW",
                "| verdict:", proposal.get("verdict"),
                "| route:", proposal.get("route")
            )

        except Exception as exc:
            record["error"] = {
                "type": type(exc).__name__,
                "message": str(exc)[:500]
            }
            record["automated_pass"] = False
            record["human_review_status"] = "pending"
            print(report_id, "ERROR:", type(exc).__name__)

        output_path.write_text(
            json.dumps(record, indent=2, ensure_ascii=False),
            encoding="utf-8"
        )

    print("=== BATCH COMPLETE ===")


if __name__ == "__main__":
    main()
