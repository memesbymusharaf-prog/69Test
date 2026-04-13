import os
import json
import time
import re
import requests
import threading
import asyncio
import aiohttp
from datetime import datetime
from flask import Flask, request
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import BOT_TOKEN, ADMIN_CHAT_ID, BOT_USERNAME

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

# ========== FILES ==========
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

# ========== BIN INFO FUNCTION ==========
async def get_bin_info(bin_number: str) -> dict:
    BINLIST_URL = "https://bins.antipublic.cc/bins/{}"
    
    if not bin_number.isdigit() or len(bin_number) < 6:
        return {"error": "Invalid BIN. Must be at least 6 digits."}
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(BINLIST_URL.format(bin_number)) as resp:
                if resp.status == 429:
                    return {"error": "Rate limit exceeded. Try again later."}
                if resp.status == 404:
                    return {"error": "BIN not found."}
                if resp.status != 200:
                    return {"error": f"API request failed (status {resp.status})"}
                
                data = await resp.json()
                
                return {
                    "bin": data.get("bin"),
                    "scheme": data.get("brand", "N/A"),
                    "type": data.get("type", "N/A"),
                    "brand": data.get("level", "N/A"),
                    "bank": data.get("bank", "N/A"),
                    "country": data.get("country_name", "Unknown"),
                    "country_emoji": data.get("country_flag", ""),
                }
        except Exception as e:
            return {"error": f"Exception: {str(e)}"}

# ========== CALLBACK HANDLER ==========
@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    chat_id = call.message.chat.id
    data = call.data
    callback_id = call.id
    user_id = call.from_user.id
    
    users = load_users()
    
    if str(user_id) not in users:
        users[str(user_id)] = {
            'plan': 'FREE',
            'credits': 100,
            'total_checks': 0,
            'total_hits': 0,
            'joined': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'last_msg_id': None
        }
        save_users(users)
    
    user_data = users[str(user_id)]
    
    if data == 'plans':
        plans_msg = """˚ ⊹ <tg-emoji emoji-id="5893321843149902412">✨</tg-emoji> <b>Suspecious — Plans</b> <tg-emoji emoji-id="5893376775781617954">👑</tg-emoji> ⊹ ˚

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

˚ ⊹ <tg-emoji emoji-id="5893401729541608160">💘</tg-emoji> <b>@ZenoRealWebs To Buy</b> <tg-emoji emoji-id="5893333516871012690">🛫</tg-emoji> ⊹ ˚"""
        
        if user_data.get('last_msg_id'):
            bot.edit_message_text(plans_msg, chat_id, user_data['last_msg_id'], parse_mode='HTML')
        else:
            msg = bot.send_message(chat_id, plans_msg, parse_mode='HTML')
            users[str(user_id)]['last_msg_id'] = msg.message_id
            save_users(users)
    
    elif data == 'balance':
        plan = user_data['plan']
        credits = user_data['credits']
        checks = user_data['total_checks']
        hits = user_data['total_hits']
        hit_rate = round((hits / checks) * 100, 2) if checks > 0 else 0
        
        balance_msg = f"""˚ ⊹ <tg-emoji emoji-id="6039641775377748623">🛍</tg-emoji> <b>Sus — Balance</b> <tg-emoji emoji-id="5893321843149902412">✨</tg-emoji> ⊹ ˚

   ꒰ <tg-emoji emoji-id="5895514131896733546">🆓</tg-emoji> ꒱ <b>Plan</b> · {plan}

      ˚ <tg-emoji emoji-id="5893473283696759404">💵</tg-emoji> <b>Credits</b> — {credits}
      ˚ <tg-emoji emoji-id="5893048571560726748">🎯</tg-emoji> <b>Checks</b> — {checks}
      ˚ <tg-emoji emoji-id="5893185207355315979">🔥</tg-emoji> <b>Hits</b> — {hits}
      ˚ <tg-emoji emoji-id="5895444149699612825">📈</tg-emoji> <b>Hit Rate</b> — {hit_rate}%

˚ ⊹ <tg-emoji emoji-id="5893401729541608160">💘</tg-emoji> <i>keep grinding</i> <tg-emoji emoji-id="5893494861612455015">💎</tg-emoji> ⊹ ˚"""
        
        if user_data.get('last_msg_id'):
            bot.edit_message_text(balance_msg, chat_id, user_data['last_msg_id'], parse_mode='HTML')
        else:
            msg = bot.send_message(chat_id, balance_msg, parse_mode='HTML')
            users[str(user_id)]['last_msg_id'] = msg.message_id
            save_users(users)
    
    bot.answer_callback_query(callback_id)

# ========== MESSAGE HANDLERS ==========

