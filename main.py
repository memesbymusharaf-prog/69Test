import os
import asyncio
import json
import logging
import telebot
from config import BOT_TOKEN, ADMIN_CHAT_ID, BOT_USERNAME

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot = telebot.TeleBot(BOT_TOKEN)
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

# Import modules
import database
import plans
import sh
import msh
import proxy

database.create_connection_pool()
database.setup_database()

@bot.message_handler(commands=['start'])
def start_cmd(m):
    database.get_or_create_user(m.from_user.id, m.from_user.username or m.from_user.first_name)
    
    welcome = f"""<tg-emoji emoji-id="5386626765781221291">🌟</tg-emoji> <b>SUSPECIOUS</b> <tg-emoji emoji-id="5386626765781221291">🌟</tg-emoji>

<tg-emoji emoji-id="5384146031325758830">✨</tg-emoji> <b>Hey {m.from_user.first_name}! Welcome Back</b> <tg-emoji emoji-id="5384273819487717218">❤️</tg-emoji>

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
    
    keyboard = {
        "inline_keyboard": [
            [{"text": "PLANS", "callback_data": "plans", "icon_custom_emoji_id": "5902056028513505203", "style": "primary"},
             {"text": "BALANCE", "callback_data": "balance", "icon_custom_emoji_id": "5895444149699612825", "style": "primary"}],
            [{"text": "SUPPORT", "url": "https://t.me/ZenoRealWebs", "icon_custom_emoji_id": "5384181297302224842", "style": "primary"}]
        ]
    }
    bot.send_message(m.chat.id, welcome, parse_mode='HTML', reply_markup=json.dumps(keyboard))

@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    if call.data == 'plans':
        bot.edit_message_text(plans.get_plans_display(), call.message.chat.id, call.message.message_id, parse_mode='HTML')
    elif call.data == 'balance':
        credits = database.get_user_credits(call.from_user.id)
        if credits == float('inf'):
            credits_display = "♾️ Unlimited"
        else:
            credits_display = str(credits)
        msg = f"""<tg-emoji emoji-id="5893321843149902412">✨</tg-emoji> ⊹ <b>BALANCE</b> <tg-emoji emoji-id="5893321843149902412">✨</tg-emoji> ⊹

   <tg-emoji emoji-id="5893473283696759404">💵</tg-emoji> <b>Credits:</b> {credits_display}

⊹ <tg-emoji emoji-id="5893401729541608160">💘</tg-emoji> <i>keep grinding</i> <tg-emoji emoji-id="5893494861612455015">💎</tg-emoji> ⊹"""
        bot.edit_message_text(msg, call.message.chat.id, call.message.message_id, parse_mode='HTML')
    bot.answer_callback_query(call.id)

@bot.message_handler(commands=['plans'])
def plans_cmd(m):
    bot.send_message(m.chat.id, plans.get_plans_display(), parse_mode='HTML')

@bot.message_handler(commands=['balance'])
def balance_cmd(m):
    credits = database.get_user_credits(m.from_user.id)
    if credits == float('inf'):
        credits_display = "♾️ Unlimited"
    else:
        credits_display = str(credits if credits else 100)
    msg = f"""<tg-emoji emoji-id="5893321843149902412">✨</tg-emoji> ⊹ <b>BALANCE</b> <tg-emoji emoji-id="5893321843149902412">✨</tg-emoji> ⊹

   <tg-emoji emoji-id="5893473283696759404">💵</tg-emoji> <b>Credits:</b> {credits_display}

