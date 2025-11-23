from __future__ import annotations

import io
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional
from uuid import uuid4

import pandas as pd
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

app = FastAPI(title="Excel Conversion Service")


class TransformationRule(str, Enum):
    uppercase = "uppercase"
    lowercase = "lowercase"
    trim = "trim"
    dedupe = "dedupe"


class ExportFormat(str, Enum):
    csv = "csv"
    xlsx = "xlsx"


class UploadPreview(BaseModel):
    session_id: str = Field(..., description="Identifier for the uploaded file session")
    filename: str
    columns: List[str]
    rows: List[Dict[str, Any]]
    total_rows: int
    created_at: datetime


class TransformRequest(BaseModel):
    rules: List[TransformationRule] = Field(
        default_factory=list,
        description="List of transformation rules to apply in order",
    )


class LabelRequest(BaseModel):
    rename: Dict[str, str] = Field(
        default_factory=dict,
        description="Mapping of existing column name to the desired label",
    )


class CellUpdate(BaseModel):
    row: int = Field(..., ge=0, description="Zero-based row index to update")
    column: str = Field(..., description="Column name to update")
    value: Any


class EditRequest(BaseModel):
    updates: List[CellUpdate] = Field(
        default_factory=list, description="One or more inline cell edits"
    )


class HistoryEntry(BaseModel):
    action: str
    detail: Dict[str, Any]
    ts: datetime


class SessionSummary(BaseModel):
    session_id: str
    filename: str
    created_at: datetime
    total_rows: int
    columns: List[str]


class PreviewResponse(BaseModel):
    session: SessionSummary
    rows: List[Dict[str, Any]]
    history: List[HistoryEntry]


class SessionState:
    def __init__(self, filename: str, df: pd.DataFrame):
        self.filename = filename
        self.original_df = df.copy()
        self.current_df = df
        self.created_at = datetime.utcnow()
        self.history: List[HistoryEntry] = []
        self.undo_stack: List[pd.DataFrame] = []
        self.backups: List[bytes] = []

    @property
    def summary(self) -> SessionSummary:
        return SessionSummary(
            session_id="",
            filename=self.filename,
            created_at=self.created_at,
            total_rows=len(self.current_df.index),
            columns=list(self.current_df.columns),
        )

    def snapshot(self) -> None:
        self.undo_stack.append(self.current_df.copy())

    def record(self, action: str, detail: Dict[str, Any]) -> None:
        entry = HistoryEntry(action=action, detail=detail, ts=datetime.utcnow())
        self.history.append(entry)
        if len(self.history) > 50:
            self.history.pop(0)

    def backup(self) -> None:
        buffer = io.BytesIO()
        self.current_df.to_csv(buffer, index=False)
        self.backups.append(buffer.getvalue())
        if len(self.backups) > 5:
            self.backups.pop(0)


SESSIONS: Dict[str, SessionState] = {}
SUPPORTED_EXTENSIONS = {".xlsx", ".xls", ".csv"}


def _deserialize(file_name: str, content: bytes) -> pd.DataFrame:
    ext = Path(file_name).suffix.lower()
    if ext not in SUPPORTED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Unsupported file type")

    try:
        if ext == ".csv":
            return pd.read_csv(io.BytesIO(content))
        return pd.read_excel(io.BytesIO(content))
    except Exception as exc:  # pragma: no cover - serialization layer
        raise HTTPException(status_code=400, detail=f"Failed to parse file: {exc}")


def _normalize_records(df: pd.DataFrame, limit: int = 20) -> List[Dict[str, Any]]:
    limited = df.head(limit).where(pd.notnull(df), None)
    return [dict(row) for row in limited.to_dict(orient="records")]


def _get_session(session_id: str) -> SessionState:
    if session_id not in SESSIONS:
        raise HTTPException(status_code=404, detail="Session not found")
    return SESSIONS[session_id]


@app.get("/health")
def health() -> Dict[str, str]:
    return {"service": "excel-converter", "status": "ok", "ts": datetime.utcnow().isoformat()}


@app.post("/upload", response_model=UploadPreview)
async def upload(file: UploadFile = File(...)) -> UploadPreview:
    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="Uploaded file is empty")

    df = _deserialize(file.filename, content)
    session_id = uuid4().hex
    state = SessionState(filename=file.filename, df=df)
    SESSIONS[session_id] = state
    state.record("upload", {"filename": file.filename, "rows": len(df.index)})
    state.backup()

    return UploadPreview(
        session_id=session_id,
        filename=file.filename,
        columns=list(df.columns),
        rows=_normalize_records(df),
        total_rows=len(df.index),
        created_at=state.created_at,
    )