@bot.message_handler(commands=['start'])
def start_cmd(message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    first_name = message.from_user.first_name
    
    users = load_users()
    
    if str(user_id) not in users:
        users[str(user_id)] = {
            'plan': 'FREE',
            'credits': 100,
            'total_checks': 0,
            'total_hits': 0,
            'joined': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        save_users(users)
    
    users[str(user_id)]['last_msg_id'] = None
    save_users(users)
    
    welcome = f"""˚ ⊹ <tg-emoji emoji-id="5893185207355315979">🔥</tg-emoji> 𝗭𝗘𝗡𝗢 𝗢𝗥 𝗪𝗛𝗔𝗧 𝗦𝗶𝗥? !! <tg-emoji emoji-id="5893450623449305489">⚡</tg-emoji> ⊹ ˚

   <tg-emoji emoji-id="5893321843149902412">✨</tg-emoji> 𝗁𝖾𝗒 {first_name} !! · 𝗐𝖾𝗅𝖼𝗈𝗆𝖾 𝖻𝖺𝖼𝗄 <tg-emoji emoji-id="5895213106228891182">❤️</tg-emoji>

   ꒰ <tg-emoji emoji-id="6039641775377748623">🛒</tg-emoji> ꒱ 𝖢𝗁𝖾𝖼𝗄𝖾𝗋𝗌
      ˚ /sh — 𝗌𝗂𝗇𝗀𝗅𝖾  ˚ /msh — 𝗆𝖺𝗌𝗌
      ˚ /ct — 𝖼𝗎𝗌𝗍𝗈𝗆 𝗀𝖺𝗍𝖾

   ꒰ <tg-emoji emoji-id="5893382531037794941">🔍</tg-emoji> ꒱ 𝖫𝗈𝗈𝗄𝗎𝗉𝗌
      ˚ /vbv — 𝟥𝖣𝖲  ˚ /mvbv — 𝗆𝖺𝗌𝗌
      ˚ /bin — 𝖻𝗂𝗇 𝗂𝗇𝖿𝗈

   ꒰ <tg-emoji emoji-id="5902432207519093015">⚙️</tg-emoji> ꒱ 𝖠𝖼𝖼𝗈𝗎𝗇𝗍
      ˚ /redeem — 𝗉𝗋𝖾𝗆𝗂𝗎𝗆
      ˚ /balance — 𝗌𝗍𝖺𝗍𝗌  ˚ /daily — 𝖿𝗋𝖾𝖾
      ˚ /plans — 𝗉𝗋𝗂𝖼𝗂𝗇𝗀  ˚ /proxy — 𝗉𝗋𝗈𝗑𝗂𝖾𝗌

   ˚ ⊹ <tg-emoji emoji-id="5893401729541608160">💘</tg-emoji> - @ZenoRealWebs - <tg-emoji emoji-id="5893333516871012690">🛫</tg-emoji> ⊹ ˚"""
    
    bot.send_message(chat_id, welcome, parse_mode='HTML')

@bot.message_handler(commands=['bin'])
def bin_cmd(message):
    chat_id = message.chat.id
    text = message.text.strip()
    bin_data = re.sub(r'/bin\s*', '', text).strip()
    
    if not bin_data or not re.match(r'^\d{6,8}$', bin_data):
        msg = "❌ <b>Please enter valid BIN</b>\n\nExample: <code>/bin 411111</code>"
        bot.send_message(chat_id, msg, parse_mode='HTML')
        return
    
    loading = bot.send_message(chat_id, "<tg-emoji emoji-id=\"5386625507355804546\">🔄</tg-emoji> <b>Fetching BIN info...</b>", parse_mode='HTML')
    
    try:
        url = f"https://bins.antipublic.cc/bins/{bin_data}"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            bin_num = data.get('bin', bin_data)
            scheme = data.get('brand', 'N/A')
            card_type = data.get('type', 'N/A')
            brand = data.get('level', 'N/A')
            bank = data.get('bank', 'N/A')
            country = data.get('country_name', 'Unknown')
            flag = data.get('country_flag', '')
            
            # Check if prepaid
            is_prepaid = "PREPAID" in str(data).upper()
            prepaid_text = "𝗻𝗼𝘁 𝗽𝗿𝗲𝗽𝗮𝗶𝗱" if not is_prepaid else "𝗽𝗿𝗲𝗽𝗮𝗶𝗱"
            
            msg = f"""˚ ⊹ <tg-emoji emoji-id="5902056028513505203">💳</tg-emoji> <b>𝗕𝗜𝗡 𝗟𝗼𝗼𝗸𝘂𝗽</b> <tg-emoji emoji-id="5893382531037794941">🔍</tg-emoji> ⊹ ˚

   ꒰ <tg-emoji emoji-id="5893494861612455015">💎</tg-emoji> ꒱ <b>𝗰𝗮𝗿𝗱 𝗱𝗲𝘁𝗮𝗶𝗹𝘀</b>
      ˚ <tg-emoji emoji-id="5895440460322706085">🏷</tg-emoji> <b>𝗕𝗜𝗡:</b> <code>{bin_num}</code>
      ˚ <tg-emoji emoji-id="5902016123972358349">🛡</tg-emoji> <b>{scheme}</b>  ˚ <tg-emoji emoji-id="5895440460322706085">🧾</tg-emoji> <b>{card_type}</b>
      ˚ <tg-emoji emoji-id="5893376775781617954">👑</tg-emoji> <b>{brand}</b>  ˚ <tg-emoji emoji-id="5893473283696759404">🪙</tg-emoji> <i>{prepaid_text}</i>

   ꒰ <tg-emoji emoji-id="5893255507380014983">🏦</tg-emoji> ꒱ <b>𝗶𝘀𝘀𝘂𝗲𝗿</b>
      ˚ <tg-emoji emoji-id="5893255507380014983">💼</tg-emoji> <b>{bank}</b>
      ˚ <tg-emoji emoji-id="5902242339899838759">🌎</tg-emoji> <b>{country}</b> {flag}

   ˚ <i>𝘁𝗵𝗲𝗿𝗲 𝘂 𝗴𝗼 𝗽𝗼𝗼𝗸𝗶𝗲~</i> <tg-emoji emoji-id="5893401729541608160">💘</tg-emoji>"""
            
        elif response.status_code == 404:
            msg = f"❌ <b>BIN not found:</b> <code>{bin_data}</code>"
        else:
            msg = f"❌ <b>API Error:</b> Status {response.status_code}"
    except Exception as e:
        msg = f"❌ <b>Error:</b> {str(e)}"
    
    bot.edit_message_text(msg, chat_id, loading.message_id, parse_mode='HTML')

@bot.message_handler(commands=['plans'])
def plans_cmd(message):
    chat_id = message.chat.id
    
    plans_msg = """<tg-emoji emoji-id="5893321843149902412">✨</tg-emoji> ⊹ <b>Suspecious — Plans</b> <tg-emoji emoji-id="5893376775781617954">👑</tg-emoji> ⊹

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
    
    bot.send_message(chat_id, plans_msg, parse_mode='HTML')

@bot.message_handler(commands=['balance'])
def balance_cmd(message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    users = load_users()
    
    if str(user_id) not in users:
        users[str(user_id)] = {
            'plan': 'FREE',
            'credits': 100,
            'total_checks': 0,
            'total_hits': 0,
            'joined': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        save_users(users)
    
    user_data = users[str(user_id)]
    hit_rate = round((user_data['total_hits'] / user_data['total_checks']) * 100, 1) if user_data['total_checks'] > 0 else 0
    
    balance_msg = f"""˚ ⊹ <tg-emoji emoji-id="6039641775377748623">🛍</tg-emoji> <b>Sus — Balance</b> <tg-emoji emoji-id="5893321843149902412">✨</tg-emoji> ⊹ ˚

   ꒰ <tg-emoji emoji-id="5895514131896733546">🆓</tg-emoji> ꒱ <b>Plan</b> · {user_data['plan']}

      ˚ <tg-emoji emoji-id="5893473283696759404">💵</tg-emoji> <b>Credits</b> — {user_data['credits']}
      ˚ <tg-emoji emoji-id="5893048571560726748">🎯</tg-emoji> <b>Checks</b> — {user_data['total_checks']}
      ˚ <tg-emoji emoji-id="5893185207355315979">🔥</tg-emoji> <b>Hits</b> — {user_data['total_hits']}
      ˚ <tg-emoji emoji-id="5895444149699612825">📈</tg-emoji> <b>Hit Rate</b> — {hit_rate}%

˚ ⊹ <tg-emoji emoji-id="5893401729541608160">💘</tg-emoji> <i>keep grinding</i> <tg-emoji emoji-id="5893494861612455015">💎</tg-emoji> ⊹ ˚"""
    
    bot.send_message(chat_id, balance_msg, parse_mode='HTML')

@bot.message_handler(commands=['daily'])
def daily_cmd(message):
    chat_id = message.chat.id
    user_id = str(message.from_user.id)
    users = load_users()
    today = datetime.now().strftime('%Y-%m-%d')
    
    if user_id not in users:
        users[user_id] = {
            'plan': 'FREE',
            'credits': 100,
            'total_checks': 0,
            'total_hits': 0,
            'joined': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        save_users(users)
    
    last_claim = users[user_id].get('last_daily', '')
    
    if last_claim == today:
        msg = "❌ <b>You already claimed today's free credits!</b>\n\nCome back tomorrow!"
    else:
        free_credits = 50
        users[user_id]['credits'] = users[user_id].get('credits', 100) + free_credits
        users[user_id]['last_daily'] = today
        save_users(users)
        msg = f"🍀 <b>Daily Credits Claimed!</b> 🍀\n\n✅ <b>+{free_credits} Credits Added!</b>\n💰 <b>Total Credits:</b> {users[user_id]['credits']}"
    
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
    
    loading = bot.send_message(chat_id, "<tg-emoji emoji-id=\"5386625507355804546\">🔄</tg-emoji> <b>Fetching VBV info...</b>", parse_mode='HTML')
    
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
def proxy_cmd(message):
    chat_id = message.chat.id
    proxies = load_proxies()
    total = len(proxies)
    
    proxy_msg = f"""˚ ⊹ <tg-emoji emoji-id="5902242339899838759">🌎</tg-emoji> <b>𝗣𝗿𝗼𝘅𝘆 𝗠𝗲𝗻𝘂</b> <tg-emoji emoji-id="5893321843149902412">✨</tg-emoji> ⊹ ˚

      ꒰ <tg-emoji emoji-id="5895440460322706085">📋</tg-emoji> ꒱ <b>/proxy list</b>  ˚ 𝘴𝘩𝘰𝘸 𝘢𝘭𝘭
      ꒰ <tg-emoji emoji-id="5895514131896733546">✅</tg-emoji> ꒱ <b>/proxy add</b>  ˚ 𝘢𝘥𝘥 𝘯𝘦𝘸
      ꒰ <tg-emoji emoji-id="5893081007153746175">❌</tg-emoji> ꒱ <b>/proxy remove</b>  ˚ 𝘳𝘦𝘮𝘰𝘷𝘦
      ꒰ <tg-emoji emoji-id="5904692292324692386">⚠️</tg-emoji> ꒱ <b>/proxy clear</b>  ˚ 𝘤𝘭𝘦𝘢𝘳 𝘢𝘭𝘭
      ꒰ <tg-emoji emoji-id="5895444149699612825">📊</tg-emoji> ꒱ <b>/proxy count</b>  ˚ 𝘤𝘰𝘶𝘯𝘵
      ꒰ <tg-emoji emoji-id="5893382531037794941">🔍</tg-emoji> ꒱ <b>/proxy test</b>  ˚ 𝘵𝘦𝘴𝘵 𝘢𝘭𝘭

      ˚ <tg-emoji emoji-id="5902449142575141204">🔌</tg-emoji> <b>{total} proxies</b>"""
    
    bot.send_message(chat_id, proxy_msg, parse_mode='HTML')

@bot.message_handler(func=lambda m: True)
def unknown(message):
    pass
#============ PROXY LIST ========

@bot.message_handler(commands=['proxy list'])
def proxy_list(message):
    chat_id = message.chat.id
    proxies = load_proxies()
    total = len(proxies)
    
    if not proxies:
        msg = "<tg-emoji emoji-id=\"5893494861612455015\">⭐️</tg-emoji> <b>NO PROXIES TO LIST</b> <tg-emoji emoji-id=\"5893494861612455015\">⭐️</tg-emoji>"
        bot.send_message(chat_id, msg, parse_mode='HTML')
        return
    
    # Format proxy list
    proxy_text = ""
    for i, p in enumerate(proxies, 1):
        # Extract just IP:port from proxy string
        proxy_display = p['proxy'].split('://')[-1] if '://' in p['proxy'] else p['proxy']
        # Remove user:pass@ if present
        if '@' in proxy_display:
            proxy_display = proxy_display.split('@')[-1]
        proxy_text += f"      ˚ <tg-emoji emoji-id=\"5902449142575141204\">🔌</tg-emoji> {i}. {proxy_display}\n"
    
    msg = f"""˚ ⊹ <tg-emoji emoji-id="5902242339899838759">🌎</tg-emoji> <b>𝗣𝗿𝗼𝘅𝘆 𝗟𝗶𝘀𝘁</b> <tg-emoji emoji-id="5893321843149902412">✨</tg-emoji> ⊹ ˚

      ˚ <tg-emoji emoji-id="5893255507380014983">📦</tg-emoji> <b>{total} proxies</b>

{proxy_text}"""
    
    bot.send_message(chat_id, msg, parse_mode='HTML')

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
    bot.remove_webhook()
    bot.infinity_polling()
