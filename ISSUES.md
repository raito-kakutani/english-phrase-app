# Issues

## Issue: Add MySQL support and environment-based DB configuration

### Decision

Use MySQL as the application database instead of SQLite or PostgreSQL.

### Why

- Phrase data will need persistent storage.
- Environment-based configuration is required so local, test, and production settings can differ safely.
- The current backend only exposes a health check and does not yet connect to any database.

### Tasks

- Add a `backend/.env.example` file with MySQL-related variables.
- Define required environment variables such as `MYSQL_HOST`, `MYSQL_PORT`, `MYSQL_USER`, `MYSQL_PASSWORD`, `MYSQL_DATABASE`, or a single `DATABASE_URL`.
- Add Python settings loading for environment variables.
- Add MySQL client and ORM-related dependencies to the backend.
- Implement a database connection layer in the FastAPI app.
- Add an initial schema and migration setup.
- Decide how tables for phrases, translations, and any future user progress data should be modeled.
- Add a startup validation step so the app fails clearly when DB settings are missing or invalid.
- Document local MySQL setup and backend startup steps in `README.md`.

### Suggested Example

```env
MYSQL_HOST=127.0.0.1
MYSQL_PORT=3306
MYSQL_USER=english_app
MYSQL_PASSWORD=change-me
MYSQL_DATABASE=english_phrase_app
```

Or:

```env
DATABASE_URL=mysql+pymysql://english_app:change-me@127.0.0.1:3306/english_phrase_app
```
