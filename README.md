# Packaging Compliance Scanner

Smart India Hackathon 2026 (SIH26034), team project.

The system reads label text from photos of product packages and checks the mandatory declarations against Legal Metrology (Packaged Commodities) rules. It returns a pass, fail or review verdict for each field, keeps a history of scans, and shows the results on a web dashboard.

## How it works

```
package photo(s) -> OCR module -> package classifier -> rule engine -> verdict per field
                    (ocr/)        (rules/)               (rules/)       + ingredient check
                                                                        + MRP tampering check
                                       |
                          FastAPI backend (backend/) -> SQLite database
                                       |
                          React dashboard (frontend-dashboard/)
```

## Modules

| Folder | What it does |
| --- | --- |
| `ocr/` | Reads text from package photos with EasyOCR, with image preprocessing, quality checks and multi-image aggregation. See [ocr/README.md](ocr/README.md) |
| `rules/` | Classifies the package type, extracts and validates label fields, checks restricted ingredients, and checks the MRP region for tampering. Rules live in `rules/rules.json` |
| `backend/` | FastAPI application and database models |
| `frontend-dashboard/` | React (Vite) dashboard for scan history and analytics |

Fields checked: manufacturer information, generic name, net quantity, manufacturing date, MRP (maximum retail price), consumer care details, unit sale price and country of origin.

## Running it

Requires Python 3.10+ and Node.js.

**Backend** (from the repository root):

```bash
python -m venv venv
source venv/bin/activate          # on Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn backend.main:app --reload
```

The API runs at `http://localhost:8000`. EasyOCR downloads its language models the first time it runs.

**Frontend:**

```bash
cd frontend-dashboard
npm install
cp .env.example .env              # set VITE_API_BASE_URL if the backend is not on localhost:8000
npm run dev
```

If the backend is not reachable, the dashboard falls back to mock data and shows a banner saying so.

## API

| Method | Endpoint | Purpose |
| --- | --- | --- |
| POST | `/scan` | Upload one package image; returns package type, overall verdict and per-field results |
| POST | `/batch` | Upload several images of one product (`product_id` plus `files`) |
| GET | `/history` | List past scans, newest first |
| GET | `/scans/{scan_id}` | Details of one scan |

```bash
curl -X POST http://localhost:8000/scan -F "file=@backend/test_image.jpg"
```

## Limitations

- This is a hackathon prototype, not legal advice.
- OCR accuracy depends on photo quality, and OCR models are not fine-tuned.
- Accuracy has not been measured on a labelled test set.
- Some cases are marked for manual review instead of being judged automatically.

