import sqlite3
import pandas as pd

def init_db():
    conn = sqlite3.connect("inventory.db")
    cursor = conn.cursor()
    cursor.execute(
        '''CREATE TABLE IF NOT EXISTS inventory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            quantity INTEGER,
            category TEXT,
            description TEXT,
            status TEXT
        )'''
    )

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT CHECK(role IN ('Admin', 'User')) NOT NULL
    )
''')

    conn.commit()
    conn.close()



def add_item(name, quantity, category, description, status):
    conn = sqlite3.connect("inventory.db") 
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO inventory (name, quantity, category, description, status) VALUES (?, ?, ?, ?, ?)",
        (name, quantity, category, description, status)
    )
    conn.commit()
    conn.close()


def delete_item(item_id):
    conn = sqlite3.connect("inventory.db")
    cursor= conn.cursor()
    cursor.execute("DELETE FROM inventory WHERE id = ?", (item_id,))
    conn.commit()
    conn.close()



def edit_item(item_id, name, quantity, category, description, status):
    conn = sqlite3.connect("inventory.db")
    cursor= conn.cursor()
    cursor.execute("""
        UPDATE inventory
        SET name = ?, quantity = ?, category = ?, description = ?, status= ?
        WHERE id = ?
    """, (name, quantity, category, description, status,  item_id))
    conn.commit()
    conn.close()


def get_all_items():
    conn = sqlite3.connect("inventory.db")
    array =  pd.read_sql_query("SELECT * FROM inventory", conn)
    conn.close()
    return array


def get_item_by_id(item_id):
    conn = sqlite3.connect("inventory.db")
    cursor= conn.cursor()
    cursor.execute("SELECT * FROM inventory WHERE id=?", (item_id,))
    result = cursor.fetchone()
    conn.close
    return result

def create_user(username, password, role):
    conn = sqlite3.connect("inventory.db")
    c = conn.cursor()
    c.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", (username, password, role))
    conn.commit()
    conn.close()

def authenticate(username, password):
    conn = sqlite3.connect("inventory.db")
    c = conn.cursor()
    c.execute("SELECT role FROM users WHERE username = ? AND password = ?", (username, password))
    result = c.fetchone()
    conn.close()
    return result[0] if result else None

