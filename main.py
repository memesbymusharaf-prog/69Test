import os
import asyncio
import logging
import json
from datetime import datetime
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import BOT_TOKEN, ADMIN_CHAT_ID, BOT_USERNAME

# ========== LOGGING ==========
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ========== BOT INIT ==========
bot = telebot.TeleBot(BOT_TOKEN)

# Create event loop for async functions
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

# ========== IMPORT MODULES ==========
import database
import bin
import proxy
import seturl
import sh
import msh

# Initialize database
database.create_connection_pool()
database.setup_database()
database.setup_custom_gates_table()

# ========== START COMMAND ==========
@bot.message_handler(commands=['start'])
def start_cmd(message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    first_name = message.from_user.first_name
    
    # Get or create user
    database.get_or_create_user(user_id, message.from_user.username or first_name)
    
    welcome = f"""<tg-emoji emoji-id="5386626765781221291">🌟</tg-emoji> <b>SUSPECIOUS</b> <tg-emoji emoji-id="5386626765781221291">🌟</tg-emoji>

<tg-emoji emoji-id="5384146031325758830">✨</tg-emoji> <b>Hey {first_name}! Welcome Back</b> <tg-emoji emoji-id="5384273819487717218">❤️</tg-emoji>

   ꒰ <tg-emoji emoji-id="5902432207519093015">🛒</tg-emoji> ꒱  <b>/sh</b> — Shopify Single
   ꒰ <tg-emoji emoji-id="6039641775377748623">🛍</tg-emoji> ꒱  <b>/msh</b> — Shopify Mass
   ꒰ <tg-emoji emoji-id="5902056028513505203">💳</tg-emoji> ꒱  <b>/bin</b> — BIN Info
   ꒰ <tg-emoji emoji-id="6041705726206808304">🚀</tg-emoji> ꒱  <b>/vbv</b> — VBV Info

   ꒰ <tg-emoji emoji-id="5902449142575141204">🔑</tg-emoji> ꒱  <b>/redeem</b> — Premium
   ꒰ <tg-emoji emoji-id="5902242339899838759">🌎</tg-emoji> ꒱  <b>/proxy</b> — Proxies
   ꒰ <tg-emoji emoji-id="5893376775781617954">👑</tg-emoji> ꒱  <b>/plans</b> — Pricing
   ꒰ <tg-emoji emoji-id="5893473283696759404">💵</tg-emoji> ꒱  <b>/balance</b> — Credits
   ꒰ <tg-emoji emoji-id="5893402730268987918">🍀</tg-emoji> ꒱  <b>/daily</b> — Free Credits

   ˚ ⊹ <tg-emoji emoji-id="5893401729541608160">💘</tg-emoji> <b>@ZenoRealWebs</b> <tg-emoji emoji-id="5893333516871012690">🛫</tg-emoji> ⊹ ˚"""
    
    # BUTTONS WITH PRIMARY COLOR (Bot API 9.4)
    keyboard = {
        "inline_keyboard": [
            [
                {"text": "PLANS", "callback_data": "plans", "icon_custom_emoji_id": "5902056028513505203", "style": "primary"},
                {"text": "BALANCE", "callback_data": "balance", "icon_custom_emoji_id": "5895444149699612825", "style": "primary"}
            ],
            [
                {"text": "SUPPORT", "url": "https://t.me/ZenoRealWebs", "icon_custom_emoji_id": "5384181297302224842", "style": "primary"}
            ]
        ]
    }
    
    bot.send_message(chat_id, welcome, parse_mode='HTML', reply_markup=json.dumps(keyboard))

# ========== CALLBACK HANDLER ==========
@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    chat_id = call.message.chat.id
    data = call.data
    user_id = call.from_user.id
    
    if data == 'plans':
        msg = """<tg-emoji emoji-id="5893321843149902412">✨</tg-emoji> ⊹ <b>PLANS</b> <tg-emoji emoji-id="5893376775781617954">👑</tg-emoji> ⊹

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
        bot.edit_message_text(msg, chat_id, call.message.message_id, parse_mode='HTML')
    
    elif data == 'balance':
        credits = database.get_user_credits(user_id)
        if credits == float('inf'):
            credits_display = "♾️ Unlimited"
        else:
            credits_display = str(credits)
        
        msg = f"""<tg-emoji emoji-id="5893321843149902412">✨</tg-emoji> ⊹ <b>BALANCE</b> <tg-emoji emoji-id="5893321843149902412">✨</tg-emoji> ⊹

   <tg-emoji emoji-id="5893473283696759404">💵</tg-emoji> <b>Credits:</b> {credits_display}

⊹ <tg-emoji emoji-id="5893401729541608160">💘</tg-emoji> <i>keep grinding</i> <tg-emoji emoji-id="5893494861612455015">💎</tg-emoji> ⊹"""
        bot.edit_message_text(msg, chat_id, call.message.message_id, parse_mode='HTML')
    
    bot.answer_callback_query(call.id)

# ========== SHOPIFY SINGLE CHECK ==========
@bot.message_handler(commands=['sh'])
def sh_command(message):
    """Handle /sh command"""
    class MockUpdate:
        def __init__(self, msg):
            self.effective_user = msg.from_user
            self.message = msg
            self.effective_chat = msg.chat
        
        class Message:
            def __init__(self, m):
                self.from_user = m.from_user
                self.chat = m.chat
                self.text = m.text
                self.reply_to_message = m.reply_to_message
            
            async def reply_text(self, text, parse_mode=None, disable_web_page_preview=None):
                return bot.reply_to(m, text, parse_mode=parse_mode)
        
        self.message = Message(msg)
    
    class MockContext:
        args = message.text.split()[1:] if len(message.text.split()) > 1 else []
    
    update = MockUpdate(message)
    
    async def run():
        await sh.handle_sh_command(update, MockContext())
    
    asyncio.run_coroutine_threadsafe(run(), loop)

# ========== SHOPIFY MASS CHECK ==========
@bot.message_handler(commands=['msh'])
def msh_command(message):
    """Handle /msh command"""
    class MockUpdate:
        def __init__(self, msg):
            self.effective_user = msg.from_user
            self.message = msg
            self.effective_chat = msg.chat
            
            class MockMessage:
                def __init__(self, m):
                    self.from_user = m.from_user
                    self.chat = m.chat
                    self.text = m.text
                    self.document = m.document
                    self.reply_to_message = m.reply_to_message
                
                async def reply_text(self, text, parse_mode=None, reply_markup=None, disable_web_page_preview=None):
                    return bot.reply_to(m, text, parse_mode=parse_mode, reply_markup=reply_markup)
            
            self.message = MockMessage(msg)
    
    class MockContext:
        args = message.text.split()[1:] if len(message.text.split()) > 1 else []
    
    update = MockUpdate(message)
    
    async def run():
        await msh.handle_msh_command(update, MockContext())
    
    asyncio.run_coroutine_threadsafe(run(), loop)

# ========== STOP COMMAND ==========
@bot.message_handler(commands=['stop'])
def stop_command(message):
    """Handle /stop command"""
    class MockUpdate:
        def __init__(self, msg):
            self.effective_user = msg.from_user
            self.message = msg
            self.effective_chat = msg.chat
        
        class Message:
            def __init__(self, m):
                self.from_user = m.from_user
                self.chat = m.chat
                self.text = m.text
            
            async def reply_text(self, text, parse_mode=None, disable_web_page_preview=None):
                return bot.reply_to(m, text, parse_mode=parse_mode)
        
        self.message = Message(msg)
    
    class MockContext:
        args = message.text.split()[1:] if len(message.text.split()) > 1 else []
    
    update = MockUpdate(message)
    
    async def run():
        await msh.handle_stop_command(update, MockContext())
    
    asyncio.run_coroutine_threadsafe(run(), loop)

# ========== PROXY COMMANDS ==========
@bot.message_handler(commands=['proxy'])
def proxy_cmd(message):
    """Handle /proxy command"""
    class MockUpdate:
        def __init__(self, msg):
            self.effective_user = msg.from_user
            self.message = msg
            self.effective_chat = msg.chat
        
        class Message:
            def __init__(self, m):
                self.from_user = m.from_user
                self.chat = m.chat
                self.text = m.text
                self.document = m.document
                self.reply_to_message = m.reply_to_message
            
            async def reply_text(self, text, parse_mode=None, reply_markup=None, disable_web_page_preview=None):
                return bot.reply_to(m, text, parse_mode=parse_mode, reply_markup=reply_markup)
        
        self.message = Message(msg)
    
    class MockContext:
        args = message.text.split()[1:] if len(message.text.split()) > 1 else []
    
    update = MockUpdate(message)
    
    async def run():
        await proxy.handle_proxy_command(update, MockContext())
    
    asyncio.run_coroutine_threadsafe(run(), loop)

@bot.message_handler(commands=['rproxy'])
def rproxy_cmd(message):
    """Handle /rproxy command"""
    class MockUpdate:
        def __init__(self, msg):
            self.effective_user = msg.from_user
            self.message = msg
            self.effective_chat = msg.chat
        
        class Message:
            def __init__(self, m):
                self.from_user = m.from_user
                self.chat = m.chat
                self.text = m.text
            
            async def reply_text(self, text, parse_mode=None, disable_web_page_preview=None):
                return bot.reply_to(m, text, parse_mode=parse_mode)
        
        self.message = Message(msg)
    
    class MockContext:
        args = message.text.split()[1:] if len(message.text.split()) > 1 else []
    
    update = MockUpdate(message)
    
    async def run():
        await proxy.handle_rproxy_command(update, MockContext())
    
    asyncio.run_coroutine_threadsafe(run(), loop)

@bot.message_handler(commands=['myproxy'])
def myproxy_cmd(message):
    """Handle /myproxy command"""
    class MockUpdate:
        def __init__(self, msg):
            self.effective_user = msg.from_user
            self.message = msg
            self.effective_chat = msg.chat
        
        class Message:
            def __init__(self, m):
                self.from_user = m.from_user
                self.chat = m.chat
                self.text = m.text
            
            async def reply_text(self, text, parse_mode=None, disable_web_page_preview=None):
                return bot.reply_to(m, text, parse_mode=parse_mode)
        
        self.message = Message(msg)
    
    class MockContext:
        args = message.text.split()[1:] if len(message.text.split()) > 1 else []
    
    update = MockUpdate(message)
    
    async def run():
        await proxy.handle_myproxy_command(update, MockContext())
    
    asyncio.run_coroutine_threadsafe(run(), loop)

# ========== SETURL COMMANDS ==========
@bot.message_handler(commands=['seturl'])
def seturl_cmd(message):
    """Handle /seturl command"""
    class MockUpdate:
        def __init__(self, msg):
            self.effective_user = msg.from_user
            self.message = msg
            self.effective_chat = msg.chat
        
        class Message:
            def __init__(self, m):
                self.from_user = m.from_user
                self.chat = m.chat
                self.text = m.text
                self.document = m.document
                self.reply_to_message = m.reply_to_message
            
            async def reply_text(self, text, parse_mode=None, reply_markup=None, disable_web_page_preview=None):
                return bot.reply_to(m, text, parse_mode=parse_mode, reply_markup=reply_markup)
        
        self.message = Message(msg)
    
    class MockContext:
        args = message.text.split()[1:] if len(message.text.split()) > 1 else []
    
    update = MockUpdate(message)
    
    async def run():
        await seturl.handle_seturl_command(update, MockContext())
    
    asyncio.run_coroutine_threadsafe(run(), loop)

@bot.message_handler(commands=['delurl'])
def delurl_cmd(message):
    """Handle /delurl command"""
    class MockUpdate:
        def __init__(self, msg):
            self.effective_user = msg.from_user
            self.message = msg
            self.effective_chat = msg.chat
        
        class Message:
            def __init__(self, m):
                self.from_user = m.from_user
                self.chat = m.chat
                self.text = m.text
            
            async def reply_text(self, text, parse_mode=None, disable_web_page_preview=None):
                return bot.reply_to(m, text, parse_mode=parse_mode)
        
        self.message = Message(msg)
    
    class MockContext:
        args = message.text.split()[1:] if len(message.text.split()) > 1 else []
    
    update = MockUpdate(message)
    
    async def run():
        await seturl.handle_delurl_command(update, MockContext())
    
    asyncio.run_coroutine_threadsafe(run(), loop)

@bot.message_handler(commands=['resites'])
def resites_cmd(message):
    """Handle /resites command"""
    class MockUpdate:
        def __init__(self, msg):
            self.effective_user = msg.from_user
            self.message = msg
            self.effective_chat = msg.chat
        
        class Message:
            def __init__(self, m):
                self.from_user = m.from_user
                self.chat = m.chat
                self.text = m.text
            
            async def reply_text(self, text, parse_mode=None, disable_web_page_preview=None):
                return bot.reply_to(m, text, parse_mode=parse_mode)
        
        self.message = Message(msg)
    
    class MockContext:
        args = message.text.split()[1:] if len(message.text.split()) > 1 else []
    
    update = MockUpdate(message)
    
    async def run():
        await seturl.handle_resites_command(update, MockContext())
    
    asyncio.run_coroutine_threadsafe(run(), loop)

# ========== DAILY COMMAND ==========
@bot.message_handler(commands=['daily'])
def daily_cmd(message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    
    users = database.load_users() if hasattr(database, 'load_users') else {}
    
    if str(user_id) not in users:
        users[str(user_id)] = {'credits': 100, 'last_daily': None}
    
    last = users[str(user_id)].get('last_daily', '')
    today = datetime.now().strftime('%Y-%m-%d')
    
    if last == today:
        msg = "❌ <b>You already claimed today's free credits!</b>\n\nCome back tomorrow!"
    else:
        users[str(user_id)]['credits'] = users[str(user_id)].get('credits', 100) + 50
        users[str(user_id)]['last_daily'] = today
        if hasattr(database, 'save_users'):
            database.save_users(users)
        msg = f"<tg-emoji emoji-id=\"5893402730268987918\">🍀</tg-emoji> <b>Daily Credits Claimed!</b> <tg-emoji emoji-id=\"5893402730268987918\">🍀</tg-emoji>\n\n✅ <b>+50 Credits Added!</b>\n💰 <b>Total Credits:</b> {users[str(user_id)]['credits']}"
    
    bot.send_message(chat_id, msg, parse_mode='HTML')

# ========== BALANCE COMMAND ==========
@bot.message_handler(commands=['balance'])
def balance_cmd(message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    
    credits = database.get_user_credits(user_id)
    if credits == float('inf'):
        credits_display = "♾️ Unlimited"
    else:
        credits_display = str(credits if credits else 100)
    
    msg = f"""<tg-emoji emoji-id="5893321843149902412">✨</tg-emoji> ⊹ <b>BALANCE</b> <tg-emoji emoji-id="5893321843149902412">✨</tg-emoji> ⊹

   <tg-emoji emoji-id="5893473283696759404">💵</tg-emoji> <b>Credits:</b> {credits_display}

⊹ <tg-emoji emoji-id="5893401729541608160">💘</tg-emoji> <i>keep grinding</i> <tg-emoji emoji-id="5893494861612455015">💎</tg-emoji> ⊹"""
    bot.send_message(chat_id, msg, parse_mode='HTML')

# ========== PLANS COMMAND ==========
@bot.message_handler(commands=['plans'])
def plans_cmd(message):
    chat_id = message.chat.id
    
    msg = """<tg-emoji emoji-id="5893321843149902412">✨</tg-emoji> ⊹ <b>PLANS</b> <tg-emoji emoji-id="5893376775781617954">👑</tg-emoji> ⊹

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

# ========== VBV COMMAND ==========
@bot.message_handler(commands=['vbv'])
def vbv_cmd(message):
    chat_id = message.chat.id
    text = message.text.strip()
    import re
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

# ========== MAIN ==========
if __name__ == '__main__':
    print(f"Bot @{BOT_USERNAME} started!")
    bot.remove_webhook()
    bot.infinity_polling()
