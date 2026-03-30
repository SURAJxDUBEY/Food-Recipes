import os
import json
import sqlite3
from flask import Flask, request, jsonify, render_template, g

app = Flask(__name__)
DATABASE = "leftover_chef.db"

# ── Database helpers ──────────────────────────────────────────────────────────

def get_db():
    db = getattr(g, "_database", None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, "_database", None)
    if db is not None:
        db.close()

def init_db():
    with app.app_context():
        db = get_db()
        db.executescript("""
            CREATE TABLE IF NOT EXISTS recipes (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                title       TEXT NOT NULL,
                description TEXT,
                ingredients TEXT NOT NULL,   -- JSON array of ingredient names (lowercase)
                steps       TEXT NOT NULL,   -- JSON array of step strings
                time        TEXT,
                difficulty  TEXT,
                cuisine     TEXT
            );

            CREATE TABLE IF NOT EXISTS searches (
                id      INTEGER PRIMARY KEY AUTOINCREMENT,
                items   TEXT NOT NULL,
                created DATETIME DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS saved_recipes (
                id        INTEGER PRIMARY KEY AUTOINCREMENT,
                recipe_id INTEGER NOT NULL,
                created   DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(recipe_id) REFERENCES recipes(id)
            );
        """)
        db.commit()
        seed_recipes(db)

