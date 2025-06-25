import os, json, requests, re
from scrapingbee import ScrapingBeeClient
from dotenv import load_dotenv
from pathlib import Path
from bs4 import BeautifulSoup

load_dotenv(dotenv_path=Path(__file__).parent / ".env")

SCRAPINGBEE_API_KEY = os.getenv("SCRAPINGBEE_API_KEY")
BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")

client = ScrapingBeeClient(api_key=SCRAPINGBEE_API_KEY)

def clean_json(text):
    text = re.sub(r'\\(?![\"/bfnrtu])', '', text)
    return text

def extract_name_from_title(title):
    match = re.search(r"(?:WITB.*?[:\-–]?\s*)?([A-Z][a-z]+(?:\s[A-Z][a-z]+)+)", title)
    if match:
        return match.group(1).strip()
    return title.strip()

def discover_pga_player_urls(limit=12):
    print("🔍 Discovering PGA WITB posts...")
    url = "https://www.golfwrx.com/category/equipment/whats-in-the-bag-equipment/"
    resp = client.get(url, params={"render_js": "true"})
    if resp.status_code != 200:
        print(f"❌ Failed to load archive page: Status {resp.status_code}")
        return []

    soup = BeautifulSoup(resp.content, "html.parser")
    links = []
    for a in soup.select("a[href*='witb']"):
        title = a.get_text(strip=True)
        href = a["href"]
        if "lpga" not in title.lower():
            full_url = href if href.startswith("http") else f"https://www.golfwrx.com{href}"
            name = extract_name_from_title(title)
            links.append((name, full_url))

    return list(dict.fromkeys(links))[:limit]

def player_exists(name):
    try:
        res = requests.get(f"{BASE_URL}/players/")
        if res.status_code == 200:
            return any(p["name"].lower() == name.lower() for p in res.json())
    except:
        pass
    return False

def scrape_player_with_ai(name, country, tour, url):
    # Skip names that don't look like real player names
    if len(name.split()) < 2:
        print(f"⏭️ Skipping non-player name: {name}")
        return

    print(f"🤖 Scraping {name} using AI extraction...")

    ai_query = (
        f"Extract ONLY the clubs used by the player named '{name}' listed on this WITB page. "
        "Return a JSON list of objects with: category, brand, model, loft, and shaft. "
        "Ignore clubs belonging to any other player mentioned."
    )

    response = client.get(url, params={"render_js": "false", "ai_query": ai_query})
    if response.status_code != 200:
        print("❌ Failed to fetch page.")
        return

    try:
        raw = clean_json(response.text)
        data = json.loads(raw)
    except Exception as e:
        print(f"❌ JSON parsing failed for {name}: {e}")
        return

    gear = data if isinstance(data, list) else data.get("clubs", [])
    if not gear:
        print("⚠️ No clubs found for", name)
        return

    if player_exists(name):
        print(f"⏭️ Player {name} already exists, skipping.")
        return

    player_payload = {"name": name, "country": country, "tour": tour}
    res = requests.post(f"{BASE_URL}/players/", json=player_payload)  # Note the slash!
    if res.status_code not in [200, 201]:
        print("❌ Failed to create player:", res.text)
        return

    player_id = res.json()["id"]
    print(f"✅ Player created: {name} → ID: {player_id}")

    for item in gear:
        if isinstance(item.get("loft"), list):
            item["loft"] = ", ".join(item["loft"])
        res = requests.post(f"{BASE_URL}/players/{player_id}/witb_items/", json=item)
        if res.status_code in [200, 201]:
            print(f"✔️ Added: {item['category']} - {item['model']}")
        else:
            print(f"❌ Failed to add {item['category']}: {res.text}")

if __name__ == "__main__":
    players = discover_pga_player_urls(limit=12)[4:]  # Skip first 4
    for name, url in players:
        print(f"➡️ Scraping: {name} from {url}")
        scrape_player_with_ai(name=name, country="USA", tour="PGA", url=url)
