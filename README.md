# LeftoverChef

Recipe search app: `frontend.html` + FastAPI (`server.py`).

## Repo layout (use these exact names)

```
.
├── api/
│   └── index.py      # Vercel serverless entry (imports server:app)
├── frontend.html     # UI (lowercase)
├── server.py         # API + SQLite + seed data
├── requirements.txt
└── vercel.json
```

Do **not** rename `frontend.html` to `FrontEnd.html` — Linux and Vercel are case-sensitive.

## Local run

```bash
pip install -r requirements.txt
uvicorn server:app --reload --port 8000
```

Open `frontend.html` in a browser (or use Live Server). API: `http://localhost:8000`.

## Git

```bash
git init
git add .
git commit -m "Initial LeftoverChef"
```

Create a repo on GitHub, then:

```bash
git remote add origin <your-repo-url>
git branch -M main
git push -u origin main
```

## Vercel (recommended: connect GitHub)

1. Import the GitHub repo in [Vercel](https://vercel.com).
2. Leave defaults; root directory = repo root.
3. Deploy.

Or CLI from this folder:

```bash
npm i -g vercel
vercel login
vercel --prod
```

After deploy, open your site URL; API calls go to `/api/*` (see `frontend.html`).

## Troubleshooting `404 NOT_FOUND`

- Confirm `api/index.py` exists in the repo (folder `api`, file `index.py`).
- Confirm `vercel.json` is committed.
- Redeploy after fixing file names.

See: [Vercel NOT_FOUND](https://vercel.com/docs/errors/NOT_FOUND)
