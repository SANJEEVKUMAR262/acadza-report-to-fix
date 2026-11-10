
import json
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

with (DATA_DIR / "taxonomy.json").open(encoding="utf-8") as f:
    TAXONOMY = json.load(f)

VALID_ROUTES = {
    "auto_apply",
    "faculty_review",
    "no_change",
}


def validate_proposal(proposal):
    errors = []

    verdict = proposal.get("verdict")
    repair = proposal.get("repair")
    route = proposal.get("route")
    edit = proposal.get("edit")

    if verdict not in TAXONOMY["verdicts"]:
        errors.append("Invalid verdict")

    if route not in VALID_ROUTES:
        errors.append("Invalid route")

    if verdict != "defect":
        if repair is not None:
            errors.append("Non-defect verdict cannot have a repair")

        if edit is not None:
            errors.append("Non-defect verdict cannot have an edit")

        if route == "auto_apply":
            errors.append("Non-defect cannot be auto-applied")

    if repair is not None:
        if repair not in TAXONOMY["repairs"]:
            errors.append("Unknown repair type")
        else:
            rule = TAXONOMY["repairs"][repair]

            if route == "auto_apply" and not rule["auto"]:
                errors.append("Repair requires faculty review")

            if edit is not None:
                field = edit.get("field")

                if field not in rule["fields"]:
                    errors.append(
                        f"Repair '{repair}' cannot edit '{field}'"
                    )

    if route == "auto_apply":
        if verdict != "defect" or repair is None or edit is None:
            errors.append(
                "Auto-apply requires defect, repair, and edit"
            )

    return errors
