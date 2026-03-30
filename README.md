# 🍳 Leftover Chef

> Tell it what's in your fridge — it tells you what to cook.

No AI API needed. All recipe matching is done against a built-in SQLite database of 30+ recipes.

---

## 🗂 Project Structure

```
leftover-chef/
├── api/
│   └── index.py        ← Flask app (Vercel looks here automatically)
├── templates/
│   └── index.html
├── static/
│   ├── css/style.css
│   └── js/main.js
├── requirements.txt
├── vercel.json
└── .gitignore
```

---

## 🚀 Run locally

```bash
pip install -r requirements.txt
python api/index.py
# → http://localhost:5000
```

## ☁️ Deploy to Vercel

```bash
git init && git add . && git commit -m "init"
git remote add origin https://github.com/YOU/leftover-chef.git
git push -u origin main
```

Import on vercel.com → Other framework → Deploy. No environment variables needed.

> **Note:** SQLite resets on Vercel redeploys (ephemeral filesystem). Fine for demos — for persistence use Vercel Postgres.