def seed_recipes(db):
    """Insert recipes only if the table is empty."""
    count = db.execute("SELECT COUNT(*) FROM recipes").fetchone()[0]
    if count > 0:
        return

    recipes = [
        # ── Egg dishes ──
        ("Scrambled Eggs", "Simple fluffy scrambled eggs",
         ["eggs", "butter", "salt", "pepper"],
         ["Crack eggs into a bowl and whisk well.", "Melt butter in a pan over low heat.", "Pour in eggs and stir gently until just set.", "Season with salt and pepper and serve."],
         "10 mins", "Easy", "Global"),

        ("Omelette", "Classic folded omelette",
         ["eggs", "butter", "salt", "pepper"],
         ["Beat eggs with salt and pepper.", "Melt butter in a non-stick pan.", "Pour eggs in and let the edges set.", "Fold in half and slide onto a plate."],
         "10 mins", "Easy", "French"),

        ("Egg Fried Rice", "Quick fried rice with egg",
         ["eggs", "rice", "oil", "soy sauce", "garlic"],
         ["Heat oil in a wok or pan.", "Add garlic and fry 30 seconds.", "Add cold cooked rice and stir-fry 3 minutes.", "Push rice aside, scramble eggs in the gap.", "Mix everything together and add soy sauce."],
         "15 mins", "Easy", "Chinese"),

        ("Spanish Omelette", "Hearty potato and egg tortilla",
         ["eggs", "potato", "onion", "oil", "salt"],
         ["Slice potato and onion thinly.", "Fry in oil until soft, then drain.", "Beat eggs, mix in potato and onion.", "Cook in an oiled pan until set on the bottom.", "Flip carefully and cook the other side."],
         "30 mins", "Medium", "Spanish"),

        ("Egg Bhurji", "Indian spiced scrambled eggs",
         ["eggs", "onion", "tomatoes", "chilli", "oil", "salt", "cumin"],
         ["Heat oil and sauté onion until golden.", "Add chilli, cumin and tomatoes; cook until mushy.", "Beat eggs and pour in.", "Scramble together and season with salt."],
         "15 mins", "Easy", "Indian"),

        # ── Pasta ──
        ("Pasta Aglio e Olio", "Garlicky pasta with olive oil",
         ["pasta", "garlic", "oil", "salt", "pepper"],
         ["Cook pasta in salted boiling water until al dente.", "Slice garlic and fry in oil until golden.", "Drain pasta, reserve a cup of pasta water.", "Toss pasta with garlic oil, adding pasta water to loosen.", "Season and serve immediately."],
         "20 mins", "Easy", "Italian"),

        ("Tomato Pasta", "Simple tomato sauce pasta",
         ["pasta", "tomatoes", "garlic", "oil", "salt", "basil"],
         ["Cook pasta until al dente.", "Sauté garlic in oil, add chopped tomatoes.", "Simmer sauce 10 minutes, season.", "Toss with drained pasta and fresh basil."],
         "25 mins", "Easy", "Italian"),

        ("Mac and Cheese", "Creamy stovetop mac and cheese",
         ["pasta", "cheese", "butter", "milk", "salt"],
         ["Cook pasta and drain.", "Melt butter in the same pot.", "Add milk and heat gently.", "Add grated cheese and stir until melted.", "Mix in pasta, season and serve."],
         "25 mins", "Easy", "American"),

        ("Pasta Arrabbiata", "Spicy tomato pasta",
         ["pasta", "tomatoes", "garlic", "chilli", "oil", "salt"],
         ["Sauté garlic and chilli in oil.", "Add tomatoes, crush and simmer 15 minutes.", "Cook pasta al dente, drain.", "Toss with sauce and serve."],
         "25 mins", "Easy", "Italian"),

        # ── Rice dishes ──
        ("Plain Vegetable Rice", "Simple spiced vegetable rice",
         ["rice", "onion", "oil", "salt", "cumin", "carrots"],
         ["Heat oil and fry onion and cumin.", "Add diced carrots, cook 3 minutes.", "Add washed rice and double the water.", "Cover and simmer 15 minutes until cooked."],
         "25 mins", "Easy", "Indian"),

        ("Tomato Rice", "Tangy one-pot tomato rice",
         ["rice", "tomatoes", "onion", "garlic", "oil", "salt", "cumin"],
         ["Sauté onion and garlic in oil.", "Add chopped tomatoes and cumin, cook until soft.", "Add rice and twice the water.", "Cover and cook 15 minutes."],
         "25 mins", "Easy", "Indian"),

        ("Chicken Rice", "Simple boiled chicken with seasoned rice",
         ["rice", "chicken", "garlic", "onion", "salt", "oil"],
         ["Simmer chicken with onion, garlic and salt until cooked.", "Remove chicken and use the stock to cook rice.", "Shred chicken and serve over the rice."],
         "40 mins", "Medium", "Asian"),

        # ── Chicken ──
        ("Butter Chicken (Simple)", "Quick pan butter chicken",
         ["chicken", "butter", "tomatoes", "garlic", "onion", "salt", "chilli"],
         ["Marinate chicken in salt and chilli.", "Sauté onion and garlic in butter.", "Add tomatoes and cook to a thick sauce.", "Add chicken pieces and cook through.", "Simmer 10 minutes and serve."],
         "35 mins", "Medium", "Indian"),

        ("Garlic Chicken", "Pan-fried garlic butter chicken",
         ["chicken", "garlic", "butter", "salt", "pepper"],
         ["Season chicken with salt and pepper.", "Sear in butter until golden on both sides.", "Add minced garlic and baste chicken.", "Cook until done through."],
         "25 mins", "Easy", "Global"),

        ("Chicken Stir Fry", "Quick veggie and chicken stir fry",
         ["chicken", "broccoli", "garlic", "soy sauce", "oil", "onion"],
         ["Slice chicken thin and stir-fry in hot oil.", "Remove and fry garlic, onion and broccoli.", "Return chicken, add soy sauce.", "Toss everything and serve."],
         "20 mins", "Easy", "Chinese"),

        ("Chicken Soup", "Simple comforting chicken soup",
         ["chicken", "carrots", "onion", "garlic", "salt", "pepper"],
         ["Simmer chicken with onion and garlic in water.", "Add sliced carrots, cook 20 minutes.", "Remove chicken, shred and return to pot.", "Season with salt and pepper."],
         "45 mins", "Easy", "Global"),

        # ── Vegetable dishes ──
        ("Stir-Fried Broccoli", "Simple garlic broccoli",
         ["broccoli", "garlic", "oil", "soy sauce", "salt"],
         ["Blanch broccoli in salted water 2 minutes.", "Heat oil and fry garlic until fragrant.", "Add broccoli and soy sauce.", "Toss and serve immediately."],
         "15 mins", "Easy", "Chinese"),

        ("Aloo Sabzi", "Indian spiced potatoes",
         ["potato", "onion", "oil", "cumin", "chilli", "salt", "turmeric"],
         ["Dice potato and fry onion in oil.", "Add cumin, chilli and turmeric.", "Add potato and a splash of water.", "Cover and cook until potato is soft."],
         "25 mins", "Easy", "Indian"),

        ("Carrot Soup", "Smooth blended carrot soup",
         ["carrots", "onion", "garlic", "butter", "salt", "pepper"],
         ["Sauté onion and garlic in butter.", "Add diced carrots and enough water to cover.", "Simmer 20 minutes until soft.", "Blend until smooth, season and serve."],
         "30 mins", "Easy", "Global"),

        ("Mixed Veg Curry", "Hearty mixed vegetable curry",
         ["potato", "carrots", "onion", "tomatoes", "garlic", "oil", "chilli", "cumin", "salt", "turmeric"],
         ["Heat oil and fry onion, garlic, cumin.", "Add chilli, turmeric, tomatoes; cook to a paste.", "Add diced vegetables and enough water.", "Cover and simmer 20 minutes until tender."],
         "35 mins", "Medium", "Indian"),

        ("Dal (Lentil Soup)", "Comforting spiced lentils",
         ["lentils", "onion", "tomatoes", "garlic", "oil", "chilli", "cumin", "salt", "turmeric"],
         ["Boil lentils until very soft.", "Fry onion, garlic, cumin in oil.", "Add chilli, turmeric and tomatoes; cook 5 minutes.", "Mix into lentils, simmer together 5 minutes."],
         "30 mins", "Easy", "Indian"),

        # ── Bread / quick bites ──
        ("French Toast", "Sweet egg-soaked toast",
         ["bread", "eggs", "milk", "butter", "sugar"],
         ["Beat eggs with milk and a pinch of sugar.", "Soak bread slices in the mixture.", "Fry in butter until golden on both sides.", "Serve warm."],
         "15 mins", "Easy", "Global"),

        ("Cheese Toast", "Quick grilled cheese toast",
         ["bread", "cheese", "butter"],
         ["Butter the bread slices.", "Top with sliced or grated cheese.", "Grill or toast until cheese melts.", "Serve immediately."],
         "10 mins", "Easy", "Global"),

        ("Bread Upma", "Savoury crumbled bread dish",
         ["bread", "onion", "chilli", "oil", "mustard seeds", "salt"],
         ["Tear bread into pieces.", "Heat oil, add mustard seeds until they pop.", "Fry onion and chilli until soft.", "Add bread pieces, mix well and season."],
         "15 mins", "Easy", "Indian"),

        # ── Soups & stews ──
        ("Tomato Soup", "Classic blended tomato soup",
         ["tomatoes", "onion", "garlic", "butter", "salt", "pepper"],
         ["Sauté onion and garlic in butter.", "Add chopped tomatoes and a cup of water.", "Simmer 15 minutes.", "Blend smooth, season and serve."],
         "25 mins", "Easy", "Global"),

        ("Onion Soup", "Simple caramelised onion soup",
         ["onion", "butter", "salt", "pepper", "bread"],
         ["Slice onions and cook in butter over low heat 30 minutes until caramelised.", "Add water or stock, season.", "Simmer 10 minutes.", "Serve with toasted bread."],
         "45 mins", "Medium", "French"),

        # ── Snacks ──
        ("Poha", "Light flattened rice snack",
         ["poha", "onion", "oil", "mustard seeds", "chilli", "salt", "turmeric"],
         ["Rinse poha and drain.", "Heat oil, pop mustard seeds.", "Fry onion and chilli.", "Add turmeric, then poha; mix gently.", "Season and serve."],
         "15 mins", "Easy", "Indian"),

        ("Banana Pancakes", "Two-ingredient banana pancakes",
         ["banana", "eggs"],
         ["Mash banana in a bowl.", "Beat in eggs until smooth.", "Cook spoonfuls in a non-stick pan.", "Flip when edges are set."],
         "15 mins", "Easy", "Global"),

        ("Peanut Butter Toast", "Quick high-protein snack",
         ["bread", "peanut butter"],
         ["Toast the bread.", "Spread peanut butter generously.", "Serve as is or with banana slices."],
         "5 mins", "Easy", "Global"),

        ("Masala Chai", "Classic spiced Indian tea",
         ["milk", "tea", "sugar", "ginger", "cardamom"],
         ["Boil water with ginger and cardamom.", "Add tea and simmer 2 minutes.", "Add milk and sugar.", "Strain into cups and serve hot."],
         "10 mins", "Easy", "Indian"),
    ]

    db.executemany(
        "INSERT INTO recipes (title, description, ingredients, steps, time, difficulty, cuisine) VALUES (?,?,?,?,?,?,?)",
        [(t, d, json.dumps(i), json.dumps(s), tm, diff, c) for t, d, i, s, tm, diff, c in recipes]
    )
    db.commit()


