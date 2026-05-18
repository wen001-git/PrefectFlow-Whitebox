import Link from "next/link";

export function Nav() {
  return (
    <nav className="border-b bg-gray-50">
      <div className="mx-auto flex max-w-6xl items-center gap-6 px-4 py-3 text-sm">
        <span className="font-semibold">PrefectFlow Whitebox</span>
        <Link href="/" className="text-blue-600 hover:underline">
          Picker
        </Link>
        <Link href="/runs/_demo" className="text-blue-600 hover:underline">
          Runs
        </Link>
      </div>
    </nav>
  );
}
