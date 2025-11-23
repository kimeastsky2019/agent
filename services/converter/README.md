# Excel Conversion Service

A FastAPI microservice that lets users upload spreadsheets, review and label data, apply common cleanup rules, and export the improved dataset.

## Features
- Upload Excel (`.xlsx`, `.xls`) or CSV files.
- Inline edit cells, rename columns, and apply transformation rules (uppercase, lowercase, trim whitespace, de-duplicate rows).
- Keep a change history with undo snapshots and automatic backups for safety.
- Export the curated dataset as CSV or Excel with custom filenames.

## Key Endpoints
- `POST /upload` – upload a spreadsheet and start a session with a preview.
- `GET /sessions` – list active sessions.
- `GET /sessions/{session_id}/preview` – fetch the latest preview plus history.
- `POST /sessions/{session_id}/transform` – apply transformation rules.
- `POST /sessions/{session_id}/label` – rename columns for labeling.
- `PATCH /sessions/{session_id}/cells` – inline cell edits.
- `POST /sessions/{session_id}/undo` – revert to the previous snapshot.
- `GET /sessions/{session_id}/export` – download the processed file as CSV or Excel.

Run locally with:
```bash
uvicorn main:app --reload --port 8006
```