# ── Matching logic ────────────────────────────────────────────────────────────

def normalise(items):
    """Return a set of lowercase stripped strings."""
    return {item.lower().strip() for item in items}

def match_recipes(user_ingredients):
    """
    For each recipe in the DB, calculate how many of its required ingredients
    the user has. Return two lists:
        - can_make   : all required ingredients present
        - almost     : missing only 1-2 ingredients (with what's missing)
    """
    db = get_db()
    rows = db.execute("SELECT * FROM recipes").fetchall()
    user_set = normalise(user_ingredients)

    can_make = []
    almost   = []

    for row in rows:
        recipe_ings = set(json.loads(row["ingredients"]))
        have   = user_set & recipe_ings
        missing = recipe_ings - user_set

        if not missing:
            can_make.append({
                "id":          row["id"],
                "title":       row["title"],
                "description": row["description"],
                "ingredients": list(recipe_ings),
                "steps":       json.loads(row["steps"]),
                "time":        row["time"],
                "difficulty":  row["difficulty"],
                "cuisine":     row["cuisine"],
                "match_pct":   100,
            })
        elif len(missing) <= 2:
            almost.append({
                "id":          row["id"],
                "title":       row["title"],
                "description": row["description"],
                "ingredients": list(recipe_ings),
                "steps":       json.loads(row["steps"]),
                "time":        row["time"],
                "difficulty":  row["difficulty"],
                "cuisine":     row["cuisine"],
                "missing":     sorted(missing),
                "match_pct":   round(len(have) / len(recipe_ings) * 100),
            })

    # Sort can_make by fewest ingredients (simplest first)
    can_make.sort(key=lambda r: len(r["ingredients"]))
    # Sort almost by fewest missing
    almost.sort(key=lambda r: len(r["missing"]))

    return can_make, almost


