# 🍳 Leftover Chef

> Tell it what's in your fridge — it tells you what to cook.

No AI API needed. All recipe matching is done against a built-in SQLite database of 30+ recipes.

---

## 🚀 Run locally

```bash
# 1. Clone
git clone https://github.com/YOUR_USERNAME/leftover-chef.git
cd leftover-chef

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate      # macOS/Linux
venv\Scripts\activate         # Windows

# 3. Install (just Flask — nothing else needed)
pip install -r requirements.txt

# 4. Run
python app.py
# → http://localhost:5000
```

The SQLite database and all recipes are created automatically on first run.

---

## ☁️ Deploy to Vercel

```bash
git init && git add . && git commit -m "init"
git remote add origin https://github.com/YOU/leftover-chef.git
git push -u origin main
```

Import on [vercel.com](https://vercel.com) → **Other** framework → Deploy.  
**No environment variables needed.**

> SQLite resets on Vercel redeploys (ephemeral filesystem). Works great for demos. For persistent storage swap to Vercel Postgres.

---

## 🗂 Structure

```
leftover-chef/
├── app.py              # Flask app + recipe DB + matching logic
├── wsgi.py             # Vercel entry point
├── requirements.txt    # Only: flask
├── vercel.json
├── .gitignore
├── templates/index.html
└── static/
    ├── css/style.css
    └── js/main.js
```

## 🛠 Tech Stack

| Layer | Tech |
|---|---|
| Frontend | HTML, CSS, Vanilla JS |
| Backend | Python 3, Flask |
| Database | SQLite (built-in, zero config) |
| AI | None — pure DB matching |
