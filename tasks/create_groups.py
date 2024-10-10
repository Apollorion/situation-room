import requests
import json
import os

# Function to create pushover group
def create_group(name):
    url = f"https://api.pushover.net/1/groups.json?token={os.environ['PUSHOVER_API_TOKEN']}"
    data = {
        "name": name
    }
    response = requests.post(url, data=data)
    response = response.json()

    if response["status"] == 1:
        return response["group"]

    print(response)
    raise Exception(f"Failed to create group {name}.")

# List of all 32 NHL teams

teams = [
    "Anaheim Ducks",
    "Boston Bruins",
    "Buffalo Sabres",
    "Calgary Flames",
    "Carolina Hurricanes",
    "Chicago Blackhawks",
    "Colorado Avalanche",
    "Columbus Blue Jackets",
    "Dallas Stars",
    "Detroit Red Wings",
    "Edmonton Oilers",
    "Florida Panthers",
    "Los Angeles Kings",
    "Minnesota Wild",
    "Montreal Canadiens",
    "Nashville Predators",
    "New Jersey Devils",
    "New York Islanders",
    "New York Rangers",
    "Ottawa Senators",
    "Philadelphia Flyers",
    "Pittsburgh Penguins",
    "San Jose Sharks",
    "Seattle Kraken",
    "St. Louis Blues",
    "Tampa Bay Lightning",
    "Toronto Maple Leafs",
    "Utah Hockey Club",
    "Vancouver Canucks",
    "Vegas Golden Knights",
    "Washington Capitals",
    "Winnipeg Jets"
]

group_ids = {}

for team in teams:
    print(f"Creating group {team}...")
    group_ids[team] = create_group(team)

# write to file
with open("groups.json", "w") as f:
    f.write(json.dumps(group_ids, indent=4))