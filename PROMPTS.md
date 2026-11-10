# Prompting, Experiments, and Failure Analysis

## 1. AI Integration Objective

The intended workflow was to use an AI model to assess student-reported errors in educational questions, identify defects, explain evidence, and propose corrections subject to validation and faculty approval.

The implementation also includes offline data preparation, assessment validation, and a faculty-review dashboard.

## 2. Verified OpenAI API Test

Source: `engine/test_openai.py`

Model: `gpt-4.1-mini` (default configuration)

API: OpenAI Responses API

Exact prompt:

> Reply with exactly: ACADZA API CONNECTED

Configuration:

- `max_output_tokens=30`
- `store=False`
- `timeout=30.0`
- `max_retries=0`

Expected response:

> ACADZA API CONNECTED

Observed outcome: The API attempt encountered an `insufficient_quota` error. A successful model response was not obtained.

This was an API-access failure, not evidence that the model answered incorrectly.

## 3. Offline Processing

Source: `engine/batch_processor.py`

The batch processor creates pending assessment records from the prepared report dataset.

Its output explicitly records:

- `mode: offline`
- `analysisCompleted: false`
- `status: pending_analysis`
- No final AI verdicts

This stage does not perform model inference.

## 4. Assessment Workflow

The completed dataset contains 44 assessment records.

The assessments were produced through human-assisted mathematical and content review, then checked against the project's validation rules.

The review process considered:

1. The original question and answer.
2. The student's complaint.
3. The existing solution.
4. Whether the complaint identified a genuine defect.
5. Whether a specific correction was justified.
6. Whether faculty review was necessary.

The resulting assessments include verdicts, repair categories, evidence, student replies, confidence values, and optional proposed edits.

These assessments must not be represented as successful automated outputs from the OpenAI API.

## 5. Safety and Validation

The workflow distinguishes reported problems from validated correction proposals.

Important safeguards include:

- No automatic modification of original questions.
- Faculty review for proposed corrections.
- Validation before a correction can be approved.
- Conservative handling of incomplete or ambiguous questions.
- Treating student-supplied instructions as untrusted content.
- Sanitizing rendered question content.

## 6. Observed Failure and Recovery

### Failure 1: OpenAI API quota limitation

Observed: The connectivity test failed with `insufficient_quota`.

Impact: Live AI inference could not be completed through the configured API.

Recovery: Continued with an offline, human-assisted review workflow and retained explicit provenance for the assessments.

### Additional model failures

Three distinct model-response failures have not been verified from the available experiment records.

No fabricated model outputs or invented prompt iterations are included here. Further live model testing would be required to document genuine hallucination, classification, or correction failures attributable to model responses.

## 7. Limitations

- The API connectivity test did not produce a successful model response.
- The offline batch processor does not classify reports.
- Completed assessments were human-assisted.
- Validation checks do not replace independent faculty verification.
- The dashboard presents prepared assessments rather than performing live model inference.

## 8. Future Prompting Experiments

Once API access is available, the intended evaluation should test structured classification, evidence-grounded corrections, duplicate-report handling, prompt-injection resistance, and conservative abstention when question data is insufficient.

Each experiment should preserve the exact input prompt, raw model output, validation result, identified failure, and subsequent correction.
