
"use client";

import { useEffect, useState } from "react";

type SafeHtmlProps = {
  html: string;
};

export default function SafeHtml({ html }: SafeHtmlProps) {
  const [sanitized, setSanitized] = useState<string | null>(null);

  useEffect(() => {
    let active = true;

    async function sanitizeContent() {
      const DOMPurify = (await import("dompurify")).default;

      const clean = DOMPurify.sanitize(html, {
        USE_PROFILES: {
          html: true,
          mathMl: true,
          svg: false,
        },
      });

      if (active) {
        setSanitized(clean);
      }
    }

    sanitizeContent();

    return () => {
      active = false;
    };
  }, [html]);

  if (sanitized === null) {
    return (
      <p className="text-sm text-slate-500">
        Rendering question...
      </p>
    );
  }

  return (
    <div
      className="max-w-full overflow-x-auto break-words text-sm leading-7 [&_p]:mb-3 [&_sup]:align-super [&_sub]:align-sub"
      dangerouslySetInnerHTML={{ __html: sanitized }}
    />
  );
}
