import requests
from bs4 import BeautifulSoup
import re

def fetch_top50_espn():
    """
    Scrapes top 50 PGA Tour players from ESPN Golf Stats
    """
    url = "https://www.espn.com/golf/stats/player"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find the stats table
        table = soup.find('table', class_='Table')
        if not table:
            # Fallback: look for any table with player data
            table = soup.find('table')
        
        if not table:
            print("❌ Could not find stats table")
            return []
        
        # Find table rows with player data
        rows = table.find('tbody').find_all('tr') if table.find('tbody') else table.find_all('tr')[1:]  # Skip header
        
        top50 = []
        
        for i, row in enumerate(rows[:50]):  # Limit to top 50
            cells = row.find_all(['td', 'th'])
            
            if len(cells) < 3:  # Need at least rank, name, and one stat
                continue
            
            try:
                # Extract rank
                rank_cell = cells[0]
                rank = rank_cell.get_text(strip=True)
                
                # Extract player name and country from name cell
                name_cell = cells[1]
                
                # Look for country flag image
                flag_img = name_cell.find('img')
                country = "Unknown"
                if flag_img and flag_img.get('alt'):
                    country = flag_img.get('alt').strip()
                
                # Extract player name
                name_link = name_cell.find('a')
                if name_link:
                    name = name_link.get_text(strip=True)
                else:
                    name = name_cell.get_text(strip=True)
                
                # Extract age if available
                age_text = cells[2].get_text(strip=True) if len(cells) > 2 else "N/A"
                try:
                    age = int(age_text) if age_text != "N/A" and age_text.isdigit() else None
                except (ValueError, TypeError):
                    age = None
                
                # Extract additional stats if available (earnings, events, etc.)
                earnings = cells[3].get_text(strip=True) if len(cells) > 3 else "N/A"
                events = cells[4].get_text(strip=True) if len(cells) > 4 else "N/A"
                
                # Clean up name (remove extra whitespace/characters)
                name = re.sub(r'\s+', ' ', name).strip()
                
                # Set tour (since this is ESPN PGA Tour stats)
                tour = "PGA Tour"
                
                if name and rank:
                    top50.append({
                        "rank": rank,
                        "name": name,
                        "country": country,
                        "tour": tour,
                        "age": age,
                        "earnings": earnings,
                        "events": events
                    })
                    
            except Exception as e:
                print(f"⚠️ Error processing row {i+1}: {e}")
                continue
        
        return top50
        
    except requests.RequestException as e:
        print(f"❌ Error fetching data: {e}")
        return []
    except Exception as e:
        print(f"❌ Error parsing data: {e}")
        return []

def save_to_file(players, filename="top50_espn_players.txt"):
    """Save players to a text file"""
    with open(filename, 'w') as f:
        f.write("🏌️ Top 50 PGA Tour Players from ESPN\n")
        f.write("=" * 50 + "\n\n")
        for player in players:
            f.write(f"{player['rank']}. {player['name']}\n")
            f.write(f"   Country: {player['country']}\n")
            f.write(f"   Tour: {player['tour']}\n")
            f.write(f"   Age: {player['age']}\n")
            f.write(f"   Earnings: {player['earnings']}\n")
            f.write(f"   Events: {player['events']}\n\n")

if __name__ == "__main__":
    print("🏌️ Scraping top 50 PGA Tour players from ESPN...")
    players = fetch_top50_espn()
    
    if players:
        print(f"\n✅ Successfully scraped {len(players)} players:\n")
        for p in players[:10]:  # Show first 10
            print(f"{p['rank']}. {p['name']} ({p['country']}, Age: {p['age']})")
        
        if len(players) > 10:
            print(f"... and {len(players) - 10} more players")
        
        # Save to file
        save_to_file(players)
        print(f"\n📄 Full list saved to 'top50_espn_players.txt'")
    else:
        print("❌ No players found. The website structure may have changed.")