import requests
import json
import csv
import sys
from datetime import datetime

# load local sets.json
with open("cardsets.json", "r")  as file:
    cardsets_data = json.load(file)
    
# init or load csv
csv_filename = "cards.csv"
try:
    # check if file already exists and has headers
    with open(csv_filename, "r") as file:
        pass
except FileNotFoundError:
    print("Cards CSV file does not exist. Creating...")
    # create the file with headers if doesn't exist
    with open(csv_filename, "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["ID", "Name", "Race", "Type", "Description", "ATK", "DEF",
            "Level", "Attribute", "Archetype", "URL", "Set Name", "Set Code",
            "Set Rarity", "Set Rarity Code", "Earliest TCG Date"])

# Run program with command line argument -dgaf for "don't give a fuck mode". Skips prompts for specific set  
dgaf_mode = "-dgaf" in sys.argv

def fetch_card(card_id):
    """Fetch card info from YGOProDeck API"""
    url = f"https://db.ygoprodeck.com/api/v7/cardinfo.php?id={card_id}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error fetching card ID {card_id}: {response.status_code}")
        return None
    
def find_earliest_tcg_date(card_sets):
    """Find earliest TCG date from local card sets data"""
    earliest_date = None
    for card_set in card_sets:
        set_name = card_set["set_name"]
        matching_set = next((cs for cs in cardsets_data if cs["set_name"] == set_name), None)
        if matching_set and "tcg_date" in matching_set:
           tcg_date = datetime.strptime(matching_set["tcg_date"], "%Y-%m-%d")
           if earliest_date is None or tcg_date < earliest_date:
                earliest_date = tcg_date
    return earliest_date.strftime("%Y-%m-%d") if earliest_date else "N/A"

def process_card(card_data):
    """Process a single card from json returned by API and append to CSV"""
    card_info = card_data["data"][0]
    name = card_info["name"]
    race = card_info["race"]
    card_type = card_info["type"]
    desc = card_info["desc"]
    atk = card_info.get("atk", "N/A")
    defense = card_info.get("def", "N/A")
    level = card_info.get("level", "N/A")
    attribute = card_info.get("attribute", "N/A")
    archetype = card_info.get("archetype", "N/A")
    url = card_info["ygoprodeck_url"]
    card_sets = card_info.get("card_sets", [])

    if dgaf_mode:
        selected_set = {}
    elif len(card_sets) > 1:
        print("\nMultiple sets found. Select one:")
        for idx, card_set in enumerate(card_sets):
            print(f"{idx+1}: {card_set['set_name']} ({card_set['set_code']}, {card_set['set_rarity_code']})")
        choice = int(input("Enter the number of the set to select: ")) - 1
        selected_set = card_sets[choice]
    elif card_sets:
        selected_set = card_sets[0]
    else:
        print("No sets found for this card")
        selected_set = {}
        
    set_name = selected_set.get("set_name", "N/A")
    set_code = selected_set.get("set_code", "N/A")
    set_rarity = selected_set.get("set_rarity", "N/A")
    set_rarity_code = selected_set.get("set_rarity_code", "N/A")
    
    # Get earliest TCG date
    earliest_date = find_earliest_tcg_date(card_sets)
    
    # Append to CSV
    with open(csv_filename, "a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([
          card_id, name, race, card_type, desc, atk, defense, level, attribute, archetype, url, set_name, set_code, set_rarity, set_rarity_code, earliest_date  
        ])
    print(f"Card '{name}' added to the cards table!")
    
    
# Main loop
while True:
    card_id = input("\nEnter a card ID, or type 'done' to exit: ")
    if card_id.lower() == "done":
        print("Exiting...")
        break
    if not card_id.isdigit():
        print("Invalid input. Please enter a numeric card ID.")
        continue
    card_data = fetch_card(card_id)
    if card_data:
        process_card(card_data)