# English Phrase App

英語フレーズ学習アプリ。フレーズの登録・検索・学習を行うWebアプリケーションです。

## デモ

- URL:https://englishphrase.app/

## 主な機能

- フレーズの登録（英語と日本語訳）
- 日付けごとのフレーズの参照

## 技術スタック

- Backend: Python / FastAPI
- Frontend: HTML / CSS / JavaScript（静的ファイル）
- Database: MySQL
- Infra: AWS (EC2)
- CI: GitHub Actions


## ローカル環境のセットアップ

### バックエンド

```powershell
cd backend
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

起動後: `http://127.0.0.1:8000`

### フロントエンド

```powershell
cd frontend
python -m http.server 3000
```

起動後: `http://127.0.0.1:3000`


