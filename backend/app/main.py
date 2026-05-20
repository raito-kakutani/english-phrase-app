from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.services.phrase_service import process_phrase_submission


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


@app.get("/api/health")
def healthcheck() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/phrases")
def submit_phrases(payload: PhraseSubmission) -> dict[str, int | str]:
    try:
        return process_phrase_submission(
            japanese=payload.japanese,
            english=payload.english,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
