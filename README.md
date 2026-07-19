# english-phrase-app

英語フレーズ学習アプリ。

## プロジェクトメモ

- 未対応の実装項目(MySQL対応の予定を含む)は `ISSUES.md` を参照。

## 構成

- `frontend`
- `backend`

## バックエンドのセットアップ

このリポジトリには `backend/.venv-dev` にローカルのvenvフォルダが含まれている。

### PowerShell

```powershell
cd backend
.\.venv-dev\Scripts\python.exe -m uvicorn app.main:app --reload
```

バックエンドURL: `http://127.0.0.1:8000`

### 補足

- このマシンでは`venv`作成時に`pip`のブートストラップが失敗したため、現在この環境ではシステムのsite-packagesを使用している。
- venvのPythonを直接確認したい場合: `.\.venv-dev\Scripts\python.exe --version`

### テスト

```powershell
cd backend
.\venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\venv\Scripts\python.exe -m pytest
```

## フロントエンドのセットアップ

フロントエンドは通常の静的ファイル。`frontend`からローカルWebサーバーを起動する。

```powershell
cd frontend
python -m http.server 3000
```

フロントエンドURL: `http://127.0.0.1:3000`

# AWS
## EC2接続
ssh -i "C:\Users\81802\english-phrase-app-key.pem" ubuntu@56.155.34.145

## バックエンド移動
cd ~/english-phrase-app/backend

## 仮想環境有効化
source venv/bin/activate

## FastAPI起動
uvicorn app.main:app --host 0.0.0.0 --port 8000
