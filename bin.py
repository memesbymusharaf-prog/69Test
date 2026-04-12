import aiohttp

async def get_bin_info(bin_number: str) -> dict:
    if not bin_number.isdigit() or len(bin_number) < 6:
        return {"error": "Invalid BIN"}
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://lookup.binlist.net/{bin_number}") as resp:
                if resp.status != 200:
                    return {}
                data = await resp.json()
                return {
                    "scheme": data.get("scheme", "N/A"),
                    "bank": data.get("bank", {}).get("name", "N/A"),
                    "country": data.get("country", {}).get("name", "Unknown"),
                    "country_flag": data.get("country", {}).get("emoji", ""),
                    "type": data.get("type", "N/A"),
                    "brand": data.get("brand", "N/A")
                }
    except:
        return {}