⊹ <tg-emoji emoji-id="5893401729541608160">💘</tg-emoji> <i>keep grinding</i> <tg-emoji emoji-id="5893494861612455015">💎</tg-emoji> ⊹"""
    bot.send_message(m.chat.id, msg, parse_mode='HTML')

@bot.message_handler(commands=['daily'])
def daily_cmd(m):
    users = database.load_users()
    today = datetime.now().strftime('%Y-%m-%d')
    uid = str(m.from_user.id)
    if uid not in users:
        users[uid] = {'credits': 100, 'last_daily': None}
    if users[uid].get('last_daily') == today:
        bot.reply_to(m, "❌ Already claimed today!")
        return
    users[uid]['credits'] = users[uid].get('credits', 100) + 50
    users[uid]['last_daily'] = today
    database.save_users(users)
    bot.reply_to(m, f"🍀 +50 Credits! Total: {users[uid]['credits']}")

@bot.message_handler(commands=['vbv'])
def vbv_cmd(m):
    import re
    bin_data = re.sub(r'/vbv\s*', '', m.text.strip()).strip()
    if not bin_data or not re.match(r'^\d{6,8}$', bin_data):
        bot.reply_to(m, "Usage: /vbv 411111")
        return
    first = bin_data[0]
    is_vbv = (first in ['4', '5']) and (sum(int(d) for d in bin_data) % 2 == 0)
    msg = f"🚀 VBV INFO\nBIN: {bin_data}\n3DS: {'✅ Enabled' if is_vbv else '❌ Disabled'}"
    bot.reply_to(m, msg)

@bot.message_handler(commands=['sh'])
def sh_cmd(m):
    class MockUpdate:
        effective_user = m.from_user
        message = m
        class Message:
            chat = m.chat
            text = m.text
            reply_to_message = m.reply_to_message
        message = Message()
    class MockContext:
        args = m.text.split()[1:] if len(m.text.split()) > 1 else []
    async def run():
        await sh.handle_sh_command(MockUpdate(), MockContext())
    asyncio.run_coroutine_threadsafe(run(), loop)
    bot.reply_to(m, "Processing...")

@bot.message_handler(commands=['msh'])
def msh_cmd(m):
    class MockUpdate:
        effective_user = m.from_user
        message = m
        class Message:
            chat = m.chat
            text = m.text
            document = m.document
            reply_to_message = m.reply_to_message
        message = Message()
    class MockContext:
        args = m.text.split()[1:] if len(m.text.split()) > 1 else []
    async def run():
        await msh.handle_msh_command(MockUpdate(), MockContext())
    asyncio.run_coroutine_threadsafe(run(), loop)
    bot.reply_to(m, "Processing file...")

@bot.message_handler(commands=['proxy'])
def proxy_cmd(m):
    class MockUpdate:
        effective_user = m.from_user
        message = m
        class Message:
            chat = m.chat
            text = m.text
            reply_to_message = m.reply_to_message
        message = Message()
    class MockContext:
        args = m.text.split()[1:] if len(m.text.split()) > 1 else []
    async def run():
        await proxy.handle_proxy_command(MockUpdate(), MockContext())
    asyncio.run_coroutine_threadsafe(run(), loop)
    bot.reply_to(m, "Processing proxies...")

@bot.message_handler(commands=['rproxy'])
def rproxy_cmd(m):
    class MockUpdate:
        effective_user = m.from_user
        message = m
        class Message:
            chat = m.chat
            text = m.text
        message = Message()
    class MockContext:
        args = m.text.split()[1:] if len(m.text.split()) > 1 else []
    async def run():
        await proxy.handle_rproxy_command(MockUpdate(), MockContext())
    asyncio.run_coroutine_threadsafe(run(), loop)
    bot.reply_to(m, "Removing proxies...")

@bot.message_handler(commands=['myproxy'])
def myproxy_cmd(m):
    class MockUpdate:
        effective_user = m.from_user
        message = m
        class Message:
            chat = m.chat
            text = m.text
        message = Message()
    class MockContext:
        args = []
    async def run():
        await proxy.handle_myproxy_command(MockUpdate(), MockContext())
    asyncio.run_coroutine_threadsafe(run(), loop)
    bot.reply_to(m, "Fetching proxies...")

@bot.message_handler(func=lambda m: True)
def unknown(m):
    pass

if __name__ == '__main__':
    from datetime import datetime
    print(f"Bot @{BOT_USERNAME} started!")
    bot.remove_webhook()
    bot.infinity_polling()
