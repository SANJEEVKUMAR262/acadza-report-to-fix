
def validate_edit(question, edit):
    if not isinstance(edit, dict):
        return ["Edit must be an object"]

   
    question_type = question.get("questionType")
    payload = question.get("payload")

    if not isinstance(payload, dict):
        payload = question.get(question_type)

    if not isinstance(payload, dict):
        return ["Question payload is missing"]

    field = edit.get("field")

    if field not in payload:
        return [f"Field '{field}' does not exist"]

    original = payload[field]


    if not isinstance(original, str):
        return ["This validator only supports text fields"]

    find = edit.get("find")
    replace = edit.get("replace")

    if not isinstance(find, str) or not find:
        return ["Find must be a non-empty string"]

    if not isinstance(replace, str):
        return ["Replace must be a string"]

    errors = []
    occurrences = original.count(find)

    if occurrences == 0:
        errors.append("Original text not found")
    elif occurrences > 1:
        errors.append("Original text is not unique")

    if find == replace:
        errors.append("Edit does not change anything")

    return errors
