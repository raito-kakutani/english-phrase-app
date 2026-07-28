from fastapi import Depends, FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.services.phrase_save import process_phrase_submission
from app.services.phrase_get import get_phrases_by_date
from app.services.user_signup import create_user
from app.services.user_login import authenticate_user
from app.services.session import (
    SESSION_LIFETIME_SECONDS,
    delete_session,
    get_user_id_for_token,
)


app = FastAPI(title="English Phrase App API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://englishphrase.app",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SESSION_COOKIE_NAME = "session_token"


def get_current_user_id(request: Request) -> int:
    session_token = request.cookies.get(SESSION_COOKIE_NAME)
    if session_token is None:
        raise HTTPException(status_code=401, detail="ログインが必要です。")

    try:
        user_id = get_user_id_for_token(session_token)
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    if user_id is None:
        raise HTTPException(status_code=401, detail="ログインが必要です。")

    return user_id


class SignupRequest(BaseModel):
    email: str
    password: str
    first_name: str | None = None
    last_name: str | None = None


class LoginRequest(BaseModel):
    email: str
    password: str


class PhraseSubmission(BaseModel):
    japanese: str
    english: str


@app.post("/api/auth/signup")
def signup(payload: SignupRequest) -> dict[str, int | str]:
    try:
        return create_user(
            email=payload.email,
            password=payload.password,
            first_name=payload.first_name,
            last_name=payload.last_name,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.post("/api/auth/login")
def login(payload: LoginRequest, response: Response) -> dict[str, int | str]:
    try:
        result = authenticate_user(email=payload.email, password=payload.password)
    except ValueError as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    response.set_cookie(
        key=SESSION_COOKIE_NAME,
        value=result["session_token"],
        max_age=SESSION_LIFETIME_SECONDS,
        httponly=True,
        secure=True,
        samesite="lax",
        path="/",
    )
    return {"status": "logged_in", "user_id": result["user_id"]}


@app.post("/api/auth/logout")
def logout(request: Request, response: Response) -> dict[str, str]:
    session_token = request.cookies.get(SESSION_COOKIE_NAME)
    if session_token is not None:
        try:
            delete_session(session_token)
        except RuntimeError as exc:
            raise HTTPException(status_code=500, detail=str(exc)) from exc

    response.delete_cookie(SESSION_COOKIE_NAME, path="/")
    return {"status": "logged_out"}


@app.get("/api/auth/me")
def me(user_id: int = Depends(get_current_user_id)) -> dict[str, int]:
    return {"user_id": user_id}


@app.post("/api/phrases")
def submit_phrases(
    payload: PhraseSubmission, user_id: int = Depends(get_current_user_id)
) -> dict[str, int | str]:
    try:
        return process_phrase_submission(
            japanese=payload.japanese,
            english=payload.english,
            user_id=user_id,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc



@app.get("/api/phrases/date/{date}")
def fetch_phrase_by_date(
    date: str, user_id: int = Depends(get_current_user_id)
) -> list[dict[str, int | str | None]]:
    try:
        return get_phrases_by_date(
            date, f"{date}のフレーズはありません。", user_id=user_id
        )
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
