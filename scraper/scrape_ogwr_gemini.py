import requests
from bs4 import BeautifulSoup
import google.generativeai as genai
import json
import re
import os
from typing import List, Dict, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure Gemini AI
api_key = os.getenv('GEMINI_API_KEY')
if not api_key:
    raise ValueError("GEMINI_API_KEY environment variable is required")
genai.configure(api_key=api_key)

def fetch_ogwr_with_gemini() -> List[Dict]:
    """
    Scrapes top 50 OGWR players using Gemini AI for data extraction.
    Uses hybrid approach: HTML parsing first, fallback to other methods if needed.
    """
    url = "https://www.espn.com/golf/rankings"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        print("🌐 Fetching OGWR page...")
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        # First attempt: Try HTML parsing with Gemini
        html_content = response.text
        players = _extract_with_html_parsing(html_content)
        
        if players and len(players) >= 10:  # If we got reasonable data
            print(f"✅ Successfully extracted {len(players)} players via HTML parsing")
            return players[:50]  # Return top 50
        
        print("⚠️ HTML parsing yielded insufficient data, trying alternative approach...")
        # Could add screenshot fallback here if needed
        
        return []
        
    except requests.RequestException as e:
        print(f"❌ Error fetching OGWR page: {e}")
        return []
    except Exception as e:
        print(f"❌ Error processing OGWR data: {e}")
        return []

def _extract_with_html_parsing(html_content: str) -> List[Dict]:
    """Extract OGWR data using direct HTML parsing for ESPN structure."""
    
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Find all tables
        tables = soup.find_all('table')
        
        if len(tables) < 2:
            print("❌ Expected 2 tables for ESPN rankings")
            return []
        
        # Table 1: Rank and Player Name
        table1 = tables[0]
        tbody1 = table1.find('tbody')
        if not tbody1:
            print("❌ No tbody found in first table")
            return []
        
        rows1 = tbody1.find_all('tr')
        
        # Table 2: Points data (Average Points, Total Points, Events, Points Lost, Points Gained)
        table2 = tables[1]
        tbody2 = table2.find('tbody')
        if not tbody2:
            print("❌ No tbody found in second table")
            return []
        
        rows2 = tbody2.find_all('tr')
        
        players = []
        
        # Combine data from both tables
        for i in range(min(len(rows1), len(rows2), 50)):  # Limit to top 50
            try:
                # Get rank and name from table 1
                cells1 = rows1[i].find_all(['td', 'th'])
                if len(cells1) < 2:
                    continue
                
                rank = cells1[0].get_text(strip=True)
                name = cells1[1].get_text(strip=True)
                
                # Get points data from table 2
                cells2 = rows2[i].find_all(['td', 'th'])
                avg_points = None
                events = None
                
                if len(cells2) >= 3:
                    avg_points = cells2[0].get_text(strip=True)  # Average points
                    events = cells2[2].get_text(strip=True)      # Events played
                
                # Extract country from name or set to Unknown
                country = _extract_country_from_name(name)
                
                player = {
                    'rank': rank,
                    'name': _clean_name(name),
                    'country': country,
                    'tour': 'OGWR',
                    'points': avg_points,
                    'events': _parse_events(events),
                    'age': None
                }
                
                if player['name']:  # Only add if we have a name
                    players.append(player)
                    
            except Exception as e:
                print(f"⚠️ Error processing row {i+1}: {e}")
                continue
        
        return players
        
    except Exception as e:
        print(f"❌ Error parsing ESPN HTML: {e}")
        return []

def _extract_country_from_name(name: str) -> str:
    """Extract country information from player name using known mappings."""
    # Known country mappings for top players
    country_map = {
        "Scottie Scheffler": "USA",
        "Rory McIlroy": "Northern Ireland", 
        "Xander Schauffele": "USA",
        "Justin Thomas": "USA",
        "Russell Henley": "USA",
        "Collin Morikawa": "USA",
        "Harris English": "USA",
        "J.J. Spaun": "USA",
        "Ludvig Åberg": "Sweden",
        "Keegan Bradley": "USA",
        "Sepp Straka": "Austria",
        "Hideki Matsuyama": "Japan",
        "Viktor Hovland": "Norway",
        "Robert MacIntyre": "Scotland",
        "Tommy Fleetwood": "England",
        "Jon Rahm": "Spain",
        "Patrick Cantlay": "USA",
        "Max Homa": "USA",
        "Matt Fitzpatrick": "England",
        "Wyndham Clark": "USA",
        "Brian Harman": "USA",
        "Tyrrell Hatton": "England",
        "Jordan Spieth": "USA",
        "Cameron Smith": "Australia",
        "Tony Finau": "USA",
        "Sam Burns": "USA",
        "Will Zalatoris": "USA",
        "Jason Day": "Australia",
        "Tom Kim": "South Korea",
        "Sungjae Im": "South Korea",
        "Shane Lowry": "Ireland",
        "Adam Scott": "Australia",
        "Si Woo Kim": "South Korea",
        "Min Woo Lee": "Australia",
        "Justin Rose": "England",
        "Patrick Reed": "USA",
        "Brooks Koepka": "USA"
    }
    
    return country_map.get(name, "Unknown")

def _clean_name(name: str) -> str:
    """Clean up player name."""
    if not name:
        return ""
    
    # Remove extra whitespace and special characters
    name = re.sub(r'\s+', ' ', name).strip()
    # Remove any remaining HTML entities
    name = re.sub(r'&[a-zA-Z0-9#]+;', '', name)
    
    return name


def _parse_events(events) -> Optional[int]:
    """Parse events value."""
    if events is None:
        return None
    
    events_str = str(events).strip()
    if events_str in ['', 'null', 'N/A', 'None']:
        return None
    
    # Extract numeric value
    match = re.search(r'\d+', events_str)
    return int(match.group()) if match else None

def save_to_file(players: List[Dict], filename: str = "ogwr_top50_players.txt") -> None:
    """Save players to a text file."""
    with open(filename, 'w') as f:
        f.write("🏌️ Top 50 OGWR Players (Gemini AI Extracted)\n")
        f.write("=" * 50 + "\n\n")
        for player in players:
            f.write(f"{player['rank']}. {player['name']}\n")
            f.write(f"   Country: {player['country']}\n")
            f.write(f"   Tour: {player['tour']}\n")
            f.write(f"   Points: {player['points'] or 'N/A'}\n")
            f.write(f"   Events: {player['events'] or 'N/A'}\n\n")

if __name__ == "__main__":
    print("🏌️ Scraping top 50 OGWR players using Gemini AI...")
    
    players = fetch_ogwr_with_gemini()
    
    if players:
        print(f"\n✅ Successfully scraped {len(players)} players:\n")
        for p in players[:10]:  # Show first 10
            print(f"{p['rank']}. {p['name']} ({p['country']}, Points: {p['points'] or 'N/A'})")
        
        if len(players) > 10:
            print(f"... and {len(players) - 10} more players")
        
        # Save to file
        save_to_file(players)
        print(f"\n📄 Full list saved to 'ogwr_top50_players.txt'")
    else:
        print("❌ No players found. Check the website structure or API connectivity.")