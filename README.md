# LeftoverChef

Recipe app: `index.html` (UI) + FastAPI (`server.py`) + `api/*.py` (Vercel).

## Repo layout (exact names)

```
.
├── api/
│   ├── index.py
│   ├── ingredients.py
│   ├── recipes.py
│   └── search.py
├── index.html        # main UI — Vercel serves this at /
├── server.py
├── requirements.txt
```

`vercel.json` rewrites `/` → `/index.html` so the homepage is always your UI.

### Open the website (not the API)

In the browser address bar use **only**:

`https://YOUR-PROJECT.vercel.app/`

- **Do not** open `https://…vercel.app/api` — that URL shows **JSON** from the API (normal).
- If you see JSON with `"LeftoverChef API"`, delete **`/api`** from the URL and press Enter.

Do **not** use random casing (`FrontEnd.html`) — Linux/Vercel are case-sensitive.

## Local run

```bash
pip install -r requirements.txt
uvicorn server:app --reload --port 8000
```

Open `index.html` in a browser (or Live Server). API: `http://127.0.0.1:8000`.

## Git & Vercel

```bash
git add .
git commit -m "Deploy LeftoverChef"
git push
```

Import the repo on [Vercel](https://vercel.com), default settings, deploy.

If you ever see **“Due to `builds` existing…”**: your repo or an old deploy still had a `vercel.json` with `"builds"`. This project should **not** use that. Remove `builds` from `vercel.json` or delete `vercel.json` (this layout works without it).

## Troubleshooting

- `404 NOT_FOUND`: ensure all `api/*.py` files are pushed; test `https://YOUR_SITE.vercel.app/api/ingredients` in the browser.
- [Vercel NOT_FOUND](https://vercel.com/docs/errors/NOT_FOUND)
