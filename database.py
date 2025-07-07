import sqlite3
from typing import List, Tuple, Optional

DB_NAME = 'expenses.db'

def get_connection():
    return sqlite3.connect(DB_NAME)

def init_db():
    conn = get_connection()
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            amount REAL NOT NULL,
            category_id INTEGER,
            date TEXT NOT NULL,
            description TEXT,
            FOREIGN KEY (category_id) REFERENCES categories(id)
        )
    ''')
    conn.commit()
    conn.close()

def add_category(name: str):
    conn = get_connection()
    c = conn.cursor()
    try:
        c.execute('INSERT INTO categories (name) VALUES (?)', (name,))
        conn.commit()
    except sqlite3.IntegrityError:
        pass  # Category already exists
    conn.close()

def get_categories() -> List[Tuple[int, str]]:
    conn = get_connection()
    c = conn.cursor()
    c.execute('SELECT id, name FROM categories')
    categories = c.fetchall()
    conn.close()
    return categories

def add_expense(amount: float, category_id: int, date: str, description: str):
    conn = get_connection()
    c = conn.cursor()
    c.execute('INSERT INTO expenses (amount, category_id, date, description) VALUES (?, ?, ?, ?)',
              (amount, category_id, date, description))
    conn.commit()
    conn.close()

def get_expenses(category_id: Optional[int] = None) -> List[Tuple]:
    conn = get_connection()
    c = conn.cursor()
    if category_id:
        c.execute('SELECT e.id, e.amount, c.name, e.date, e.description FROM expenses e JOIN categories c ON e.category_id = c.id WHERE category_id = ? ORDER BY date DESC', (category_id,))
    else:
        c.execute('SELECT e.id, e.amount, c.name, e.date, e.description FROM expenses e JOIN categories c ON e.category_id = c.id ORDER BY date DESC')
    expenses = c.fetchall()
    conn.close()
    return expenses 