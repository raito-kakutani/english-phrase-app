# english-phrase-app

English phrase learning app.

## Project notes

- See `ISSUES.md` for pending implementation items, including planned MySQL support.

## Structure

- `frontend`
- `backend`

## Backend setup

The repository now includes a local venv folder at `backend/.venv-dev`.

### PowerShell

```powershell
cd backend
.\.venv-dev\Scripts\python.exe -m uvicorn app.main:app --reload
```

Backend URL: `http://127.0.0.1:8000`

### Notes

- This environment currently uses system site packages because `pip` bootstrap failed during `venv` creation on this machine.
- If you want to inspect the venv Python directly: `.\.venv-dev\Scripts\python.exe --version`

## Frontend setup

The frontend is plain static files. Start a local web server from `frontend`.

```powershell
cd frontend
python -m http.server 3000
```

Frontend URL: `http://127.0.0.1:3000`
