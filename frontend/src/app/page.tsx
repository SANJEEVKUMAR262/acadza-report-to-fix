


"use client";

import { useEffect, useMemo, useState } from "react";
import SafeHtml from "@/components/SafeHtml";

import {
  getLatestDecision,
  getReviewHistory,
  saveReview,
  type ReviewRecord,
  type ReviewDecision,
} from "@/lib/review";



type Report = {
  reportId: string;
  questionId: string;
  student_comment: string;
  questionType: string;
  subject: string;
  chapter: string;
  question: string;
  solution: string;
  answer: string | string[];
};


type VerifiedResult = {
  reportId: string;
  questionId: string;
  verdict: string;
  repair: string | null;
  edit: {
    field: string;
    find: string;
    replace: string;
  } | null;
  route: string;
  confidence: number;
  evidence: string[];
  student_reply: string;
  provenance: string;
  validated: boolean;
  applied: boolean;
};

export default function Home() {
  const [reports, setReports] = useState<Report[]>([]);

const [verifiedResults, setVerifiedResults] = useState<VerifiedResult[]>([]);

  const [selectedId, setSelectedId] = useState("");
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");


  const [reviewHistory, setReviewHistory] = useState<ReviewRecord[]>([]);
  const [reviewNote, setReviewNote] = useState("");
  const [reviewError, setReviewError] = useState("");

  useEffect(() => {
    setReviewHistory(getReviewHistory());
  }, []);

  function recordDecision(decision: ReviewDecision) {
    if (!selectedId) return;

    try {
      const updated = saveReview(
        selectedId,
        decision,
        reviewNote,
        verifiedResults.some(r => r.reportId === selectedId && r.validated === true && r.edit !== null && r.route === "faculty_review" && r.applied === false)
      );

      setReviewHistory(updated);
      setReviewNote("");
      setReviewError("");
    } catch (err) {
      setReviewError(
        err instanceof Error
          ? err.message
          : "Unable to save faculty decision."
      );
    }
  }



  
  useEffect(() => {
    fetch("/prepared_reports.json")
      .then((response) => {
        if (!response.ok) {
          throw new Error("Unable to load reports");
        }
        return response.json();
      })
      .then((data: Report[]) => {
        setReports(data);
        if (data.length > 0) {
          setSelectedId(data[0].reportId);
        }
      })
      .catch((err) => setError(String(err)))
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    async function loadVerifiedResults() {
      try {
        const response = await fetch("/verified_results.json");

        if (!response.ok) {
          throw new Error("Failed to load verified results");
        }

        const data: VerifiedResult[] = await response.json();
        setVerifiedResults(data);
      } catch (error) {
        console.error("Verified results loading error:", error);
      }
    }

    loadVerifiedResults();
  }, []);


  const filteredReports = useMemo(() => {
    const query = search.toLowerCase().trim();

    return reports.filter((report) =>
      [
        report.reportId,
        report.subject,
        report.chapter,
        report.student_comment,
        report.questionId,
      ]
        .join(" ")
        .toLowerCase()
        .includes(query)
    );
  }, [reports, search]);

  const selected =
    reports.find((report) => report.reportId === selectedId) ?? null;

  const uniqueQuestions = new Set(
    reports.map((report) => report.questionId)
  ).size;


  const reviewedReports = reports.filter(
    (report) =>
      getLatestDecision(reviewHistory, report.reportId) !== null
  ).length;


  return (
    <main className="min-h-screen bg-slate-100 text-slate-900">
      <header className="border-b border-slate-200 bg-white px-6 py-5">
        <div className="mx-auto max-w-7xl">
          <p className="text-sm font-semibold uppercase tracking-widest text-blue-600">
            Acadza
          </p>
          <h1 className="mt-1 text-2xl font-bold">
            AI Faculty Review Console
          </h1>
          <p className="mt-1 text-sm text-slate-500">
            Student report triage and safe question correction
          </p>
        </div>
      </header>

      <div className="mx-auto max-w-7xl space-y-6 p-6">
        <section className="grid gap-4 sm:grid-cols-3">
          <StatCard title="Total Reports" value={reports.length} />
          <StatCard title="Unique Questions" value={uniqueQuestions} />
          <StatCard title="Faculty Reviewed" value={reviewedReports} />
        </section>

        {loading && (
          <p className="rounded-xl bg-white p-5">
            Loading student reports...
          </p>
        )}

        {error && (
          <p className="rounded-xl bg-red-50 p-5 text-red-700">
            {error}
          </p>
        )}

        {!loading && !error && (
          <div className="grid gap-6 lg:grid-cols-[340px_1fr]">
            <aside className="overflow-hidden rounded-2xl border border-slate-200 bg-white">
              <div className="border-b border-slate-200 p-4">
                <h2 className="font-semibold">Student Reports</h2>
                <input
                  type="search"
                  placeholder="Search reports..."
                  value={search}
                  onChange={(event) => setSearch(event.target.value)}
                  className="mt-3 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm outline-blue-500"
                />
                <p className="mt-2 text-xs text-slate-500">
                  {filteredReports.length} reports found
                </p>
              </div>

              <div className="max-h-[650px] overflow-y-auto">
                {filteredReports.map((report) => (
                  <button
                    key={report.reportId}
                    type="button"
                    onClick={() => setSelectedId(report.reportId)}
                    className={`w-full border-b border-slate-100 p-4 text-left transition hover:bg-blue-50 ${
                      selectedId === report.reportId
                        ? "bg-blue-50"
                        : ""
                    }`}
                  >
                    <div className="flex items-center justify-between gap-2">
                      <span className="font-semibold">
                        {report.reportId}
                      </span>
                     
<span
  className={`rounded-full px-2 py-1 text-xs ${
    getLatestDecision(reviewHistory, report.reportId) === "rejected"
      ? "bg-red-100 text-red-800"
      : getLatestDecision(reviewHistory, report.reportId) === "approved"
        ? "bg-green-100 text-green-800"
        : "bg-amber-100 text-amber-800"
  }`}
>
  {getLatestDecision(reviewHistory, report.reportId)
    ?.replace("_", " ") ?? "Pending"}
</span>

                    </div>

                    <p className="mt-1 text-xs text-slate-500">
                      {report.subject} · {report.chapter}
                    </p>

                    <p className="mt-2 line-clamp-2 text-sm text-slate-700">
                      {report.student_comment}
                    </p>
                  </button>
                ))}

                {filteredReports.length === 0 && (
                  <p className="p-5 text-sm text-slate-500">
                    No matching reports.
                  </p>
                )}
              </div>
            </aside>

            <section className="space-y-5">
              {selected ? (
                <>
                  <div className="rounded-2xl border border-slate-200 bg-white p-6">
                    <div className="flex flex-wrap items-center justify-between gap-3">
                      <div>
                        <p className="text-sm text-blue-600">
                          {selected.reportId}
                        </p>
                        <h2 className="text-xl font-bold">
                          Question Review
                        </h2>
                      </div>

                      <span className="rounded-full bg-blue-100 px-3 py-1 text-sm text-blue-800">
                        {verifiedResults.some(
                          (result) => result.reportId === selected.reportId
                        )
                          ? "Analysis Complete · Faculty Review Pending"
                          : "Awaiting Analysis"}
                      </span>
                    </div>

                    <p className="mt-3 text-sm text-slate-500">
                      {selected.subject} · {selected.chapter} ·{" "}
                      {selected.questionType}
                    </p>

                    <p className="mt-2 break-all text-xs text-slate-400">
                      Question ID: {selected.questionId}
                    </p>
                  </div>

                  <ContentCard
                    title="Student Report"
                    content={selected.student_comment}
                    plainText
                  />

                  <ContentCard
                    title="Original Question"
                    content={selected.question}
                  />

                  <div className="grid gap-5 md:grid-cols-2">
                    <ContentCard
                      title="Answer Key"
                      content={
                        Array.isArray(selected.answer)
                          ? selected.answer.join(", ")
                          : String(selected.answer ?? "")
                      }
                      plainText
                    />

               
{(() => {
  const result = verifiedResults.find(
    (item) => item.reportId === selected.reportId
  );

  if (!result) {
    return (
      <ContentCard
        title="Proposed Correction"
        content="No verified correction available. Faculty review is required."
        plainText
      />
    );
  }

  return (
    <section className="rounded-xl border border-slate-200 bg-white p-5">
      <h3 className="mb-3 text-lg font-semibold">
        Proposed Correction
      </h3>

      <p className="mb-2 text-sm">
        <strong>Verdict:</strong> {result.verdict}
      </p>

      <p className="mb-2 text-sm">
        <strong>Repair:</strong> {result.repair}
      </p>

      {result.edit && (
        <div className="my-3 rounded-lg bg-slate-50 p-3 text-sm">
          <p>
            <strong>Current answer:</strong> {result.edit.find}
          </p>
          <p>
            <strong>Proposed answer:</strong> {result.edit.replace}
          </p>
        </div>
      )}

      <p className="mb-3 text-sm font-medium">
        Status: {result.applied ? "Applied" : "Not Applied"}
      </p>

      <h4 className="mb-2 font-semibold">Evidence</h4>
      <ul className="mb-4 list-disc space-y-2 pl-5 text-sm">
        {result.evidence.map((item, index) => (
          <li key={index}>{item}</li>
        ))}
      </ul>

      <h4 className="mb-2 font-semibold">Student Reply</h4>
      <p className="text-sm leading-6">{result.student_reply}</p>

      <p className="mt-4 text-xs text-slate-500">
        Source: {result.provenance.replaceAll("_", " ")}
      </p>
    </section>
  );
})()}

                  </div>

                  <ContentCard
                    title="Existing Solution"
                    content={selected.solution}
                  />

<div className="rounded-2xl border border-slate-200 bg-white p-6">
  <h3 className="text-lg font-semibold">Faculty Decision</h3>

  <p className="mt-2 text-sm text-slate-500">
    Current status:{" "}
    <strong>
      {getLatestDecision(reviewHistory, selected.reportId)?.replace(
        "_",
        " "
      ) ?? "pending"}
    </strong>
  </p>

  <label
    htmlFor="review-note"
    className="mt-5 block text-sm font-medium"
  >
    Review note
  </label>

  <textarea
    id="review-note"
    value={reviewNote}
    onChange={(event) => setReviewNote(event.target.value)}
    placeholder="Explain your faculty decision..."
    rows={3}
    className="mt-2 w-full rounded-lg border border-slate-300 p-3 text-sm"
  />

  <div className="mt-4 flex flex-wrap gap-3">
    <button
      type="button"
      onClick={() => recordDecision("approved")}
      disabled={!verifiedResults.some(r => r.reportId === selected.reportId && r.validated === true && r.edit !== null && r.route === "faculty_review" && r.applied === false)}
      title="Approve a validated correction for faculty review"
      className="rounded-lg bg-green-600 px-4 py-2 text-sm font-medium text-white hover:bg-green-700 disabled:cursor-not-allowed disabled:bg-slate-200 disabled:text-slate-500"
    >
      Approve
    </button>

    <button
      type="button"
      onClick={() => recordDecision("rejected")}
      className="rounded-lg bg-red-600 px-4 py-2 text-sm font-medium text-white hover:bg-red-700"
    >
      Reject
    </button>

    <button
      type="button"
      onClick={() => recordDecision("needs_review")}
      className="rounded-lg bg-amber-500 px-4 py-2 text-sm font-medium text-white hover:bg-amber-600"
    >
      Needs Review
    </button>
  </div>

  {reviewError && (
    <p className="mt-3 text-sm text-red-600">{reviewError}</p>
  )}

  <h4 className="mt-6 font-semibold">Audit History</h4>

  <div className="mt-3 space-y-3">
    {reviewHistory
      .filter((record) => record.reportId === selected.reportId)
      .slice()
      .reverse()
      .map((record, index) => (
        <div
          key={`${record.timestamp}-${index}`}
          className="rounded-lg border border-slate-200 p-3 text-sm"
        >
          <p className="font-semibold capitalize">
            {record.decision.replace("_", " ")}
          </p>

          <p className="mt-1 text-xs text-slate-500">
            {new Date(record.timestamp).toLocaleString()}
          </p>

          <p className="mt-2 whitespace-pre-wrap">
            {record.note || "No note provided."}
          </p>
        </div>
      ))}

    {!reviewHistory.some(
      (record) => record.reportId === selected.reportId
    ) && (
      <p className="text-sm text-slate-500">
        No faculty decisions recorded yet.
      </p>
    )}
  </div>
</div>

                </>
              ) : (
                <div className="rounded-2xl bg-white p-6">
                  Select a report to begin reviewing.
                </div>
              )}
            </section>
          </div>
        )}
      </div>
    </main>
  );
}

function StatCard({
  title,
  value,
}: {
  title: string;
  value: string | number;
}) {
  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-5">
      <p className="text-sm text-slate-500">{title}</p>
      <p className="mt-2 text-3xl font-bold">{value}</p>
    </div>
  );
}

function ContentCard({
  title,
  content,
  plainText = false,
}: {
  title: string;
  content: string;
  plainText?: boolean;
}) {
  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-6">
      <h3 className="mb-4 font-semibold">{title}</h3>

      {plainText ? (
        <p className="whitespace-pre-wrap text-sm leading-7">
          {content}
        </p>
      ) : (
        <SafeHtml html={content} />
      )}
    </div>
  );
}
