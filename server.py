"""
LeftoverChef Backend — FastAPI + SQLite
========================================
Install: pip install fastapi uvicorn

Run: uvicorn server:app --reload --port 8000
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import os
import sqlite3, json

app = FastAPI(title="LeftoverChef API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Vercel serverless filesystem is read-only except /tmp — SQLite must live there.
DB_PATH = "/tmp/recipes.db" if os.environ.get("VERCEL") else "recipes.db"

# ── DATABASE ──────────────────────────────────────────────────────────────────

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS recipes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            ingredients TEXT NOT NULL,
            steps TEXT NOT NULL,
            time_minutes INTEGER,
            servings INTEGER,
            tags TEXT
        )
    """)
    # Keep recipe names unique so seeding can be safely repeated.
    cur.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_recipes_name ON recipes(name)")
    seed_recipes(cur)
    conn.commit()
    conn.close()

RECIPES_SEED = [
    {
        "name": "Classic Omelette",
        "description": "A fluffy, golden omelette — the ultimate leftover vehicle.",
        "ingredients": ["egg", "butter", "salt", "pepper"],
        "optional": ["cheese", "onion", "tomato", "mushroom", "spinach"],
        "steps": [
            "Crack 2–3 eggs into a bowl, add salt and pepper, and whisk until fully combined.",
            "Melt butter in a non-stick pan over medium heat until foamy.",
            "Pour in the egg mixture and swirl to coat the pan.",
            "When edges begin to set, fold in any fillings you have.",
            "Fold the omelette in half and slide onto a plate. Serve immediately."
        ],
        "time_minutes": 10, "servings": 1,
        "tags": ["breakfast", "quick", "vegetarian"]
    },
    {
        "name": "Fried Rice",
        "description": "The king of leftovers — turns old rice into a complete meal.",
        "ingredients": ["rice", "egg", "soy sauce", "oil", "garlic"],
        "optional": ["carrot", "pea", "onion", "chicken", "shrimp"],
        "steps": [
            "Heat oil in a wok or large pan over high heat.",
            "Add garlic (and onion if available) and stir-fry for 30 seconds.",
            "Add any proteins or vegetables and cook through.",
            "Push everything to the side, scramble the egg in the center.",
            "Add cold cooked rice, breaking up any clumps.",
            "Drizzle soy sauce over everything and toss well. Serve hot."
        ],
        "time_minutes": 15, "servings": 2,
        "tags": ["dinner", "asian", "quick"]
    },
    {
        "name": "Pasta Aglio e Olio",
        "description": "Only 5 ingredients — a Roman classic.",
        "ingredients": ["pasta", "garlic", "olive oil", "salt", "pepper"],
        "optional": ["parsley", "chili flakes", "parmesan"],
        "steps": [
            "Cook pasta in heavily salted boiling water until al dente. Reserve 1 cup pasta water.",
            "Thinly slice 4–6 garlic cloves.",
            "Warm olive oil over low heat. Add garlic and cook until golden.",
            "Add chili flakes if you have them.",
            "Toss drained pasta in the pan with a splash of pasta water to emulsify.",
            "Finish with parsley and parmesan if available."
        ],
        "time_minutes": 20, "servings": 2,
        "tags": ["dinner", "italian", "vegetarian"]
    },
    {
        "name": "Vegetable Stir Fry",
        "description": "Any vegetables, high heat, big flavour.",
        "ingredients": ["oil", "garlic", "soy sauce", "onion"],
        "optional": ["carrot", "broccoli", "bell pepper", "mushroom", "zucchini", "cabbage", "tofu"],
        "steps": [
            "Chop all vegetables into similar-sized pieces for even cooking.",
            "Heat oil in a wok over the highest heat you have.",
            "Add garlic and stir for 20 seconds.",
            "Add harder vegetables first (carrot, broccoli), cook 2 min.",
            "Add softer vegetables (bell pepper, mushroom, zucchini).",
            "Splash in soy sauce and toss everything together.",
            "Serve over rice or noodles if available."
        ],
        "time_minutes": 15, "servings": 2,
        "tags": ["dinner", "vegan", "healthy"]
    },
    {
        "name": "French Toast",
        "description": "Stale bread's most glorious destiny.",
        "ingredients": ["bread", "egg", "milk", "butter", "sugar"],
        "optional": ["cinnamon", "vanilla", "honey", "banana", "berry"],
        "steps": [
            "Whisk together eggs, milk, sugar, and cinnamon in a shallow bowl.",
            "Dip bread slices, letting them soak 20 seconds per side.",
            "Melt butter in a pan over medium heat.",
            "Cook soaked bread 2–3 minutes per side until golden.",
            "Serve with honey, fresh fruit, or any sweet topping you have."
        ],
        "time_minutes": 15, "servings": 2,
        "tags": ["breakfast", "sweet", "vegetarian"]
    },
    {
        "name": "Potato Hash",
        "description": "Crispy golden potatoes with whatever you've got.",
        "ingredients": ["potato", "oil", "salt", "pepper", "onion"],
        "optional": ["egg", "bell pepper", "garlic", "cheese", "sausage"],
        "steps": [
            "Dice potatoes into small cubes.",
            "Heat oil generously in a heavy pan over medium-high heat.",
            "Add potatoes in a single layer. Don't stir — let them crisp for 5 minutes.",
            "Flip and add onion, bell pepper, garlic if available.",
            "Cook another 5–7 minutes until golden and tender.",
            "Make wells and crack in eggs if desired. Cover until eggs set.",
            "Season well and serve hot."
        ],
        "time_minutes": 25, "servings": 2,
        "tags": ["breakfast", "hearty", "vegetarian"]
    },
    {
        "name": "Lentil Soup",
        "description": "Warming, filling, protein-packed one-pot meal.",
        "ingredients": ["lentil", "onion", "garlic", "tomato", "oil", "salt", "cumin"],
        "optional": ["carrot", "spinach", "lemon", "chili", "potato"],
        "steps": [
            "Sauté diced onion in oil until soft and golden, about 5 minutes.",
            "Add garlic and cumin, cook 1 minute until fragrant.",
            "Add rinsed lentils, chopped tomato, and enough water to cover by 3 inches.",
            "Bring to a boil, then simmer 20–25 minutes until lentils are tender.",
            "Add spinach in the last 2 minutes.",
            "Squeeze in lemon juice, adjust seasoning, and serve."
        ],
        "time_minutes": 35, "servings": 4,
        "tags": ["dinner", "vegan", "healthy", "soup"]
    },
    {
        "name": "Banana Pancakes",
        "description": "2-ingredient magic — ripe bananas are the secret.",
        "ingredients": ["banana", "egg"],
        "optional": ["oat", "cinnamon", "vanilla", "honey", "butter"],
        "steps": [
            "Mash 1 ripe banana thoroughly in a bowl.",
            "Whisk in 2 eggs until combined. Add cinnamon and vanilla if you have them.",
            "Add a tablespoon of oats for more structure if desired.",
            "Heat a lightly buttered non-stick pan over medium-low heat.",
            "Drop small spoonfuls of batter — keep them small, they're fragile.",
            "Cook 1–2 minutes per side until set. Serve with honey or fruit."
        ],
        "time_minutes": 15, "servings": 1,
        "tags": ["breakfast", "sweet", "gluten-free"]
    },
    {
        "name": "Tomato Egg Drop",
        "description": "A beloved Chinese home-cooking classic — ready in 10 minutes.",
        "ingredients": ["tomato", "egg", "oil", "salt", "sugar"],
        "optional": ["garlic", "green onion", "soy sauce"],
        "steps": [
            "Cut tomatoes into wedges. Beat eggs with a pinch of salt.",
            "Heat oil in a wok over high heat. Scramble the eggs until just set, then remove.",
            "Add a bit more oil, then stir-fry tomatoes until they release juice.",
            "Add a pinch of sugar to balance acidity.",
            "Return eggs to the pan and toss gently together.",
            "Finish with green onion if available. Serve over rice."
        ],
        "time_minutes": 12, "servings": 2,
        "tags": ["dinner", "asian", "quick"]
    },
    {
        "name": "Garlic Bread",
        "description": "Simple, indulgent, universally loved.",
        "ingredients": ["bread", "butter", "garlic", "salt"],
        "optional": ["parsley", "cheese", "chili flakes"],
        "steps": [
            "Preheat oven to 200°C (390°F).",
            "Mince or crush garlic finely.",
            "Mix garlic into softened butter with a pinch of salt.",
            "Slice bread and spread generously with garlic butter.",
            "Bake for 8–10 minutes until golden and crispy.",
            "Top with cheese in the last 2 minutes if desired."
        ],
        "time_minutes": 15, "servings": 4,
        "tags": ["snack", "vegetarian", "side"]
    },
    {
        "name": "Avocado Toast",
        "description": "Creamy, crunchy, endlessly customisable.",
        "ingredients": ["bread", "avocado", "salt", "lemon"],
        "optional": ["egg", "tomato", "chili flakes", "olive oil", "feta"],
        "steps": [
            "Toast the bread until golden and sturdy.",
            "Halve and pit the avocado. Scoop flesh into a bowl.",
            "Mash with a fork, season with salt and a squeeze of lemon.",
            "Spread generously over toast.",
            "Top with a fried/poached egg, sliced tomato, chili flakes as desired."
        ],
        "time_minutes": 8, "servings": 1,
        "tags": ["breakfast", "healthy", "vegetarian"]
    },
    {
        "name": "Dal Tadka",
        "description": "Indian spiced lentils — comforting and deeply flavoured.",
        "ingredients": ["lentil", "onion", "tomato", "garlic", "cumin", "turmeric", "oil", "salt"],
        "optional": ["ginger", "chili", "coriander", "butter", "lemon"],
        "steps": [
            "Rinse lentils and pressure cook or boil with turmeric until completely soft.",
            "In a separate pan, heat oil and fry cumin seeds until they splutter.",
            "Add chopped onion and cook until golden brown.",
            "Add garlic (and ginger if available) and cook 1 minute.",
            "Add chopped tomato and chili, cook until oil separates.",
            "Pour this tadka over the cooked lentils. Stir and simmer 5 minutes.",
            "Finish with lemon juice and fresh coriander. Serve with rice or roti."
        ],
        "time_minutes": 30, "servings": 3,
        "tags": ["dinner", "indian", "vegan", "healthy"]
    },
]

