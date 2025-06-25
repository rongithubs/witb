from scrapingbee import ScrapingBeeClient
from bs4 import BeautifulSoup
import requests, os, json, re
from dotenv import load_dotenv
from pathlib import Path

load_dotenv(dotenv_path=Path(__file__).parent/'.env')
client = ScrapingBeeClient(api_key=os.getenv("SCRAPINGBEE_API_KEY"))
BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")
BASE_DISCOVERY = "https://www.golfwrx.com/category/equipment/whats-in-the-bag-equipment/"
LOG_FILE = "failed_scrapes.log"

def discover_pga_player_urls():
    print("🔍 Discovering PGA WITB posts...")
    found = []
    for page in range(1, 4):
        url = BASE_DISCOVERY if page == 1 else f"{BASE_DISCOVERY}page/{page}/"
        resp = client.get(url, params={"render_js": "true"})
        if resp.status_code != 200:
            print(f"⚠️ Page {page}: status {resp.status_code}")
            continue
        soup = BeautifulSoup(resp.content, "html.parser")
        for a in soup.select("a[href*='/']"):
            title = a.get_text(strip=True)
            href = a["href"]
            if "witb" in title.lower() and "lpga" not in title.lower():
                full = href if href.startswith("http") else f"https://www.golfwrx.com{href}"
                found.append((title, full))
    return list(dict.fromkeys(found))

def clean_json(text):
    text = re.sub(r"\\(?![\"/bfnrtu])", "", text)

    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        print("❌ JSON parsing failed:", e)
        with open(LOG_FILE, "a") as f:
            f.write("JSON Decode Error:\n" + text + "\n\n")
        return []

def player_exists(name):
    try:
        res = requests.get(f"{BASE_URL}/players")
        if res.status_code == 200:
            return any(p["name"].lower() == name.lower() for p in res.json())
    except Exception:
        return False
    return False

def scrape_player(name, country, tour, url):
    print(f"🤖 Scraping {name} using AI extraction...")
    if player_exists(name):
        print("…already exists, skipping")
        return
    ai_query = (
        "Extract a JSON array called 'clubs' of golf club objects (category, brand, model, loft, shaft) "
        f"from this pro golfer’s WITB: {name}. Ignore duplicates or past clubs."
    )
    resp = client.get(url, params={"render_js":"false","ai_query":ai_query})
    raw = resp.content.decode("utf-8")
    gear_data = clean_json(raw)
    if not gear_data:
        print(f"⚠️ Skipping {name}, parsing failed.")
        return
    player = {"name": name, "country": country, "tour": tour}
    res = requests.post(f"{BASE_URL}/players", json=player)
    if res.status_code not in [200, 201]:
        print("❌ Player creation failed:", res.text)
        return
    player_id = res.json()["id"]
    print(f"✅ Player created: {name} → ID: {player_id}")
    for item in gear_data:
        if not isinstance(item, dict):
            continue
        item["loft"] = str(item.get("loft")) if item.get("loft") is not None else None
        res = requests.post(f"{BASE_URL}/players/{player_id}/witb_items", json=item)
        if res.status_code in [200, 201]:
            print(f"✔️ Added: {item.get('category')} - {item.get('model')}")
        else:
            print(f"❌ Failed to add {item.get('category')}: {res.text}")

if __name__ == "__main__":
    players = discover_pga_player_urls()
    for name, url in players[:4]:
        scrape_player(name=name, country="USA", tour="PGA", url=url)
