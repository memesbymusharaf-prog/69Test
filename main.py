import os
import json
import time
import requests
import threading
import re
from datetime import datetime
from flask import Flask, request
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

from config import BOT_TOKEN, ADMIN_CHAT_ID, BOT_USERNAME

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

USER_FILE = "users.json"
PROXY_FILE = "proxies.json"
file_lock = threading.Lock()

def load_users():
    with file_lock:
        if os.path.exists(USER_FILE):
            with open(USER_FILE, 'r') as f:
                return json.load(f)
        return {}

def save_users(users):
    with file_lock:
        with open(USER_FILE, 'w') as f:
            json.dump(users, f, indent=4)

def load_proxies():
    with file_lock:
        if os.path.exists(PROXY_FILE):
            with open(PROXY_FILE, 'r') as f:
                return json.load(f)
        return []

def save_proxies(proxies):
    with file_lock:
        with open(PROXY_FILE, 'w') as f:
            json.dump(proxies, f, indent=4)

def test_proxy(proxy_string):
    try:
        proxies = {'http': proxy_string, 'https': proxy_string}
        start = time.time()
        r = requests.get('http://httpbin.org/ip', proxies=proxies, timeout=10)
        elapsed = round((time.time() - start) * 1000)
        return {'live': r.status_code == 200, 'time_ms': elapsed}
    except:
        return {'live': False, 'time_ms': 0}

# ========== CALLBACK HANDLER ==========
@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    chat_id = call.message.chat.id
    data = call.data
    user_id = str(call.from_user.id)
    
    users = load_users()
    if user_id not in users:
        users[user_id] = {
            'plan': 'FREE', 'credits': 100, 'total_checks': 0,
            'total_hits': 0, 'joined': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'last_msg_id': None
        }
        save_users(users)
    
    user_data = users[user_id]
    
    if data == 'plans':
        msg = """<tg-emoji emoji-id="5893321843149902412">✨</tg-emoji> ⊹ <b>Suspecious — Plans</b> <tg-emoji emoji-id="5893376775781617954">👑</tg-emoji> ⊹

   ꒰ <tg-emoji emoji-id="5893402730268987918">🍀</tg-emoji> ꒱ <b>Free</b>
      ˚ <tg-emoji emoji-id="5893255507380014983">📦</tg-emoji> 50 cards/session
      ˚ <tg-emoji emoji-id="5893102202817352158">⏳</tg-emoji> Slow speed
      ˚ <tg-emoji emoji-id="5893473283696759404">💰</tg-emoji> 100 credits

   ꒰ <tg-emoji emoji-id="5384546515551275588">⚡</tg-emoji> ꒱ <b>Basic — $5/week</b>
      ˚ <tg-emoji emoji-id="5893255507380014983">📦</tg-emoji> 500 cards/session
      ˚ <tg-emoji emoji-id="5902432207519093015">⚙️</tg-emoji> Slow + Medium speed
      ˚ <tg-emoji emoji-id="5893473283696759404">💵</tg-emoji> 5,000 credits

   ꒰ <tg-emoji emoji-id="5893185207355315979">🔥</tg-emoji> ꒱ <b>Pro — $15/month</b>
      ˚ <tg-emoji emoji-id="5893255507380014983">📦</tg-emoji> 2,000 cards/session
      ˚ <tg-emoji emoji-id="6041705726206808304">🚀</tg-emoji> Slow + Medium + Fast
      ˚ <tg-emoji emoji-id="5893494861612455015">💎</tg-emoji> Unlimited credits
      ˚ <tg-emoji emoji-id="5902016123972358349">⚙️</tg-emoji> Priority support

   ꒰ <tg-emoji emoji-id="5893376775781617954">👑</tg-emoji> ꒱ <b>Elite — $30/month</b>
      ˚ <tg-emoji emoji-id="5893255507380014983">📦</tg-emoji> 5,000 cards/session
      ˚ <tg-emoji emoji-id="5893048571560726748">🎯</tg-emoji> All speeds + Turbo
      ˚ <tg-emoji emoji-id="5893494861612455015">💎</tg-emoji> Unlimited credits
      ˚ <tg-emoji emoji-id="5902016123972358349">🛡</tg-emoji> Priority support

⊹ <tg-emoji emoji-id="5893401729541608160">💘</tg-emoji> <b>@ZenoRealWebs To Buy</b> <tg-emoji emoji-id="5893333516871012690">🛫</tg-emoji> ⊹"""
        
        if user_data.get('last_msg_id'):
            bot.edit_message_text(msg, chat_id, user_data['last_msg_id'], parse_mode='HTML')
        else:
            m = bot.send_message(chat_id, msg, parse_mode='HTML')
            users[user_id]['last_msg_id'] = m.message_id
            save_users(users)
    
    elif data == 'balance':
        plan = user_data['plan']
        credits = user_data['credits']
        checks = user_data['total_checks']
        hits = user_data['total_hits']
        hit_rate = round((hits / checks) * 100, 2) if checks > 0 else 0
        
        msg = f"""<tg-emoji emoji-id="5893321843149902412">✨</tg-emoji> ⊹ <b>Sus — Balance</b> <tg-emoji emoji-id="5893321843149902412">✨</tg-emoji> ⊹

   ꒰ <tg-emoji emoji-id="5895514131896733546">🆓</tg-emoji> ꒱ <b>Plan</b> · {plan}

      ˚ <tg-emoji emoji-id="5893473283696759404">💵</tg-emoji> <b>Credits</b> — {credits}
      ˚ <tg-emoji emoji-id="5893048571560726748">🎯</tg-emoji> <b>Checks</b> — {checks}
      ˚ <tg-emoji emoji-id="5893185207355315979">🔥</tg-emoji> <b>Hits</b> — {hits}
      ˚ <tg-emoji emoji-id="5895444149699612825">📈</tg-emoji> <b>Hit Rate</b> — {hit_rate}%

⊹ <tg-emoji emoji-id="5893401729541608160">💘</tg-emoji> <i>keep grinding</i> <tg-emoji emoji-id="5893494861612455015">💎</tg-emoji> ⊹"""
        
        if user_data.get('last_msg_id'):
            bot.edit_message_text(msg, chat_id, user_data['last_msg_id'], parse_mode='HTML')
        else:
            m = bot.send_message(chat_id, msg, parse_mode='HTML')
            users[user_id]['last_msg_id'] = m.message_id
            save_users(users)
    
    bot.answer_callback_query(call.id)

