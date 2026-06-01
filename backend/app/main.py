from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.services.phrase_save import process_phrase_submission
from app.services.phrase_get import get_phrases_by_date


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



@app.get("/api/phrases/date/{date}")
def fetch_phrase_by_date(date: str) -> list[dict[str, int | str | None]]:
    try:
        return get_phrases_by_date(date, f"{date}のフレーズはありません。")
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
