import os
import json
import requests
import re
from scrapingbee import ScrapingBeeClient
from dotenv import load_dotenv
from pathlib import Path

load_dotenv(dotenv_path=Path(__file__).parent / ".env")

SCRAPINGBEE_API_KEY = os.getenv("SCRAPINGBEE_API_KEY")
BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")

client = ScrapingBeeClient(api_key=SCRAPINGBEE_API_KEY)

def clean_json(text):
    # Removes any backslash that isn't part of a valid escape sequence
    cleaned = re.sub(r'\\\\(?!["\\\\/bfnrtu])', '', text)
    cleaned = re.sub(r'\\(?!["\\\\/bfnrtu])', '', cleaned)
    return cleaned

def scrape_player_with_ai(name, country, tour, url):
    print(f"🤖 Scraping {name} using AI extraction...")

    ai_query = (
        "Extract ONLY the clubs used by the player named '"
        + name +
        "' listed on this WITB page. "
        "Return a JSON list of objects with: category, brand, model, loft, and shaft. "
        "Ignore clubs belonging to any other player mentioned."
    )

    # Fetch page content + AI parsing
    response = client.get(
        url,
        params={"render_js": "false", "ai_query": ai_query}
    )

    if response.status_code != 200:
        print("❌ Failed to fetch page with AI.")
        return

    try:
        raw = clean_json(response.text)
        data = json.loads(raw)
    except Exception as e:
        print("❌ JSON parsing failed:", e)
        print(response.text)
        return

    gear = data if isinstance(data, list) else data.get("clubs", [])
    if not gear:
        print("⚠️ No clubs extracted.")
        return

    # Post player
    player_payload = {
        "name": name,
        "country": country,
        "tour": tour
    }

    res = requests.post(f"{BASE_URL}/players", json=player_payload)
    if res.status_code not in [200, 201]:
        print("❌ Failed to create player:", res.text)
        return

    player_id = res.json()["id"]
    print(f"✅ Player created: {name} → ID: {player_id}")

    for item in gear:
        # Fix loft if it's a list
        if isinstance(item.get("loft"), list):
            item["loft"] = ", ".join(item["loft"])

        res = requests.post(f"{BASE_URL}/players/{player_id}/witb_items", json=item)
        if res.status_code in [200, 201]:
            print(f"✔️ Added: {item['category']} - {item['model']}")
        else:
            print(f"❌ Failed to add {item['category']}: {res.text}")

if __name__ == "__main__":
    players = [
        {
            "name": "Rory McIlroy",
            "country": "Northern Ireland",
            "tour": "PGA",
            "url": "https://www.golfwrx.com/757540/rory-mcilroy-witb-2025-april/"
        }
    ]

    for p in players:
        scrape_player_with_ai(p["name"], p["country"], p["tour"], p["url"])