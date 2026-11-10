import json
from pathlib import Path
from collections import Counter, defaultdict

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

def load_json(filename):
    with (DATA_DIR / filename).open(encoding="utf-8") as f:
        return json.load(f)

def main():
    questions = load_json("questions.json")
    reports = load_json("reports.json")
    taxonomy = load_json("taxonomy.json")

    print("\n=== ACADZA DATASET VALIDATION ===")
    print("Total questions:", len(questions))
    print("Total reports:", len(reports))

    types = Counter(q.get("questionType") for q in questions)
    print("\nQuestion types:", dict(types))

    for field in ["_id", "qid"]:
        question_ids = [str(q.get(field)) for q in questions]
        known_ids = set(question_ids)
        matched = sum(
            str(r.get("questionId")) in known_ids
            for r in reports
        )
        print(f"Reports matching {field}: {matched}/{len(reports)}")

    report_ids = [r.get("reportId") for r in reports]
    print("Duplicate report IDs:",
          len(report_ids) - len(set(report_ids)))

    groups = defaultdict(list)
    for report in reports:
        groups[str(report.get("questionId"))].append(
            str(report.get("reportId"))
        )

    print("Unique reported questions:", len(groups))
    print("Multiple-report groups:")
    for qid, ids in groups.items():
        if len(ids) > 1:
            print(f"  {qid}: {', '.join(ids)}")

    print("\nTaxonomy keys:", list(taxonomy.keys()))
    print("\nVALIDATION INSPECTION COMPLETE")

if __name__ == "__main__":
    main()