# ========== MESSAGE HANDLERS ==========
@bot.message_handler(commands=['start'])
def start_cmd(message):
    chat_id = message.chat.id
    user_id = str(message.from_user.id)
    first_name = message.from_user.first_name
    
    users = load_users()
    if user_id not in users:
        users[user_id] = {
            'plan': 'FREE', 'credits': 100, 'total_checks': 0,
            'total_hits': 0, 'joined': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        save_users(users)
    
    users[user_id]['last_msg_id'] = None
    save_users(users)
    
    welcome = f"""<tg-emoji emoji-id="5386626765781221291">🌟</tg-emoji> <b>SUSPECIOUS</b> <tg-emoji emoji-id="5386626765781221291">🌟</tg-emoji>

<tg-emoji emoji-id="5384146031325758830">✨</tg-emoji> <b>Hey {first_name}! Welcome Back It's Suspecious Checker</b> <tg-emoji emoji-id="5384273819487717218">❤️</tg-emoji>

   ꒰ <tg-emoji emoji-id="5902432207519093015">🛒</tg-emoji> ꒱  <b>/sh</b> — Shopify Single
   ꒰ <tg-emoji emoji-id="6039641775377748623">🛍</tg-emoji> ꒱  <b>/msh</b> — Shopify Mass
   ꒰ <tg-emoji emoji-id="5902056028513505203">💳</tg-emoji> ꒱  <b>/bin</b> <code>X</code> — BiN iNFO
   ꒰ <tg-emoji emoji-id="6041705726206808304">🚀</tg-emoji> ꒱  <b>/vbv</b> <code>X</code> — VBV iNFO

   ꒰ <tg-emoji emoji-id="5902449142575141204">🔑</tg-emoji> ꒱  <b>/redeem</b> <code>X</code> — Premium
   ꒰ <tg-emoji emoji-id="5902242339899838759">🌎</tg-emoji> ꒱  <b>/proxy</b> — Proxies
   ꒰ <tg-emoji emoji-id="5893376775781617954">👑</tg-emoji> ꒱  <b>/plans</b> — Pricing
   ꒰ <tg-emoji emoji-id="5893473283696759404">💵</tg-emoji> ꒱  <b>/balance</b> — Plan & Hits
   ꒰ <tg-emoji emoji-id="5893402730268987918">🍀</tg-emoji> ꒱  <b>/daily</b> — Free Credits

   ˚ ⊹ <tg-emoji emoji-id="5893401729541608160">💘</tg-emoji> <b>@ZenoRealWebs</b> <tg-emoji emoji-id="5893333516871012690">🛫</tg-emoji> ⊹ ˚"""
    
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton("PLANS", callback_data="plans"),
        InlineKeyboardButton("BALANCE", callback_data="balance")
    )
    keyboard.add(InlineKeyboardButton("SUPPORT", url="https://t.me/ZenoRealWebs?text=Hey%20Zeno%20Bro%20What%27s%20Up"))
    
    bot.send_message(chat_id, welcome, parse_mode='HTML', reply_markup=keyboard)

