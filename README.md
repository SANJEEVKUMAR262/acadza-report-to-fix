# Acadza — Report to Fix Loop

A faculty-in-the-loop review system for student-reported errors in educational questions.

## Overview

The system joins student reports with their original questions, organizes reports by question, assesses reported issues, and presents evidence and proposed corrections in a Next.js review dashboard.

Faculty can approve eligible corrections, reject reports, or mark them for further review. Decisions are recorded in a local browser audit history.

## Dataset

- 44 student reports
- 43 original questions
- 39 distinct questions referenced by reports
- 44 completed assessment records

Input data is stored in `data/`.

## Review Workflow

1. Load original questions and student reports.
2. Match reports to questions and group related complaints.
3. Classify issues and document supporting evidence.
4. Produce proposed corrections where sufficient evidence exists.
5. Validate assessment records and correction proposals.
6. Display results in the faculty review console.
7. Record faculty decisions without automatically changing original questions.

## Safety

- Original questions remain unchanged during assessment.
- Corrections requiring faculty review are not automatically applied.
- Approval requires a validated, unapplied correction proposal routed for faculty review.
- Reports without sufficient evidence cannot be approved as corrections.
- Student-supplied instructions are treated as untrusted content.
- Question content is rendered through a sanitization component.
- Faculty review history is stored in browser localStorage.

## Project Structure

- `data/` — original datasets, prepared reports, and assessment results
- `engine/` — data preparation, grouping, validation, and safety logic
- `frontend/` — Next.js faculty review dashboard
- `data/results.json` — completed assessment output
- `PRODUCT.md` — product decisions and trade-offs
- `PROMPTS.md` — AI prompting and evaluation documentation

## Run the Dashboard

Requirements: Node.js and npm.

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:3000.

## Production Build

```bash
cd frontend
npm run build
```

## Review Data

The dashboard reads:

- `frontend/public/prepared_reports.json`
- `frontend/public/verified_results.json`

The assessment output is also available at `data/results.json`.

## AI Usage and Provenance

An OpenAI API integration was tested but encountered an insufficient-quota error. Completed assessments were produced through human-assisted mathematical review and validation. They must not be represented as successful automated model-generated classifications.

## Limitations

- Faculty decisions are stored locally in the browser, not in a shared backend.
- The dashboard does not automatically apply approved corrections to the question bank.
- Assessment validation does not replace independent academic or faculty verification.
- A production deployment serves the review interface and prepared assessment data.
