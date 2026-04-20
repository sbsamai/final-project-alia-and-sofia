import sqlite3
import requests
import json
import time

crime_data_api = "xczSIpzphElLZGUKa6qPmDkCTpys2VWQpQbDYpSp"
crime_url = "https://api.usa.gov/crime/fbi/cde"

cities = [
    "New York"
    # "New York", "Los Angeles", "Chicago", "Boston", "Seattle", "Ann Arbor", 
    # "Philadelphia", "Detroit", "Pittsburgh", "Houston", "Dallas", "Austin", 
    # "San Francisco", "Sacramento", "Oakland", "San Diego", "Las Vegas", "Salt Lake City",
    # "Jacksonville", "Miami", "Burlington", "Spokane", "San Antonio", "Charlottesville", 
    # "Durham", "Hartford", "Denver", "Omaha", "Phoenix", "Columbus", "Cincinnati", 
    # "Nashville", "Charlotte", "Indianapolis", "Portland", "Baltimore", "Milwaukee", 
    # "Atlanta", "Minneapolis", "Tulsa", "Kansas City", "Fresno", "Tucson", "Louisville",
    # "Albuquerque", "Memphis", "Chattanooga", "Fort Worth", "Boulder", "Oklahoma City"
]

city_states = {
    "New York": "New York", "Los Angeles": "California", "Chicago": "Illinois", "Boston": "Massachusetts", "Seattle": "Washington", "Ann Arbor": "Michigan",
    "Philadelphia": "Pennsylvania", "Detroit": "Michigan", "Pittsburgh": "Pennsylvania", "Houston": "Texas", "Dallas": "Texas", "Austin": "Texas",
    "San Francisco": "California", "Sacramento": "California", "Oakland": "California", "San Diego": "California", "Las Vegas": "Nevada", "Salt Lake City": "Utah",
    "Jacksonville": "Florida", "Miami": "Florida", "Burlington": "Vermont", "Spokane": "Washington", "San Antonio": "Texas", "Charlottesville": "Virginia",
    "Durham": "North Carolina", "Hartford": "Connecticut", "Denver": "Colorado", "Omaha": "Nebraska", "Phoenix": "Arizona", "Columbus": "Ohio", "Cincinnati": "Ohio",
    "Nashville": "Tennessee", "Charlotte": "North Carolina", "Indianapolis": "Indiana", "Portland": "Oregon", "Baltimore": "Maryland", "Milwaukee": "Wisconsin",
    "Atlanta": "Georgia", "Minneapolis": "Minnesota", "Tulsa": "Oklahoma", "Kansas City": "Missouri", "Fresno": "California", "Tucson": "Arizona", "Louisville": "Kentucky",
    "Albuquerque": "New Mexico", "Memphis": "Tennessee", "Chattanooga": "Tennessee", "Fort Worth": "Texas", "Boulder": "Colorado", "Oklahoma City": "Oklahoma"
}

def read_crime_data(city, json_file):
    state = city_states.get(city)
    if not state:
        print(f"No state found for {city}")
        return
    params = {
        "api_key": crime_data_api,
        'state': state
    }
    response = requests.get(f'{crime_url}/shr/state/{state}', params=params)
    print(f"Status code: {response.status_code}")
    print(f"URL called: {response.url}")
    print(f"Response text: {response.text[:500]}")
    response_json = response.json()
    city_agencies = [
        agency for agency in response_json.get("results", [])
        if city.lower() in agency.get("city_name", "").lower()
    ]
    try:
        try:
            with open(json_file, 'r') as f:
                prev_data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            prev_data = []

        prev_data.append({"city": city, "state": state, "agencies": city_agencies})

        with open(json_file, 'w') as f:
            json.dump(prev_data, f, indent=2)
            print(f"Saved {city} to {json_file} ({len(city_agencies)} agencies found)")
    except:
        return 'Error saving json'
    
    
def load_crime_cities_json(cities):
    for city in cities:
        read_crime_data(city, 'city_crime_data.json')
        print(f'Successfully saved {city}')
        time.sleep(2)


if __name__ == "__main__":
    load_crime_cities_json(cities)


