
from engine.safety import validate_proposal
from engine.edit_validator import validate_edit


def validate_full_proposal(question, proposal):
    errors = validate_proposal(proposal)

    edit = proposal.get("edit")

    if edit is not None:
        if proposal.get("verdict") != "defect":
            return errors

        if not isinstance(edit, dict):
            errors.append("Edit must be an object")
            return errors

        if "find" in edit or "replace" in edit:
            errors.extend(validate_edit(question, edit))
        else:
            errors.append(
                "Unsupported edit format: manual review required"
            )

    return errors