@app.get("/sessions/{session_id}/preview", response_model=PreviewResponse)
def preview(session_id: str, limit: int = 20) -> PreviewResponse:
    state = _get_session(session_id)
    summary = state.summary.model_copy(update={"session_id": session_id})
    return PreviewResponse(
        session=summary,
        rows=_normalize_records(state.current_df, limit=limit),
        history=state.history,
    )


@app.post("/sessions/{session_id}/transform", response_model=PreviewResponse)
def transform(session_id: str, req: TransformRequest):
    state = _get_session(session_id)
    state.snapshot()
    df = state.current_df.copy()

    for rule in req.rules:
        if rule == TransformationRule.uppercase:
            df = df.applymap(lambda v: v.upper() if isinstance(v, str) else v)
        elif rule == TransformationRule.lowercase:
            df = df.applymap(lambda v: v.lower() if isinstance(v, str) else v)
        elif rule == TransformationRule.trim:
            df = df.applymap(lambda v: v.strip() if isinstance(v, str) else v)
        elif rule == TransformationRule.dedupe:
            df = df.drop_duplicates().reset_index(drop=True)

    state.current_df = df
    state.record("transform", {"rules": [r.value for r in req.rules]})
    state.backup()
    return preview(session_id)


@app.post("/sessions/{session_id}/label", response_model=PreviewResponse)
def label(session_id: str, req: LabelRequest):
    state = _get_session(session_id)
    unknown = [c for c in req.rename if c not in state.current_df.columns]
    if unknown:
        raise HTTPException(status_code=400, detail=f"Unknown columns: {', '.join(unknown)}")

    if not req.rename:
        return preview(session_id)

    state.snapshot()
    state.current_df = state.current_df.rename(columns=req.rename)
    state.record("label", {"rename": req.rename})
    state.backup()
    return preview(session_id)


@app.patch("/sessions/{session_id}/cells", response_model=PreviewResponse)
def edit_cells(session_id: str, req: EditRequest):
    state = _get_session(session_id)
    if not req.updates:
        return preview(session_id)

    df = state.current_df
    state.snapshot()
    for update in req.updates:
        if update.column not in df.columns:
            raise HTTPException(status_code=400, detail=f"Unknown column: {update.column}")
        if update.row >= len(df.index):
            raise HTTPException(status_code=400, detail=f"Row {update.row} is out of bounds")
        df.at[update.row, update.column] = update.value

    state.record("edit", {"count": len(req.updates)})
    state.backup()
    return preview(session_id)


@app.post("/sessions/{session_id}/undo", response_model=PreviewResponse)
def undo(session_id: str):
    state = _get_session(session_id)
    if not state.undo_stack:
        raise HTTPException(status_code=400, detail="No previous snapshot to restore")

    state.current_df = state.undo_stack.pop()
    state.record("undo", {"remaining": len(state.undo_stack)})
    state.backup()
    return preview(session_id)


@app.get("/sessions/{session_id}/history", response_model=List[HistoryEntry])
def history(session_id: str):
    state = _get_session(session_id)
    return state.history


@app.get("/sessions/{session_id}/export")
def export(
    session_id: str,
    fmt: ExportFormat = ExportFormat.csv,
    filename: Optional[str] = None,
):
    state = _get_session(session_id)
    buffer = io.BytesIO()

    if fmt == ExportFormat.csv:
        media_type = "text/csv"
        fname = filename or Path(state.filename).stem + ".csv"
        state.current_df.to_csv(buffer, index=False)
    else:
        media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        fname = filename or Path(state.filename).stem + ".xlsx"
        with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
            state.current_df.to_excel(writer, index=False, sheet_name="Sheet1")

    buffer.seek(0)
    state.record("export", {"format": fmt.value, "filename": fname})
    state.backup()
    headers = {"Content-Disposition": f"attachment; filename={fname}"}
    return StreamingResponse(buffer, media_type=media_type, headers=headers)


@app.get("/sessions")
def list_sessions() -> List[SessionSummary]:
    summaries: List[SessionSummary] = []
    for session_id, state in SESSIONS.items():
        summary = state.summary.model_copy(update={"session_id": session_id})
        summaries.append(summary)
    return summaries
