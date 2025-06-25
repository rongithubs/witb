from scrapingbee import ScrapingBeeClient
from bs4 import BeautifulSoup
import requests
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(dotenv_path=Path(__file__).parent / ".env")

SCRAPINGBEE_API_KEY = os.getenv("JXHUW4U9BNJ6YPZO3M2V4LORQOQKQ7QFJVOS4Z2WFOQ88EEF3JA7V1FCVHXO65ZOTZNNB16UGBQ3MM2I")
BASE_URL = "http://localhost:8000"

client = ScrapingBeeClient(api_key="JXHUW4U9BNJ6YPZO3M2V4LORQOQKQ7QFJVOS4Z2WFOQ88EEF3JA7V1FCVHXO65ZOTZNNB16UGBQ3MM2I")

def scrape_rory():
    print("Scraping WITB for Rory McIlroy...")
    print("🔑 API Key:", os.getenv("SCRAPINGBEE_API_KEY"))
    response = client.get("https://www.golfwrx.com/rory-mcilroy-witb/", params={"render_js": "true"})
    print(response.status_code)
    print(response.text[:500])

    response = client.get(
        "https://www.golfwrx.com/rory-mcilroy-witb/",
        params={"render_js": "false"}
    )

    if response.status_code != 200:
        print("Failed to fetch page.")
        return

    soup = BeautifulSoup(response.content, "html.parser")

    # Example fallback data for demo
    player = {
        "name": "Rory McIlroy",
        "country": "Northern Ireland",
        "tour": "PGA"
    }

    # Example gear list (should be parsed dynamically later)
    gear = [
        {"category": "Driver", "brand": "TaylorMade", "model": "Qi10 LS", "loft": "9°", "shaft": "Ventus Black 6X"},
        {"category": "3 Wood", "brand": "TaylorMade", "model": "Qi10", "loft": "15°", "shaft": "Ventus Blue 7X"},
        {"category": "Wedge", "brand": "TaylorMade", "model": "MG4", "loft": "52°", "shaft": "DG TI S400"},
        {"category": "Wedge", "brand": "TaylorMade", "model": "MG4", "loft": "56°", "shaft": "DG TI S400"},
        {"category": "Wedge", "brand": "TaylorMade", "model": "MG4", "loft": "60°", "shaft": "DG TI S400"},
    ]

    # Create player
    res = requests.post(f"{BASE_URL}/players", json=player)
    if res.status_code not in [200, 201]:
        print("Error creating player:", res.text)
        return

    player_id = res.json()["id"]
    print(f"Created player {player['name']} with ID: {player_id}")

    # Post each gear item
    for item in gear:
        res = requests.post(f"{BASE_URL}/players/{player_id}/witb_items", json=item)
        if res.status_code in [200, 201]:
            print(f"✔️ Added: {item['category']} - {item['model']}")
        else:
            print(f"❌ Failed to add {item['category']}: {res.text}")

if __name__ == "__main__":
    scrape_rory()