@bot.message_handler(commands=['plans'])
def plans_cmd(message):
    chat_id = message.chat.id
    msg = """<tg-emoji emoji-id="5893321843149902412">✨</tg-emoji> ⊹ <b>Suspecious — Plans</b> <tg-emoji emoji-id="5893376775781617954">👑</tg-emoji> ⊹

   ꒰ <tg-emoji emoji-id="5893402730268987918">🍀</tg-emoji> ꒱ <b>Free</b>
      ˚ <tg-emoji emoji-id="5893255507380014983">📦</tg-emoji> 50 cards/session
      ˚ <tg-emoji emoji-id="5893102202817352158">⏳</tg-emoji> Slow speed
      ˚ <tg-emoji emoji-id="5893473283696759404">💰</tg-emoji> 100 credits

   ꒰ <tg-emoji emoji-id="5384546515551275588">⚡</tg-emoji> ꒱ <b>Basic — $5/week</b>
      ˚ <tg-emoji emoji-id="5893255507380014983">📦</tg-emoji> 500 cards/session
      ˚ <tg-emoji emoji-id="5902432207519093015">⚙️</tg-emoji> Slow + Medium speed
      ˚ <tg-emoji emoji-id="5893473283696759404">💵</tg-emoji> 5,000 credits

   ꒰ <tg-emoji emoji-id="5893185207355315979">🔥</tg-emoji> ꒱ <b>Pro — $15/month</b>
      ˚ <tg-emoji emoji-id="5893255507380014983">📦</tg-emoji> 2,000 cards/session
      ˚ <tg-emoji emoji-id="6041705726206808304">🚀</tg-emoji> Slow + Medium + Fast
      ˚ <tg-emoji emoji-id="5893494861612455015">💎</tg-emoji> Unlimited credits
      ˚ <tg-emoji emoji-id="5902016123972358349">⚙️</tg-emoji> Priority support

   ꒰ <tg-emoji emoji-id="5893376775781617954">👑</tg-emoji> ꒱ <b>Elite — $30/month</b>
      ˚ <tg-emoji emoji-id="5893255507380014983">📦</tg-emoji> 5,000 cards/session
      ˚ <tg-emoji emoji-id="5893048571560726748">🎯</tg-emoji> All speeds + Turbo
      ˚ <tg-emoji emoji-id="5893494861612455015">💎</tg-emoji> Unlimited credits
      ˚ <tg-emoji emoji-id="5902016123972358349">🛡</tg-emoji> Priority support

⊹ <tg-emoji emoji-id="5893401729541608160">💘</tg-emoji> <b>@ZenoRealWebs To Buy</b> <tg-emoji emoji-id="5893333516871012690">🛫</tg-emoji> ⊹"""
    bot.send_message(chat_id, msg, parse_mode='HTML')

