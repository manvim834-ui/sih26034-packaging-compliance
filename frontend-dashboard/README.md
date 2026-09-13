# LMPC Compliance Scanner — Frontend Scaffold (Theme E)

Scaffold for Theme E: History, Analytics, Export, Admin — plus a placeholder
Scan route so the full nav works end-to-end. Everything currently runs on
mock data in `src/mock/scans.js`.

## Run it

```
npm install
cp .env.example .env   # set VITE_API_BASE_URL if your backend isn't on localhost:8000
npm run dev
```

## Connecting the real backend

History and Analytics now call `GET /history` on the backend (see
`src/api/client.js`). If the backend isn't running or isn't reachable,
the app automatically falls back to mock data and shows a small banner
saying so — so you can keep developing the UI even when the backend is
down, and you'll know which data you're looking at.

Steps to connect it for real:
1. Start the FastAPI backend (Person 3's repo/folder — `/backend` once the
   repo restructure lands).
2. Ask them to add CORS middleware allowing your dev server's origin, or
   the fetch will be blocked by the browser:
   ```python
   from fastapi.middleware.cors import CORSMiddleware
   app.add_middleware(
       CORSMiddleware,
       allow_origins=["http://localhost:5173"],
       allow_methods=["*"],
       allow_headers=["*"],
   )
   ```
3. Set `VITE_API_BASE_URL` in `.env` to wherever it's running (defaults to
   `http://localhost:8000`).
4. Reload — the banner should disappear once real data loads.

`POST /batch` isn't built yet on the backend, so batch upload isn't wired
into the frontend yet either. `/rules` (for the Admin ruleset editor) also
still needs sanity-checking with Person 2 before wiring it up — Admin
still runs on mock data for now.

## Structure

```
src/
  components/    Layout (sidebar nav), VerdictBadge (shared with Theme D),
                 PageHeader, MiniLineChart, MiniBarChart
  pages/         Scan (placeholder), History, Analytics, Admin
  mock/          scans.js — mock data + the proposed API/ruleset schema
  styles/        design tokens (tokens.css) + global styles
```

## Before wiring up real data

Confirm by Day 4, with Person 2 (rules) and Person 3 (backend):
- Exact scan object shape returned by the API
- Whether batches are nested objects or a flat list sharing `batch_id`
- Whether Analytics gets pre-aggregated data or raw scans to compute from
- Exact ruleset JSON schema (field, required, applies_when, validator,
  legal_reference, enabled)

`src/mock/scans.js` has my best-guess schema as a starting point for that
conversation — update it once the real contract is settled, then swap the
mock imports in each page for real API calls.

## Notes

- `VerdictBadge` is meant to be shared with Person 4's Scan screen (Theme D)
  so verdicts look identical everywhere — sync with them before both of you
  build your own versions.
- Charts are hand-rolled SVG (no chart library yet) to keep the scaffold
  dependency-light. Swap in `recharts` or `chart.js` once you want richer
  interactivity (tooltips, animation, etc).
- Export buttons are wired up visually but not functionally yet — add
  `jspdf`/`papaparse` when you get to that part.
- Two schema details are still open questions (see comments in
  `src/mock/scans.js`): the exact non-compliant/needs-review status
  strings, and whether "category" and "package type" are the same field.
  Flag these with Person 2/3 before relying on them too heavily.
