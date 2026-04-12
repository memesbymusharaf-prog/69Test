
import sqlite3
import json
import random
from datetime import datetime
from typing import List, Tuple

DB_FILE = "bot_database.db"

def get_db():
    return sqlite3.connect(DB_FILE)

def setup_database():
    conn = get_db()
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        username TEXT,
        joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        tier TEXT DEFAULT 'Free',
        credits INTEGER DEFAULT 250,
        proxies TEXT DEFAULT '[]'
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS user_plans (
        user_id INTEGER PRIMARY KEY,
        tier TEXT NOT NULL,
        expiry_date TIMESTAMP
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS custom_gates (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        gate_name TEXT UNIQUE,
        site_url TEXT,
        created_by INTEGER
    )''')
    conn.commit()
    conn.close()

def setup_custom_gates_table():
    setup_database()

def create_connection_pool():
    setup_database()
    return True

def close_connection_pool():
    pass

def get_or_create_user(user_id: int, username: str):
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT username, joined_at, tier, credits FROM users WHERE user_id = ?", (user_id,))
    r = c.fetchone()
    if r:
        conn.close()
        return r
    c.execute("INSERT INTO users (user_id, username, tier, credits) VALUES (?, ?, ?, ?)", 
              (user_id, username, "Free", 250))
    conn.commit()
    c.execute("SELECT username, joined_at, tier, credits FROM users WHERE user_id = ?", (user_id,))
    r = c.fetchone()
    conn.close()
    return r

def get_user_credits(user_id: int):
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT credits FROM users WHERE user_id = ?", (user_id,))
    r = c.fetchone()
    conn.close()
    return r[0] if r else 250

def update_user_credits(user_id: int, change: int) -> bool:
    conn = get_db()
    c = conn.cursor()
    c.execute("UPDATE users SET credits = credits + ? WHERE user_id = ?", (change, user_id))
    conn.commit()
    conn.close()
    return True

def get_user_proxies(user_id: int) -> List[str]:
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT proxies FROM users WHERE user_id = ?", (user_id,))
    r = c.fetchone()
    conn.close()
    return json.loads(r[0]) if r and r[0] else []

def add_user_proxy(user_id: int, proxy: str) -> Tuple[bool, str]:
    p = get_user_proxies(user_id)
    if proxy in p:
        return False, "Proxy exists"
    if len(p) >= 10:
        return False, "Limit 10"
    p.append(proxy)
    conn = get_db()
    c = conn.cursor()
    c.execute("UPDATE users SET proxies = ? WHERE user_id = ?", (json.dumps(p), user_id))
    conn.commit()
    conn.close()
    return True, "Proxy added"

def remove_user_proxies(user_id: int, count: int) -> Tuple[bool, str]:
    p = get_user_proxies(user_id)
    if not p:
        return False, "No proxies"
    if count == -1:
        rm = len(p)
        p = []
    else:
        rm = min(count, len(p))
        p = p[rm:]
    conn = get_db()
    c = conn.cursor()
    c.execute("UPDATE users SET proxies = ? WHERE user_id = ?", (json.dumps(p), user_id))
    conn.commit()
    conn.close()
    return True, f"Removed {rm} proxies"

def get_random_user_proxy(user_id: int):
    p = get_user_proxies(user_id)
    return random.choice(p) if p else None

def load_users():
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT user_id, username, joined_at, tier, credits, proxies FROM users")
    rows = c.fetchall()
    conn.close()
    u = {}
    for row in rows:
        u[str(row[0])] = {
            'username': row[1],
            'joined_at': row[2],
            'tier': row[3],
            'credits': row[4],
            'proxies': json.loads(row[5]) if row[5] else []
        }
    return u

def save_users(users):
    pass

def add_custom_gate(gate_name: str, site_url: str, user_id: int) -> bool:
    conn = get_db()
    c = conn.cursor()
    try:
        c.execute("INSERT INTO custom_gates (gate_name, site_url, created_by) VALUES (?, ?, ?)",
                  (gate_name, site_url, user_id))
        conn.commit()
        conn.close()
        return True
    except:
        conn.close()
        return False

def get_custom_gate_url(gate_name: str):
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT site_url FROM custom_gates WHERE gate_name = ?", (gate_name,))
    r = c.fetchone()
    conn.close()
    return r[0] if r else None

def get_all_gates():
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT gate_name, site_url FROM custom_gates")
    r = c.fetchall()
    conn.close()
    return r

def delete_custom_gate(gate_name: str) -> bool:
    conn = get_db()
    c = conn.cursor()
    c.execute("DELETE FROM custom_gates WHERE gate_name = ?", (gate_name,))
    conn.commit()
    a = c.rowcount
    conn.close()
    return a > 0