@bot.message_handler(commands=['balance'])
def balance_cmd(message):
    chat_id = message.chat.id
    user_id = str(message.from_user.id)
    users = load_users()
    
    if user_id not in users:
        users[user_id] = {'plan': 'FREE', 'credits': 100, 'total_checks': 0, 'total_hits': 0, 'joined': datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        save_users(users)
    
    u = users[user_id]
    hit_rate = round((u['total_hits'] / u['total_checks']) * 100, 2) if u['total_checks'] > 0 else 0
    
    msg = f"""<tg-emoji emoji-id="5893321843149902412">✨</tg-emoji> ⊹ <b>Sus — Balance</b> <tg-emoji emoji-id="5893321843149902412">✨</tg-emoji> ⊹

   ꒰ <tg-emoji emoji-id="5895514131896733546">🆓</tg-emoji> ꒱ <b>Plan</b> · {u['plan']}

      ˚ <tg-emoji emoji-id="5893473283696759404">💵</tg-emoji> <b>Credits</b> — {u['credits']}
      ˚ <tg-emoji emoji-id="5893048571560726748">🎯</tg-emoji> <b>Checks</b> — {u['total_checks']}
      ˚ <tg-emoji emoji-id="5893185207355315979">🔥</tg-emoji> <b>Hits</b> — {u['total_hits']}
      ˚ <tg-emoji emoji-id="5895444149699612825">📈</tg-emoji> <b>Hit Rate</b> — {hit_rate}%

⊹ <tg-emoji emoji-id="5893401729541608160">💘</tg-emoji> <i>keep grinding</i> <tg-emoji emoji-id="5893494861612455015">💎</tg-emoji> ⊹"""
    bot.send_message(chat_id, msg, parse_mode='HTML')

@bot.message_handler(commands=['daily'])
def daily_cmd(message):
    chat_id = message.chat.id
    user_id = str(message.from_user.id)
    users = load_users()
    
    if user_id not in users:
        users[user_id] = {'plan': 'FREE', 'credits': 100, 'total_checks': 0, 'total_hits': 0, 'joined': datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        save_users(users)
    
    last = users[user_id].get('last_daily', '')
    today = datetime.now().strftime('%Y-%m-%d')
    
    if last == today:
        msg = "❌ <b>You already claimed today's free credits!</b>\n\nCome back tomorrow!"
    else:
        users[user_id]['credits'] += 50
        users[user_id]['last_daily'] = today
        save_users(users)
        msg = f"<tg-emoji emoji-id=\"5893402730268987918\">🍀</tg-emoji> <b>Daily Credits Claimed!</b> <tg-emoji emoji-id=\"5893402730268987918\">🍀</tg-emoji>\n\n✅ <b>+50 Credits Added!</b>\n💰 <b>Total Credits:</b> {users[user_id]['credits']}"
    
    bot.send_message(chat_id, msg, parse_mode='HTML')

@bot.message_handler(commands=['vbv'])
def vbv_cmd(message):
    chat_id = message.chat.id
    text = message.text.strip()
    bin_data = re.sub(r'/vbv\s*', '', text).strip()
    
    if not bin_data or not re.match(r'^\d{6,8}$', bin_data):
        msg = "❌ <b>Please enter valid BIN</b>\n\nExample: <code>/vbv 411111</code>"
        bot.send_message(chat_id, msg, parse_mode='HTML')
        return
    
    loading = bot.send_message(chat_id, "🔄 <b>Fetching VBV info...</b>", parse_mode='HTML')
    
    first_digit = bin_data[0]
    digit_sum = sum(int(d) for d in bin_data)
    is_vbv = (first_digit in ['4', '5']) and (digit_sum % 2 == 0)
    
    msg = f"""<tg-emoji emoji-id="6041705726206808304">🚀</tg-emoji> <b>VBV INFO</b> <tg-emoji emoji-id="6041705726206808304">🚀</tg-emoji>

<b>BIN:</b> <code>{bin_data}</code>
"""
    if is_vbv:
        msg += "<b>3DS Status:</b> ✅ <b>VBV Enabled</b>\n"
        msg += "<b>Risk Level:</b> 🔴 High (3DS Required)"
    else:
        msg += "<b>3DS Status:</b> ❌ <b>Non-VBV</b>\n"
        msg += "<b>Risk Level:</b> 🟢 Low (No 3DS)"
    
    bot.edit_message_text(msg, chat_id, loading.message_id, parse_mode='HTML')

@bot.message_handler(commands=['proxy'])
def proxy_menu(message):
    chat_id = message.chat.id
    proxies = load_proxies()
    total = len(proxies)
    
    msg = f"""<tg-emoji emoji-id="5902242339899838759">🌎</tg-emoji> <b>PROXY MENU</b> <tg-emoji emoji-id="5893321843149902412">✨</tg-emoji>

      ꒰ <tg-emoji emoji-id="5895440460322706085">📋</tg-emoji> ꒱  <b>/proxy list</b> · show all proxies
      ꒰ <tg-emoji emoji-id="5895514131896733546">✅</tg-emoji> ꒱  <b>/proxy add</b> · add new proxies
      ꒰ <tg-emoji emoji-id="5893081007153746175">❌</tg-emoji> ꒱  <b>/proxy remove</b> · remove proxy
      ꒰ <tg-emoji emoji-id="5904692292324692386">⚠️</tg-emoji> ꒱  <b>/proxy clear</b> · remove all
      ꒰ <tg-emoji emoji-id="5895444149699612825">📊</tg-emoji> ꒱  <b>/proxy count</b> · count
      ꒰ <tg-emoji emoji-id="5893382531037794941">🔍</tg-emoji> ꒱  <b>/proxy test</b> · test all

      <tg-emoji emoji-id="5902449142575141204">🔌</tg-emoji> <b>total proxies:</b> {total}"""
    bot.send_message(chat_id, msg, parse_mode='HTML')

@bot.message_handler(commands=['proxy list'])
def proxy_list(message):
    chat_id = message.chat.id
    proxies = load_proxies()
    
    if not proxies:
        msg = "<tg-emoji emoji-id=\"5893494861612455015\">⭐️</tg-emoji> <b>NO PROXIES TO LIST</b> <tg-emoji emoji-id=\"5893494861612455015\">⭐️</tg-emoji>"
    else:
        msg = "<tg-emoji emoji-id=\"5895440460322706085\">📋</tg-emoji> <b>PROXY LIST</b> <tg-emoji emoji-id=\"5895440460322706085\">📋</tg-emoji>\n\n"
        for i, p in enumerate(proxies, 1):
            status = '✅ LIVE' if p['status'] == 'live' else '❌ DEAD'
            msg += f"{i}. <code>{p['proxy']}</code> - {status}\n"
    bot.send_message(chat_id, msg, parse_mode='HTML')

@bot.message_handler(commands=['proxy count'])
def proxy_count(message):
    chat_id = message.chat.id
    proxies = load_proxies()
    live = sum(1 for p in proxies if p['status'] == 'live')
    dead = sum(1 for p in proxies if p['status'] != 'live')
    
    msg = f"<tg-emoji emoji-id=\"5895444149699612825\">📊</tg-emoji> <b>PROXY COUNT</b> <tg-emoji emoji-id=\"5895444149699612825\">📊</tg-emoji>\n\n✅ <b>Live:</b> {live}\n❌ <b>Dead:</b> {dead}\n📦 <b>Total:</b> {len(proxies)}"
    bot.send_message(chat_id, msg, parse_mode='HTML')

@bot.message_handler(commands=['proxy clear'])
def proxy_clear(message):
    chat_id = message.chat.id
    proxies = load_proxies()
    
    if not proxies:
        msg = "<tg-emoji emoji-id=\"5893163582194978381\">❌</tg-emoji> <b>NO PROXIES TO CLEAR</b> <tg-emoji emoji-id=\"5893163582194978381\">❌</tg-emoji>"
    else:
        count = len(proxies)
        save_proxies([])
        msg = f"<tg-emoji emoji-id=\"5904692292324692386\">🗑️</tg-emoji> <b>CLEARED {count} PROXIES</b> <tg-emoji emoji-id=\"5904692292324692386\">🗑️</tg-emoji>"
    bot.send_message(chat_id, msg, parse_mode='HTML')

@bot.message_handler(func=lambda m: m.text and m.text.startswith('/proxy add'))
def proxy_add(message):
    chat_id = message.chat.id
    proxy_data = message.text.replace('/proxy add', '').strip()
    
    if not proxy_data:
        msg = "<tg-emoji emoji-id=\"5893162100431261050\">❄️</tg-emoji> <b>/proxy add ip:port:user:pass</b> <tg-emoji emoji-id=\"5893162100431261050\">❄️</tg-emoji>\n\n<b>Example:</b>\n<code>/proxy add 192.168.1.1:8080:user:pass</code>"
        bot.send_message(chat_id, msg, parse_mode='HTML')
        return
    
    testing = bot.send_message(chat_id, "<tg-emoji emoji-id=\"5386625507355804546\">🔄</tg-emoji> <b>TESTING PROXY</b> <tg-emoji emoji-id=\"5386625507355804546\">🔄</tg-emoji>", parse_mode='HTML')
    
    result = test_proxy(proxy_data)
    proxies = load_proxies()
    
    exists = any(p['proxy'] == proxy_data for p in proxies)
    
    if exists:
        msg = "<tg-emoji emoji-id=\"5384273712113535129\">⚠️</tg-emoji> <b>PROXY ALREADY EXISTS</b> <tg-emoji emoji-id=\"5384273712113535129\">⚠️</tg-emoji>"
    elif result['live']:
        proxies.append({'proxy': proxy_data, 'status': 'live', 'added': datetime.now().strftime('%Y-%m-%d %H:%M:%S')})
        save_proxies(proxies)
        total = len(proxies)
        parts = proxy_data.split(':')
        ip_port = f"{parts[0]}:{parts[1]}"
        msg = f"<tg-emoji emoji-id=\"5895514131896733546\">✅</tg-emoji> <b>Added {total} working proxy</b>\n<tg-emoji emoji-id=\"5893255507380014983\">📦</tg-emoji> <b>Total:</b> {total}\n\n<tg-emoji emoji-id=\"5904238507555033712\">🟠</tg-emoji> <code>{ip_port}</code>"
    else:
        msg = f"<tg-emoji emoji-id=\"5893163582194978381\">❌</tg-emoji> <b>PROXY IS DEAD</b> <tg-emoji emoji-id=\"5893163582194978381\">❌</tg-emoji>\n<tg-emoji emoji-id=\"5775896410780079073\">🕓</tg-emoji> <b>TIME TAKEN :</b> {result['time_ms']}ms"
    
    bot.edit_message_text(msg, chat_id, testing.message_id, parse_mode='HTML')

@bot.message_handler(func=lambda m: m.text and m.text.startswith('/proxy remove'))
def proxy_remove(message):
    chat_id = message.chat.id
    proxy_data = message.text.replace('/proxy remove', '').strip()
    
    if not proxy_data:
        msg = "<tg-emoji emoji-id=\"5893162100431261050\">❄️</tg-emoji> <b>/proxy remove ip:port:user:pass</b> <tg-emoji emoji-id=\"5893162100431261050\">❄️</tg-emoji>"
    else:
        proxies = load_proxies()
        found = False
        for i, p in enumerate(proxies):
            if p['proxy'] == proxy_data or p['proxy'].startswith(proxy_data):
                proxies.pop(i)
                found = True
                break
        if found:
            save_proxies(proxies)
            msg = f"<tg-emoji emoji-id=\"5893081007153746175\">✅</tg-emoji> <b>PROXY REMOVED</b> <tg-emoji emoji-id=\"5893081007153746175\">✅</tg-emoji>\n\n<code>{proxy_data}</code>"
        else:
            msg = "<tg-emoji emoji-id=\"5893163582194978381\">❌</tg-emoji> <b>PROXY NOT FOUND</b> <tg-emoji emoji-id=\"5893163582194978381\">❌</tg-emoji>"
    bot.send_message(chat_id, msg, parse_mode='HTML')

@bot.message_handler(commands=['proxy test'])
def proxy_test(message):
    chat_id = message.chat.id
    proxies = load_proxies()
    
    if not proxies:
        msg = "<tg-emoji emoji-id=\"5893494861612455015\">⭐️</tg-emoji> <b>NO PROXIES TO TEST</b> <tg-emoji emoji-id=\"5893494861612455015\">⭐️</tg-emoji>"
        bot.send_message(chat_id, msg, parse_mode='HTML')
        return
    
    testing = bot.send_message(chat_id, "<tg-emoji emoji-id=\"5386625507355804546\">🔄</tg-emoji> <b>TESTING ALL PROXIES</b> <tg-emoji emoji-id=\"5386625507355804546\">🔄</tg-emoji>", parse_mode='HTML')
    
    updated = []
    live = 0
    dead = 0
    
    for p in proxies:
        result = test_proxy(p['proxy'])
        if result['live']:
            p['status'] = 'live'
            updated.append(p)
            live += 1
        else:
            dead += 1
    
    save_proxies(updated)
    
    msg = f"<tg-emoji emoji-id=\"5893382531037794941\">🔍</tg-emoji> <b>PROXY TEST COMPLETE</b> <tg-emoji emoji-id=\"5893382531037794941\">🔍</tg-emoji>\n\n✅ <b>Live:</b> {live}\n❌ <b>Dead (Removed):</b> {dead}\n📦 <b>Total Active:</b> {len(updated)}"
    bot.edit_message_text(msg, chat_id, testing.message_id, parse_mode='HTML')

@bot.message_handler(func=lambda m: True)
def unknown(message):
    pass

# ========== FLASK WEBHOOK ==========
@app.route(f'/{BOT_TOKEN}', methods=['POST'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        json_str = request.get_data().decode('UTF-8')
        update = telebot.types.Update.de_json(json_str)
        bot.process_new_updates([update])
        return '', 200
    return '', 403

@app.route('/', methods=['GET'])
def index():
    return 'Bot is running!'

if __name__ == '__main__':
    print(f"Bot @{BOT_USERNAME} started!")
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))