"use client";

import type { LineageField } from "@/lib/api";

export function FieldPicker({
  fields,
  selected,
  onChange,
}: {
  fields: LineageField[];
  selected: string | null;
  onChange: (fieldId: string) => void;
}) {
  return (
    <label className="flex flex-wrap items-center gap-2 text-sm">
      <span className="text-xs font-semibold uppercase tracking-wide text-gray-600">
        Field
      </span>
      <select
        value={selected ?? ""}
        onChange={(e) => onChange(e.target.value)}
        className="min-w-[280px] rounded border border-gray-300 bg-white px-2 py-1 text-sm shadow-sm focus:border-blue-500 focus:outline-none"
      >
        <option value="" disabled>
          Choose a field…
        </option>
        {fields.map((f) => (
          <option key={f.field_id} value={f.field_id}>
            {f.sheet} · {f.label || f.field_id}
          </option>
        ))}
      </select>
    </label>
  );
}
