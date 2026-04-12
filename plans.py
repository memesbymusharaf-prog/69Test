from database import get_user_plan, update_user_plan, get_or_create_user
from datetime import datetime

PLANS_DISPLAY_MSG = """<tg-emoji emoji-id="5893321843149902412">✨</tg-emoji> ⊹ <b>PLANS</b> <tg-emoji emoji-id="5893376775781617954">👑</tg-emoji> ⊹

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

def get_plans_display() -> str:
    return PLANS_DISPLAY_MSG

def get_user_current_tier(user_id: int) -> str:
    if user_id == 7167704900:
        return "owner"
    
    user_plan = get_user_plan(user_id)
    if user_plan:
        tier, expiry_date = user_plan
        if expiry_date:
            expiry = datetime.strptime(expiry_date, '%Y-%m-%d %H:%M:%S')
            if datetime.now() > expiry:
                return "Free"
        return tier
    
    return "Free"
