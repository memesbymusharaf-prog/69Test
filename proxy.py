import re
import logging
import aiohttp
import asyncio
import random
from datetime import datetime
from typing import List, Tuple, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TEST_SITE = "https://api.ipify.org?format=json"
last_command_time = {}

def get_user_current_tier(user_id: int) -> str:
    try:
        import database
        ud = database.get_or_create_user(user_id, "")
        return ud[2] if ud and len(ud) > 2 else "Free"
    except:
        return "Free"

def auto_fix_proxy_format(raw: str) -> Optional[str]:
    if not raw:
        return None
    p = raw.strip()
    if p.startswith('hytp://'):
        p = 'http://' + p[7:]
    proto = "http"
    if p.startswith(('http://', 'https://')):
        parts = p.split('://', 1)
        proto = parts[0]
        core = parts[1]
    else:
        core = p
    if '@' in core:
        auth, host = core.rsplit('@', 1)
        if ':' in host:
            return f"{proto}://{auth}@{host}"
        return None
    parts = core.split(':')
    if len(parts) >= 4 and parts[1].isdigit():
        host, port, user, pw = parts[0], parts[1], parts[2], ':'.join(parts[3:])
        return f"{proto}://{user}:{pw}@{host}:{port}"
    if len(parts) == 2 and parts[1].isdigit():
        return f"{proto}://{parts[0]}:{parts[1]}"
    return None

def normalize_proxy_format(proxy: str) -> str:
    fixed = auto_fix_proxy_format(proxy)
    return fixed if fixed else f"http://{proxy}"

async def test_proxy(proxy: str) -> Tuple[bool, str]:
    try:
        np = normalize_proxy_format(proxy)
        timeout = aiohttp.ClientTimeout(total=15)
        async with aiohttp.ClientSession(timeout=timeout) as s:
            async with s.get(TEST_SITE, proxy=np) as r:
                if r.status == 200:
                    data = await r.json()
                    return True, f"Working (IP: {data.get('ip', 'Unknown')})"
                return False, "Failed"
    except Exception as e:
        return False, f"Dead: {str(e)[:50]}"

async def handle_proxy_command(update, context):
    user_id = update.effective_user.id
    first_name = update.effective_user.first_name
    if not context.args and not update.message.reply_to_message:
        await update.message.reply_text("Usage: /proxy ip:port:user:pass")
        return
    proxy_text = ""
    if context.args:
        proxy_text = " ".join(context.args)
    elif update.message.reply_to_message and update.message.reply_to_message.text:
        proxy_text = update.message.reply_to_message.text
    lines = proxy_text.split('\n')
    proxies = []
    for line in lines:
        for word in line.split():
            fixed = auto_fix_proxy_format(word)
            if fixed:
                proxies.append(fixed)
    if not proxies:
        await update.message.reply_text("No valid proxies found")
        return
    curr = await asyncio.to_thread(database.get_user_proxies, user_id)
    if len(curr) >= 10:
        await update.message.reply_text("Proxy limit reached (10)")
        return
    max_add = 10 - len(curr)
    if len(proxies) > max_add:
        proxies = proxies[:max_add]
    msg = await update.message.reply_text(f"Testing {len(proxies)} proxies...")
    results = []
    for p in proxies:
        ok, msg_txt = await test_proxy(p)
        if ok:
            suc, _ = await asyncio.to_thread(database.add_user_proxy, user_id, p)
            if suc:
                results.append(f"✅ {p[:50]}...")
            else:
                results.append(f"⚠️ {p[:50]}... already exists")
        else:
            results.append(f"❌ {p[:50]}... {msg_txt[:30]}")
    await msg.edit_text("\n".join(results[:10]))

async def handle_rproxy_command(update, context):
    user_id = update.effective_user.id
    if context.args:
        try:
            cnt = int(context.args[0])
        except:
            await update.message.reply_text("Usage: /rproxy [count]")
            return
    else:
        cnt = -1
    suc, msg = await asyncio.to_thread(database.remove_user_proxies, user_id, cnt)
    await update.message.reply_text(msg)

async def handle_myproxy_command(update, context):
    user_id = update.effective_user.id
    proxies = await asyncio.to_thread(database.get_user_proxies, user_id)
    if not proxies:
        await update.message.reply_text("No proxies found")
        return
    txt = "Your proxies:\n"
    for i, p in enumerate(proxies[:10], 1):
        parts = p.split('@')
        if len(parts) == 2:
            auth, host = parts
            user = auth.split(':')[0] if ':' in auth else auth
            txt += f"{i}. {user}:****@{host}\n"
        else:
            txt += f"{i}. {p[:50]}...\n"
    await update.message.reply_text(txt)
