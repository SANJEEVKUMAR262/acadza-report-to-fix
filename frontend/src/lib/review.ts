
export type ReviewDecision =
  | "approved"
  | "rejected"
  | "needs_review";

export type ReviewRecord = {
  reportId: string;
  decision: ReviewDecision;
  timestamp: string;
  note: string;
};

const STORAGE_KEY = "acadza_faculty_reviews_v1";

export function getReviewHistory(): ReviewRecord[] {
  if (typeof window === "undefined") {
    return [];
  }

  try {
    const stored = localStorage.getItem(STORAGE_KEY);

    if (!stored) {
      return [];
    }

    const parsed: unknown = JSON.parse(stored);

    if (!Array.isArray(parsed)) {
      return [];
    }

    return parsed.filter(
      (item): item is ReviewRecord =>
        typeof item === "object" &&
        item !== null &&
        typeof item.reportId === "string" &&
        ["approved", "rejected", "needs_review"].includes(
          item.decision
        ) &&
        typeof item.timestamp === "string" &&
        typeof item.note === "string"
    );
  } catch {
    return [];
  }
}

export function saveReview(
  reportId: string,
  decision: ReviewDecision,
  note: string,
  hasValidatedProposal = false
): ReviewRecord[] {
  if (decision === "approved" && !hasValidatedProposal) {
    throw new Error(
      "Cannot approve without a validated correction proposal."
    );
  }

  if (!reportId.trim()) {
    throw new Error("A report ID is required.");
  }

  const record: ReviewRecord = {
    reportId,
    decision,
    timestamp: new Date().toISOString(),
    note: note.trim(),
  };

  const history = [...getReviewHistory(), record];

  localStorage.setItem(STORAGE_KEY, JSON.stringify(history));

  return history;
}

export function getLatestDecision(
  history: ReviewRecord[],
  reportId: string
): ReviewDecision | null {
  for (let index = history.length - 1; index >= 0; index--) {
    if (history[index].reportId === reportId) {
      return history[index].decision;
    }
  }

  return null;
}
