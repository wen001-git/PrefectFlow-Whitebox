"use client";

import { useEffect } from "react";

export default function GlobalError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    // eslint-disable-next-line no-console
    console.error("app error boundary:", error);
  }, [error]);

  return (
    <section className="space-y-3 rounded border border-red-300 bg-red-50 p-4">
      <h2 className="text-lg font-semibold text-red-800">
        Something went wrong
      </h2>
      <p className="text-sm text-red-700">{error.message}</p>
      <button
        type="button"
        onClick={reset}
        className="rounded border border-red-400 bg-white px-3 py-1 text-sm hover:bg-red-100"
      >
        Try again
      </button>
    </section>
  );
}
