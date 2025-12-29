import sqlite3

conn = sqlite3.connect('meal_planner.db')
cur = conn.cursor()

def create_database():
    cur.execute("PRAGMA foreign_keys = ON;")

    cur.execute("""
        CREATE TABLE IF NOT EXISTS recipes (
            id INTEGER PRIMARY KEY,
            name text, 
            link text
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS ingredients (
            ingredient_id INTEGER PRIMARY KEY,
            ingredient TEXT,
            recipe_id INTEGER,
            FOREIGN KEY (recipe_id) REFERENCES recipes (id) ON DELETE CASCADE
        )
    """)

    conn.commit()

conn.close()