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


## 9. Live Groq AI Experiments

Following the OpenAI quota limitation, the project successfully used
Groq with model `openai/gpt-oss-20b` for live AI experiments.

Implementation:
- `engine/groq_batch.py`
- `engine/proposal_validator.py`
- `engine/ai_quality_gate.py`

Experiment evidence is stored in `data/ai_experiments/`.

All 44 report IDs were covered by an attempted AI experiment.
Coverage means attempted processing, not 44 successful or approved outputs.
Some attempts produced malformed JSON, incomplete responses, or proposals
rejected by validation.

The existing `data/results.json` assessments remain human-assisted.
They must not be attributed to Groq.

### Prompting approach

The model received the original question, solution, answer key, and
student complaint. It was instructed to produce a structured JSON
assessment containing the report ID, question ID, verdict, repair
category, evidence, optional edit, confidence, student reply, and
faculty-review route.

The prompt emphasized evidence-based reasoning, minimal supported
corrections, and faculty oversight. Original prompts and raw outputs
are preserved in the experiment records.

### Iteration 1: Initial live model output

The first R001 experiment correctly identified an answer-key problem,
but the student-facing explanation was inadequate.

A separate JSON-mode attempt returned an API validation error.
A subsequent retry without that response-format setting succeeded.

### Iteration 2: Improved student communication

The R001 iteration-two retry produced a more useful student reply
while retaining the correct answer-key diagnosis.

R002 demonstrated that structurally valid output can still contain
unsupported reasoning: the model claimed that the original solution
used multiplication where the original MathML already represented
subtraction. This was initially missed by automated validation.

### Iteration 3: Batch processing and quality checks

Batch experiments used temperature 0 and a structured output prompt.
Each attempt preserved its raw response, parsed proposal when
available, validation findings, and errors.

The batch processor did not edit original questions. Every proposed
correction was routed for faculty review.

## 10. Observed AI Failures

### Failure A: Unsupported factual explanation — R002

The model proposed a correction based partly on an incorrect claim
about the existing solution's mathematical operation.

Impact: A plausible explanation could mislead faculty despite a
structurally valid proposal.

Mitigation: Compare evidence with the original question and MathML,
rather than trusting model-generated explanations or schema checks.

### Failure B: Invalid edit target — R012

The model identified a spelling issue but proposed editing an
unsupported `options` field instead of the actual question field.

Impact: The proposed correction could not be safely applied.

Mitigation: Structural validation rejected the proposal. A separate
human-corrected candidate was saved for faculty review.

### Failure C: Incorrect replacement match — R014

The model identified a raw LaTeX rendering issue but proposed a
replacement string that did not match the original source. Its verdict
and repair combination also violated the expected schema.

Impact: The proposed edit would not reliably correct the question.

Mitigation: Validate exact text matches and repair categories.
A separate corrected candidate was saved pending faculty approval.

### Failure D: Unsupported answer-key replacement — R006

The question omitted the cube's edge length, although its solution
implicitly assumed 10 cm. The model detected missing information but
proposed replacing the answer `50` with `?` and omitted the student
reply.

Impact: The proposal could damage an answer key without resolving
the incomplete question.

Mitigation: Preserve the original answer, document that 50 mm³ is
conditional on the assumed edge length, and request faculty review.
See `R006_human_review.json`.

### Failure E: Malformed or truncated JSON

Several attempts, including R019 and R031, failed JSON parsing.
Other responses omitted required fields such as `student_reply`.

Impact: The output could not be treated as a complete assessment.

Mitigation: Preserve raw responses and parsing errors, mark failed
attempts for review, and never auto-apply them.

## 11. Evaluation Boundaries

- Attempt coverage: 44 of 44 report IDs.
- Attempt coverage does not establish correctness or successful parsing.
- Automated PASS indicates validation checks passed, not faculty approval.
- Human-corrected proposals are separate from raw AI outputs.
- No proposed correction is automatically applied.
- The dashboard uses prepared human-assisted assessments rather than
  making a live Groq request on each page load.
- Browser-local faculty decisions are not shared backend approvals.

The experiment records provide auditable evidence of both successful
and unsuccessful model behavior.
