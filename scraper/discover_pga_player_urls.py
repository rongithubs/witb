
# import requests
# from bs4 import BeautifulSoup
# import re

# def discover_pga_player_urls(limit=5):
#     print("🔍 Discovering PGA WITB posts...")

#     archive_url = "https://www.golfwrx.com/tag/whats-in-the-bag/"
#     headers = {
#         "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
#     }

#     response = requests.get(archive_url, headers=headers)
#     if response.status_code != 200:
#         print(f"❌ Failed to load archive page: Status {response.status_code}")
#         return []

#     soup = BeautifulSoup(response.text, "html.parser")
#     links = soup.select("a.topic_title")
#     player_urls = []

#     for link in links:
#         href = link.get("href")
#         title = link.get_text(strip=True)

#         if not href or "witb" not in href.lower():
#             continue

#         # Use regex to extract the player's name
#         match = re.search(r"(.*?)(?= WITB|’s WITB|WITB:)", title, re.IGNORECASE)
#         clean_name = match.group(1).strip() if match else title.strip()

#         player_urls.append((clean_name, href))

#         if len(player_urls) >= limit:
#             break

#     return player_urls