// TODO: d-ui-core-screens will wire this form to /api/v1/runs (POST) and
// populate options from /api/v1/servicers + /api/v1/remit-dates.
// HARD RESTRAINT (architecture § 5): no form libraries (react-hook-form,
// formik, zod-form) at this stage. If validation grows complex, propose:
//   "ADR: introduce a form/validation library for apps/web".

export function Picker() {
  return (
    <form className="space-y-3 max-w-md">
      <label className="block text-sm">
        <span className="block font-medium">Remit date</span>
        <select className="mt-1 w-full rounded border px-2 py-1" disabled>
          <option>-- placeholder --</option>
        </select>
      </label>
      <label className="block text-sm">
        <span className="block font-medium">Servicer</span>
        <select className="mt-1 w-full rounded border px-2 py-1" disabled>
          <option>-- placeholder --</option>
        </select>
      </label>
      <button
        type="submit"
        disabled
        className="rounded bg-gray-300 px-4 py-2 text-sm text-gray-600"
      >
        Submit (not wired)
      </button>
    </form>
  );
}