# ── Routes ────────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/find-recipes", methods=["POST"])
def find_recipes():
    data  = request.get_json()
    items = data.get("items", [])
    if not items:
        return jsonify({"error": "No ingredients provided"}), 400

    # Save search
    db = get_db()
    db.execute("INSERT INTO searches (items) VALUES (?)", (json.dumps(items),))
    db.commit()

    can_make, almost = match_recipes(items)
    return jsonify({
        "can_make": can_make,
        "almost":   almost,
    })

@app.route("/api/save-recipe", methods=["POST"])
def save_recipe():
    data      = request.get_json()
    recipe_id = data.get("recipe_id")
    if not recipe_id:
        return jsonify({"error": "No recipe_id provided"}), 400
    db = get_db()
    db.execute("INSERT INTO saved_recipes (recipe_id) VALUES (?)", (recipe_id,))
    db.commit()
    return jsonify({"success": True})

@app.route("/api/saved-recipes", methods=["GET"])
def get_saved():
    db = get_db()
    rows = db.execute("""
        SELECT r.id, r.title, r.description, r.time, r.difficulty, r.cuisine,
               r.ingredients, sr.created
        FROM saved_recipes sr
        JOIN recipes r ON sr.recipe_id = r.id
        ORDER BY sr.created DESC
    """).fetchall()
    out = []
    for row in rows:
        out.append({
            "id":          row["id"],
            "title":       row["title"],
            "description": row["description"],
            "time":        row["time"],
            "difficulty":  row["difficulty"],
            "cuisine":     row["cuisine"],
            "ingredients": json.loads(row["ingredients"]),
            "created":     row["created"],
        })
    return jsonify(out)

@app.route("/api/history", methods=["GET"])
def get_history():
    db = get_db()
    rows = db.execute(
        "SELECT id, items, created FROM searches ORDER BY created DESC LIMIT 15"
    ).fetchall()
    return jsonify([
        {"id": r["id"], "items": json.loads(r["items"]), "created": r["created"]}
        for r in rows
    ])

@app.route("/api/all-ingredients", methods=["GET"])
def all_ingredients():
    """Return a deduplicated sorted list of every ingredient in the DB."""
    db = get_db()
    rows = db.execute("SELECT ingredients FROM recipes").fetchall()
    ing_set = set()
    for row in rows:
        for item in json.loads(row["ingredients"]):
            ing_set.add(item.capitalize())
    return jsonify(sorted(ing_set))


# ── Entry point ───────────────────────────────────────────────────────────────

# Always initialise the DB (required for Vercel cold starts)
init_db()

if __name__ == "__main__":
    app.run(debug=True, port=5000)
