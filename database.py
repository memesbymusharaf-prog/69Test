import json
import os
from datetime import datetime
from typing import List, Tuple, Optional

USERS_FILE = "users.json"
PLANS_FILE = "plans.json"

def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_users(users):
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f, indent=4)

def load_plans():
    if os.path.exists(PLANS_FILE):
        with open(PLANS_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_plans(plans):
    with open(PLANS_FILE, 'w') as f:
        json.dump(plans, f, indent=4)

def setup_database():
    load_users()
    load_plans()

def create_connection_pool():
    setup_database()
    return True

def close_connection_pool():
    pass

def setup_custom_gates_table():
    pass

def get_or_create_user(user_id: int, username: str = None):
    users = load_users()
    user_id_str = str(user_id)
    
    if user_id_str in users:
        u = users[user_id_str]
        return (u.get('username', username), u.get('joined_at', str(datetime.now())), u.get('tier', 'Free'), u.get('credits', 100))
    
    users[user_id_str] = {
        'username': username or str(user_id),
        'joined_at': str(datetime.now()),
        'tier': 'Free',
        'credits': 100,
        'proxies': [],
        'last_daily': None
    }
    save_users(users)
    return (username or str(user_id), str(datetime.now()), 'Free', 100)

def get_user_credits(user_id: int) -> int:
    users = load_users()
    user_id_str = str(user_id)
    if user_id_str in users:
        credits = users[user_id_str].get('credits', 100)
        if has_active_plan(user_id):
            return float('inf')
        return credits
    return 100

def update_user_credits(user_id: int, change: int) -> bool:
    users = load_users()
    user_id_str = str(user_id)
    if user_id_str not in users:
        get_or_create_user(user_id)
    users[user_id_str]['credits'] = users[user_id_str].get('credits', 100) + change
    save_users(users)
    return True

def get_user_plan(user_id: int) -> Optional[tuple]:
    plans = load_plans()
    user_id_str = str(user_id)
    if user_id_str in plans:
        p = plans[user_id_str]
        return (p.get('tier'), p.get('expiry_date'))
    return None

def update_user_plan(user_id: int, tier: str, expiry_date) -> bool:
    plans = load_plans()
    users = load_users()
    user_id_str = str(user_id)
    
    plans[user_id_str] = {
        'tier': tier,
        'expiry_date': expiry_date.strftime('%Y-%m-%d %H:%M:%S') if expiry_date else None
    }
    save_plans(plans)
    
    if user_id_str in users:
        users[user_id_str]['tier'] = tier
        save_users(users)
    
    return True

def has_active_plan(user_id: int) -> bool:
    plan = get_user_plan(user_id)
    if not plan:
        return False
    tier, expiry_date = plan
    if expiry_date:
        expiry = datetime.strptime(expiry_date, '%Y-%m-%d %H:%M:%S')
        if datetime.now() > expiry:
            return False
    return tier in ['Basic', 'Pro', 'Elite']

def get_all_active_plans() -> List[tuple]:
    plans = load_plans()
    from datetime import datetime
    result = []
    for user_id, p in plans.items():
        tier = p.get('tier')
        expiry_date = p.get('expiry_date')
        if expiry_date:
            expiry = datetime.strptime(expiry_date, '%Y-%m-%d %H:%M:%S')
            if datetime.now() > expiry:
                continue
        result.append((int(user_id), tier, expiry_date))
    return result

def get_user_proxies(user_id: int) -> List[str]:
    users = load_users()
    user_id_str = str(user_id)
    if user_id_str in users:
        return users[user_id_str].get('proxies', [])
    return []

def add_user_proxy(user_id: int, proxy: str) -> tuple:
    users = load_users()
    user_id_str = str(user_id)
    if user_id_str not in users:
        get_or_create_user(user_id)
    
    proxies = users[user_id_str].get('proxies', [])
    if proxy in proxies:
        return False, "Proxy already exists"
    if len(proxies) >= 10:
        return False, "Proxy limit reached (10)"
    
    proxies.append(proxy)
    users[user_id_str]['proxies'] = proxies
    save_users(users)
    return True, "Proxy added"

def remove_user_proxies(user_id: int, count: int) -> tuple:
    users = load_users()
    user_id_str = str(user_id)
    if user_id_str not in users:
        return False, "User not found"
    
    proxies = users[user_id_str].get('proxies', [])
    if not proxies:
        return False, "No proxies to remove"
    
    if count == -1:
        removed = len(proxies)
        proxies = []
    else:
        removed = min(count, len(proxies))
        proxies = proxies[removed:]
    
    users[user_id_str]['proxies'] = proxies
    save_users(users)
    return True, f"Removed {removed} proxies"

def get_random_user_proxy(user_id: int):
    proxies = get_user_proxies(user_id)
    import random
    return random.choice(proxies) if proxies else None

def load_users():
    return load_users()

def save_users(users):
    save_users(users)
