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

### Testing

```powershell
cd backend
.\venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\venv\Scripts\python.exe -m pytest
```

## Frontend setup

The frontend is plain static files. Start a local web server from `frontend`.

```powershell
cd frontend
python -m http.server 3000
```

Frontend URL: `http://127.0.0.1:3000`

# AWS
## EC2接続
ssh -i "C:\Users\81802\english-phrase-app-key.pem" ubuntu@56.155.34.145

## バックエンド移動
cd ~/english-phrase-app/backend

## 仮想県境有効化
source venv/bin/activate

## FASTAPI起動
uvicorn app.main:app --host 0.0.0.0 --port 8000