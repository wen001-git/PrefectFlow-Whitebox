import Link from "next/link";

import { PickerForm } from "@/components/PickerForm";
import { apiGet, type RunListResponse } from "@/lib/api";

// Server component: derives picker options from /api/v1/runs (no
// dedicated /servicers + /remit-dates endpoints exist yet — when the
// engine lands and the run table grows large enough that scanning all
// runs is costly, propose:
//   "ADR: add /api/v1/servicers + /api/v1/remit-dates discovery endpoints".
async function fetchPickerOptions(): Promise<{
  servicers: string[];
  dates: string[];
}> {
  const res = await apiGet<RunListResponse>(
    "/api/v1/runs?limit=500&offset=0",
  );
  const servicers = Array.from(
    new Set(res.runs.map((r) => r.servicer)),
  ).sort();
  const dates = Array.from(
    new Set(res.runs.map((r) => r.remit_date)),
  ).sort((a, b) => (a < b ? 1 : -1));
  return { servicers, dates };
}

export default async function HomePage() {
  const { servicers, dates } = await fetchPickerOptions();
  return (
    <section className="space-y-6">
      <header className="space-y-1">
        <h1 className="text-2xl font-semibold">Run picker</h1>
        <p className="text-sm text-gray-600">
          Pick a servicer + remit date to browse validation runs.
        </p>
      </header>
      <PickerForm servicers={servicers} dates={dates} />
      <p className="text-xs text-gray-500">
        Or jump straight to the{" "}
        <Link className="text-blue-600 hover:underline" href="/runs">
          full run list
        </Link>
        .
      </p>
    </section>
  );
}
