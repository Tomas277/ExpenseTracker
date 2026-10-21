import os
import sqlite3
from datetime import date

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "expenses.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            amount REAL NOT NULL,
            category TEXT NOT NULL,
            description TEXT,
            date TEXT NOT NULL
        )
    """)
    cur.execute("CREATE TABLE IF NOT EXISTS categories (name TEXT PRIMARY KEY COLLATE NOCASE)")
    cur.execute("INSERT OR IGNORE INTO categories (name) SELECT DISTINCT category FROM expenses")
    conn.commit()
    conn.close()

def add_expense(amount, category, description, date_text=None):
    if date_text is None:
        date_text = date.today().isoformat()
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("INSERT OR IGNORE INTO categories (name) VALUES (?)", (category,))
    cur.execute("INSERT INTO expenses (amount, category, description, date) VALUES (?, ?, ?, ?)", (amount, category, description, date_text))
    conn.commit()
    conn.close()

def get_expenses():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT id, amount, category, description, date FROM expenses ORDER BY date DESC, id DESC")
    rows = cur.fetchall()
    conn.close()
    return rows

def get_expense(expense_id):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT id, amount, category, description, date FROM expenses WHERE id = ?", (expense_id,))
    row = cur.fetchone()
    conn.close()
    return row

def update_expense(expense_id, amount, category, description, date_text=None):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("INSERT OR IGNORE INTO categories (name) VALUES (?)", (category,))
    cur.execute("UPDATE expenses SET amount = ?, category = ?, description = ?, date = COALESCE(?, date) WHERE id = ?", (amount, category, description, date_text, expense_id))
    conn.commit()
    conn.close()

def delete_expense(expense_id):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
    conn.commit()
    conn.close()

def get_categories():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT name FROM categories ORDER BY name")
    rows = [row[0] for row in cur.fetchall()]
    conn.close()
    return rows

def get_total():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT SUM(amount) FROM expenses")
    row = cur.fetchone()
    conn.close()
    return row[0] or 0

def get_total_by_category():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT category, SUM(amount) FROM expenses GROUP BY category")
    rows = cur.fetchall()
    conn.close()
    return rows
