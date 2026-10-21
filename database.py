import os
import sqlite3
from datetime import date

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "expenses.db")

EXPENSES_COLUMNS = """(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    amount_cents INTEGER NOT NULL,
    category TEXT NOT NULL,
    description TEXT,
    date TEXT NOT NULL
)"""

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS expenses " + EXPENSES_COLUMNS)
    columns = [row[1] for row in cur.execute("PRAGMA table_info(expenses)")]
    if "amount" in columns:
        # Older databases stored the amount as a float in euros.
        cur.execute("DROP TABLE IF EXISTS expenses_new")
        cur.execute("CREATE TABLE expenses_new " + EXPENSES_COLUMNS)
        cur.execute("""
            INSERT INTO expenses_new (id, amount_cents, category, description, date)
            SELECT id, CAST(ROUND(amount * 100) AS INTEGER), category, description, date FROM expenses
        """)
        cur.execute("DROP TABLE expenses")
        cur.execute("ALTER TABLE expenses_new RENAME TO expenses")
    cur.execute("CREATE TABLE IF NOT EXISTS categories (name TEXT PRIMARY KEY COLLATE NOCASE)")
    cur.execute("INSERT OR IGNORE INTO categories (name) SELECT DISTINCT category FROM expenses")
    conn.commit()
    conn.close()

def add_expense(amount_cents, category, description, date_text=None):
    if date_text is None:
        date_text = date.today().isoformat()
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("INSERT OR IGNORE INTO categories (name) VALUES (?)", (category,))
    cur.execute("INSERT INTO expenses (amount_cents, category, description, date) VALUES (?, ?, ?, ?)", (amount_cents, category, description, date_text))
    conn.commit()
    conn.close()

def get_expenses():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT id, amount_cents, category, description, date FROM expenses ORDER BY date DESC, id DESC")
    rows = cur.fetchall()
    conn.close()
    return rows

def get_expense(expense_id):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT id, amount_cents, category, description, date FROM expenses WHERE id = ?", (expense_id,))
    row = cur.fetchone()
    conn.close()
    return row

def update_expense(expense_id, amount_cents, category, description, date_text=None):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("INSERT OR IGNORE INTO categories (name) VALUES (?)", (category,))
    cur.execute("UPDATE expenses SET amount_cents = ?, category = ?, description = ?, date = COALESCE(?, date) WHERE id = ?", (amount_cents, category, description, date_text, expense_id))
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
    cur.execute("SELECT SUM(amount_cents) FROM expenses")
    row = cur.fetchone()
    conn.close()
    return row[0] or 0

def get_total_by_category():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT category, SUM(amount_cents) FROM expenses GROUP BY category")
    rows = cur.fetchall()
    conn.close()
    return rows
