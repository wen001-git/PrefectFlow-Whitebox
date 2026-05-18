"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";

// HARD RESTRAINT (AGENTS § 6.14): no form library (react-hook-form,
// formik, zod-form). If validation grows complex, propose:
//   "ADR: introduce a form/validation library for apps/web".
export function PickerForm({
  servicers,
  dates,
}: {
  servicers: string[];
  dates: string[];
}) {
  const router = useRouter();
  const [servicer, setServicer] = useState<string>(servicers[0] ?? "");
  const [date, setDate] = useState<string>(dates[0] ?? "");
  const disabled = servicers.length === 0 || dates.length === 0;

  const onSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const params = new URLSearchParams();
    if (servicer) params.set("servicer", servicer);
    if (date) params.set("date", date);
    router.push(`/runs?${params.toString()}`);
  };

  return (
    <form className="max-w-md space-y-3" onSubmit={onSubmit}>
      <label className="block text-sm">
        <span className="block font-medium">Servicer</span>
        <select
          className="mt-1 w-full rounded border border-gray-300 px-2 py-1"
          value={servicer}
          onChange={(e) => setServicer(e.target.value)}
        >
          {servicers.length === 0 && <option value="">(none available)</option>}
          {servicers.map((s) => (
            <option key={s} value={s}>
              {s}
            </option>
          ))}
        </select>
      </label>
      <label className="block text-sm">
        <span className="block font-medium">Remit date</span>
        <select
          className="mt-1 w-full rounded border border-gray-300 px-2 py-1"
          value={date}
          onChange={(e) => setDate(e.target.value)}
        >
          {dates.length === 0 && <option value="">(none available)</option>}
          {dates.map((d) => (
            <option key={d} value={d}>
              {d}
            </option>
          ))}
        </select>
      </label>
      <button
        type="submit"
        disabled={disabled}
        className={`rounded px-4 py-2 text-sm font-medium text-white ${
          disabled
            ? "cursor-not-allowed bg-gray-300"
            : "bg-blue-600 hover:bg-blue-700"
        }`}
      >
        Browse runs →
      </button>
    </form>
  );
}
