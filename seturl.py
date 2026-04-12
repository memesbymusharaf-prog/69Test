import logging
import aiohttp
import asyncio
import re
from typing import List, Tuple

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

API_URL = "http://autosh.nikhilkhokhar.com/shopify"
TEST_CARD = "4910149950579116|03|28|106"
HARDCODED_PROXIES = [
    "http://0A2JelrNEymAcMsT:cHo1x72JjZPwB0lg@geo.g-w.info:10080",
]

def get_user_current_tier(user_id: int) -> str:
    try:
        import database
        ud = database.get_or_create_user(user_id, "")
        return ud[2] if ud and len(ud) > 2 else "Free"
    except:
        return "Free"

def extract_domain(url: str) -> str:
    if url.startswith('http://'):
        url = url.replace('http://', 'https://', 1)
    elif not url.startswith('https://'):
        url = 'https://' + url
    m = re.match(r'(https://[^/]+)', url)
    return m.group(1) if m else url

def extract_urls(text: str) -> List[str]:
    urls = re.findall(r'https?://[^\s]+', text)
    return [extract_domain(u) for u in urls]

async def test_site(site: str, proxy: str) -> Tuple[bool, str, str]:
    try:
        proxy_clean = proxy.replace('http://', '')
        api = f"{API_URL}?site={site}&cc={TEST_CARD}&proxy={proxy_clean}"
        async with aiohttp.ClientSession() as s:
            async with s.get(api, timeout=30) as r:
                if r.status != 200:
                    return False, f"HTTP {r.status}", ""
                data = await r.json()
                resp = data.get("Response", "")
                price = data.get("Price", "")
                if any(e in resp.lower() for e in ['r4 token', 'hcaptcha', 'error', 'dead']):
                    return False, resp, price
                return True, resp, price
    except:
        return False, "Timeout", ""

async def handle_seturl_command(update, context):
    user_id = update.effective_user.id
    text = update.message.text or ""
    urls = extract_urls(text)
    if not urls:
        await update.message.reply_text("Send URLs to test")
        return
    msg = await update.message.reply_text(f"Testing {len(urls)} sites...")
    results = []
    working = []
    proxy = HARDCODED_PROXIES[0]
    for url in urls:
        ok, resp, price = await test_site(url, proxy)
        if ok:
            working.append(url)
            results.append(f"✅ {url} - ${price}")
        else:
            results.append(f"❌ {url} - {resp[:50]}")
    if working:
        import database
        for w in working:
            await asyncio.to_thread(database.add_custom_gate, w.replace('https://', '').replace('.myshopify.com', ''), w, user_id)
    await msg.edit_text("\n".join(results[:20]))

async def handle_delurl_command(update, context):
    if not context.args:
        await update.message.reply_text("Usage: /delurl https://site.myshopify.com")
        return
    url = extract_domain(context.args[0])
    import database
    name = url.replace('https://', '').split('.')[0]
    if await asyncio.to_thread(database.delete_custom_gate, name):
        await update.message.reply_text(f"Deleted: {url}")
    else:
        await update.message.reply_text("Site not found")

async def handle_resites_command(update, context):
    await update.message.reply_text("Use /seturl to add new sites")
