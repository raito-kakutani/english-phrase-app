from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.services.phrase_service import (
    get_today_phrase,
    get_yesterday_phrase,
    process_phrase_submission,
)


app = FastAPI(title="English Phrase App API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class PhraseSubmission(BaseModel):
    japanese: str
    english: str


@app.post("/api/phrases")
def submit_phrases(payload: PhraseSubmission) -> dict[str, int | str]:
    try:
        return process_phrase_submission(
            japanese=payload.japanese,
            english=payload.english,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.get("/api/phrases/today")
def fetch_today_phrase() -> dict[str, int | str | None]:
    try:
        return get_today_phrase()
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.get("/api/phrases/yesterday")
def fetch_yesterday_phrase() -> dict[str, int | str | None]:
    try:
        return get_yesterday_phrase()
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
