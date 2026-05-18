# apps/web — Stage 2 frontend (skeleton, P2.4)

Next.js 14 App Router scaffold for the Stage 2 validation-report UI.
**This is a skeleton only.** Real screens land in todo `d-ui-core-screens`.

## Run

```bash
cd apps/web
cp .env.local.example .env.local   # then edit if needed
npm install
npm run dev      # http://localhost:3000
npm run build    # production build + typecheck
npm run lint     # next lint (eslint config is created on first run)
```

The FastAPI backend is expected at `NEXT_PUBLIC_API_BASE`
(default `http://localhost:8000`).

## HARD RESTRAINT — library policy

Per `docs/stage2/11.0-architecture.en.md` § 5 and `AGENTS.md` § 6.14, this
app starts with the **minimum** dependency set:

| Allowed | Why |
|---|---|
| `next@~14.2` | App Router, pinned by architecture § 2 |
| `react@^18.2`, `react-dom@^18.2` | Next.js peer |
| `typescript@^5.4` | Types |
| `tailwindcss@^3.4` (+ `postcss`, `autoprefixer`) | Styling |
| `reactflow@^11` | The single graph library for lineage view |

**NOT allowed** without an ADR in `docs/decisions.md`:

- State managers: Redux, Zustand, Jotai, Recoil, XState
- Data fetching: React Query, SWR, RTK Query, Apollo, tRPC
- Form libs: react-hook-form, formik, zod-form
- UI kits: MUI, Chakra, Ant Design, Mantine, shadcn (as a dep)
- Anything else not in the table above

If a real need arises, add a TODO comment in the file proposing the ADR
title (e.g. `// TODO: ADR — introduce React Query for apps/web caching`)
and surface it in the PR description. **Do not silently add the dep.**

## Layout

```
apps/web/
├── app/
│   ├── layout.tsx                                # root + nav
│   ├── globals.css                               # tailwind entry
│   ├── page.tsx                                  # picker (placeholder)
│   └── runs/[runId]/
│       ├── page.tsx                              # run details (placeholder)
│       ├── sheets/[sheetName]/page.tsx           # per-sheet (placeholder)
│       ├── lineage/page.tsx                      # react-flow demo (placeholder)
│       └── diff/page.tsx                         # diff viewer (placeholder)
├── components/
│   ├── Nav.tsx
│   └── Picker.tsx
├── lib/api.ts                                    # typed fetch wrapper
├── next.config.mjs
├── tailwind.config.ts
├── postcss.config.mjs
├── tsconfig.json
└── package.json
```

Every placeholder page is marked with a `// TODO: d-ui-core-screens` comment.
