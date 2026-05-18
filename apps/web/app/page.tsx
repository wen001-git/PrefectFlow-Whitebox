import { Picker } from "@/components/Picker";

// TODO: d-ui-core-screens will replace this placeholder with the real picker
// wired against /api/v1/servicers and /api/v1/remit-dates.
export default function HomePage() {
  return (
    <section className="space-y-4">
      <h1 className="text-2xl font-semibold">Run picker</h1>
      <p className="text-sm text-gray-600">
        Placeholder — submission not wired yet. See{" "}
        <code>docs/stage2/6.0-ui-architecture.en.md</code>.
      </p>
      <Picker />
    </section>
  );
}
