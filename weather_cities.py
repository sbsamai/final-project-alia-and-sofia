import sqlite3
import requests
import json
import time

weatherstack_api = "6f7fdfc359e17e9883971f1985286df3"
weather_url = "https://api.weatherstack.com/current"


cities = [
    "New York", "Los Angeles", "Chicago", "Boston", "Seattle", "Ann Arbor", 
    "Philadelphia", "Detroit", "Pittsburgh", "Houston", "Dallas", "Austin", 
    "San Francisco", "Sacramento", "Oakland", "San Diego", "Las Vegas", "Salt Lake City",
    "Jacksonville", "Miami", "Burlington", "Spokane", "San Antonio", "Charlottesville", 
    "Durham", "Hartford", "Denver", "Omaha", "Phoenix", "Columbus", "Cincinnati", 
    "Nashville", "Charlotte", "Indianapolis", "Portland", "Baltimore", "Milwaukee", 
    "Atlanta", "Minneapolis", "Tulsa", "Kansas City", "Fresno", "Tucson", "Louisville",
    "Albuquerque", "Memphis", "Chattanooga", "Fort Worth", "Boulder", "Oklahoma City"
]

city_states = {
     "New York": "NY", "Los Angeles": "CA", "Chicago": "IL", "Boston": "MA", "Seattle": "WA", "Ann Arbor": "MI", 
    "Philadelphia": "PA", "Detroit": "MI", "Pittsburgh": "PA", "Houston": "TX", "Dallas": "TX", "Austin": "TX", 
    "San Francisco": "CA", "Sacramento": "CA", "Oakland": "CA", "San Diego": "CA", "Las Vegas": "NV", "Salt Lake City": "UT",
    "Jacksonville": "FL", "Miami": "FL", "Burlington": "VT", "Spokane": "WA", "San Antonio": "TX", "Charlottesville": "VA", 
    "Durham": "NC", "Hartford": "CT", "Denver": "CO", "Omaha": "NE", "Phoenix": "AZ", "Columbus": "OH", "Cincinnati": "OH", 
    "Nashville": "TN", "Charlotte": "NC", "Indianapolis": "IN", "Portland": "OR", "Baltimore": "MD", "Milwaukee": "WI", 
    "Atlanta": "GA", "Minneapolis": "MN", "Tulsa": "OK", "Kansas City": "MO", "Fresno": "CA", "Tucson": "AZ", "Louisville": "KY",
    "Albuquerque": "NM", "Memphis": "TN", "Chattanooga": "TN", "Fort Worth": "TX", "Boulder": "CO", "Oklahoma City": "OK"
}


def read_weather_data(city, json_file):
    params = {
        "access_key": weatherstack_api,
        "query": city,
        "units": "f"
    }
    response = requests.get(weather_url, params=params)
    response_json = response.json()
    try:
        try:
            with open(json_file, 'r') as f:
                prev_data = json.load(f)
                prev_data.append(response_json)
        except (FileNotFoundError, json.JSONDecodeError):
            prev_data = []
        prev_data.append(response_json)
        with open(json_file, 'w') as f:
            json.dump(prev_data, f, indent=2)
            print(f'Saved to {json_file}')
    except:
        return 'Error saving json'
    
    
def load_weather_cities_json(cities):
    for city in cities:
        read_weather_data(city, 'city_weather_data.json')
        print(f'Successfully saved {city}')
        time.sleep(2)


if __name__ == "__main__":
    load_weather_cities_json(cities)


