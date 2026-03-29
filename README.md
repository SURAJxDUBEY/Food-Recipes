# LeftoverChef

Recipe app: `index.html` (UI) + FastAPI (`server.py`) + `api/*.py` (Vercel).

## Repo layout (exact names)

```
.
├── api/
│   ├── health.py      # /api/health (uptime JSON)
│   ├── ingredients.py
│   ├── recipes.py
│   └── search.py
├── index.html         # main UI — open this at / on Vercel
├── server.py
├── requirements.txt
├── vercel.json
```

There is **no** `api/index.py` on purpose: a FastAPI `GET /` JSON response was being served at your **homepage** `/` on Vercel. The UI must be `index.html` at `/`.

### Open the website

Use **only** the site root (no `/api`):

`https://YOUR-PROJECT.vercel.app/`

- **API check:** `https://…vercel.app/api/health` → `{"ok":true,...}`
- **Ingredients:** `https://…vercel.app/api/ingredients`

## Local run

```bash
pip install -r requirements.txt
uvicorn server:app --reload --port 8000
```

Open `index.html` in a browser (or Live Server). API: `http://127.0.0.1:8000` (health: `/api/health`).

## Git & Vercel

```bash
git add .
git commit -m "Deploy LeftoverChef"
git push
```

## Troubleshooting

- [Vercel NOT_FOUND](https://vercel.com/docs/errors/NOT_FOUND)