def seed_recipes(cur):
    inserted = 0
    for r in RECIPES_SEED:
        all_ingredients = list(set(r["ingredients"] + r.get("optional", [])))
        cur.execute("""
            INSERT OR IGNORE INTO recipes (name, description, ingredients, steps, time_minutes, servings, tags)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            r["name"], r["description"],
            json.dumps(all_ingredients),
            json.dumps(r["steps"]),
            r["time_minutes"], r["servings"],
            json.dumps(r.get("tags", []))
        ))
        inserted += cur.rowcount
    print(f"✅ Seeded {inserted} new recipes (total predefined: {len(RECIPES_SEED)}).")

# ── MODELS ────────────────────────────────────────────────────────────────────

class SearchRequest(BaseModel):
    ingredients: List[str]

# ── MATCHING ──────────────────────────────────────────────────────────────────

def match_recipes(user_ingredients: List[str]):
    user_set = set(i.strip().lower() for i in user_ingredients if i.strip())
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM recipes")
    rows = cur.fetchall()
    conn.close()

    exact, suggestions = [], []

    for row in rows:
        recipe_ingredients = set(json.loads(row["ingredients"]))
        have = user_set & recipe_ingredients
        missing = recipe_ingredients - user_set
        ratio = len(have) / len(recipe_ingredients) if recipe_ingredients else 0

        data = {
            "id": row["id"],
            "name": row["name"],
            "description": row["description"],
            "ingredients": json.loads(row["ingredients"]),
            "steps": json.loads(row["steps"]),
            "time_minutes": row["time_minutes"],
            "servings": row["servings"],
            "tags": json.loads(row["tags"]) if row["tags"] else [],
            "match_ratio": round(ratio * 100),
            "have": sorted(list(have)),
            "missing": sorted(list(missing)),
        }

        if ratio == 1.0:
            exact.append(data)
        elif ratio >= 0.45:
            suggestions.append(data)

    exact.sort(key=lambda r: r["time_minutes"])
    suggestions.sort(key=lambda r: -r["match_ratio"])
    return exact, suggestions[:6]

# ── ROUTES ────────────────────────────────────────────────────────────────────

@app.get("/")
def root():
    return {
        "status": "LeftoverChef API running 🍳",
        "hint": "This JSON is the API root. Open the same domain at / (homepage) for the website — not /api.",
    }

@app.get("/recipes")
@app.get("/api/recipes")
def get_all_recipes():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM recipes")
    rows = cur.fetchall()
    conn.close()
    return [
        {
            "id": r["id"], "name": r["name"], "description": r["description"],
            "ingredients": json.loads(r["ingredients"]),
            "steps": json.loads(r["steps"]),
            "time_minutes": r["time_minutes"], "servings": r["servings"],
            "tags": json.loads(r["tags"]) if r["tags"] else [],
        }
        for r in rows
    ]

@app.post("/search")
@app.post("/api/search")
def search_recipes(body: SearchRequest):
    if not body.ingredients:
        return {"exact": [], "suggestions": []}
    exact, suggestions = match_recipes(body.ingredients)
    return {"exact": exact, "suggestions": suggestions, "query_ingredients": body.ingredients}

@app.get("/ingredients")
@app.get("/api/ingredients")
def get_all_ingredients():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT ingredients FROM recipes")
    rows = cur.fetchall()
    conn.close()
    all_ing = set()
    for row in rows:
        all_ing.update(json.loads(row["ingredients"]))
    return sorted(list(all_ing))

@app.on_event("startup")
def startup():
    init_db()
    print("🍳 LeftoverChef ready!")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True) 
