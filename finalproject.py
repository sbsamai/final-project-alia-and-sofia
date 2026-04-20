import sqlite3
import requests
import json
from datetime import datetime
import time

# weatherstack_api = "6f7fdfc359e17e9883971f1985286df3"
# weather_url = "https://api.weatherstack.com/current"

crime_data_api = "VOGY9tV90tYpHSJheAtRnvhy2FwcOdw13dxmJ6cT"
crime_url = "https://api.usa.gov/crime/fbi/sapi/api/estimates/states"

# cities = [
#     "New York", "Los Angeles", "Chicago", "Boston", "Seattle", "Ann Arbor", 
#     "Philadelphia", "Detroit", "Pittsburgh", "Houston", "Dallas", "Austin", 
#     "San Francisco", "Sacramento", "Oakland", "San Diego", "Las Vegas", "Salt Lake City",
#     "Jacksonville", "Miami", "Burlington", "Spokane", "San Antonio", "Charlottesville", 
#     "Durham", "Hartford", "Denver", "Omaha", "Phoenix", "Columbus", "Cincinnati", 
#     "Nashville", "Charlotte", "Indianapolis", "Portland", "Baltimore", "Milwaukee", 
#     "Atlanta", "Minneapolis", "Tulsa", "Kansas City", "Fresno", "Tucson", "Louisville",
#     "Albuquerque", "Memphis", "Chattanooga", "Fort Worth", "Boulder", "Oklahoma City"
# ]

# city_states = {
#      "New York": "NY", "Los Angeles": "CA", "Chicago": "IL", "Boston": "MA", "Seattle": "WA", "Ann Arbor": "MI", 
#     "Philadelphia": "PA", "Detroit": "MI", "Pittsburgh": "PA", "Houston": "TX", "Dallas": "TX", "Austin": "TX", 
#     "San Francisco": "CA", "Sacramento": "CA", "Oakland": "CA", "San Diego": "CA", "Las Vegas": "NV", "Salt Lake City": "UT",
#     "Jacksonville": "FL", "Miami": "FL", "Burlington": "VT", "Spokane": "WA", "San Antonio": "TX", "Charlottesville": "VA", 
#     "Durham": "NC", "Hartford": "CT", "Denver": "CO", "Omaha": "NE", "Phoenix": "AZ", "Columbus": "OH", "Cincinnati": "OH", 
#     "Nashville": "TN", "Charlotte": "NC", "Indianapolis": "IN", "Portland": "OR", "Baltimore": "MD", "Milwaukee": "WI", 
#     "Atlanta": "GA", "Minneapolis": "MN", "Tulsa": "OK", "Kansas City": "MO", "Fresno": "CA", "Tucson": "AZ", "Louisville": "KY",
#     "Albuquerque": "NM", "Memphis": "TN", "Chattanooga": "TN", "Fort Worth": "TX", "Boulder": "CO", "Oklahoma City": "OK"
# }

def setup_database():
    conn = sqlite3.connect("final_data.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cities (
                   id INTEGER PRIMARY KEY AUTOINCREMENT,
                   city_name TEXT UNIQUE)
                   """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS weather (
                   id INTEGER PRIMARY KEY AUTOINCREMENT,
                   city_id INTEGER,
                   temperature_f REAL,
                   feels_like_f REAL,
                   humidity INTEGER,
                   wind_speed_mph REAL,
                   weather_description TEXT,
                   observation_time TEXT,
                   fetched_at TEXT,
                   FOREIGN KEY(city_id) REFERENCES cities(id))
                   """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS crime (
                   id INTEGER PRIMARY KEY AUTOINCREMENT,
                   city_id INTEGER,
                   offense TEXT,
                   offense_count INTEGER,
                   year INTEGER,
                   UNIQUE(city_id, offense, year),
                   FOREIGN KEY(city_id) REFERENCES cities(id))
                   """)
    conn.commit()
    return conn

# def read_weather_data(city, json_file):
#     params = {
#         "access_key": weatherstack_api,
#         "query": city,
#         "units": "f"
#     }
#     response = requests.get(weather_url, params=params)
#     response_json = response.json()
#     try:
#         try:
#             with open(json_file, 'r') as f:
#                 prev_data = json.load(f)
#                 prev_data.append(response_json)
#         except (FileNotFoundError, json.JSONDecodeError):
#             prev_data = []
#         prev_data.append(response_json)
#         with open(json_file, 'w') as f:
#             json.dump(prev_data, f, indent=2)
#             print(f'Saved to {json_file}')
#     except:
#         return 'Error saving json'
    
    
# def load_weather_cities_json(cities):
#     for city in cities:
#         read_weather_data(city, 'city_weather_data.json')
#         print(f'Successfully saved {city}')

def read_crime_data(state):
    url = f"https://api.usa.gov/crime/fbi/sapi/api/summarized/state/{state}/all-offenses"
    params = {"api_key": crime_data_api}
    response = requests.get(url, params = params)

    print(f"Status: {response.status_code}")
 
    try:
        data = response.json()
    except:
        print("Invalid response for state:", state)
        return None
    if "results" not in data:
        print("No results for:", state, data)
        return None
    return data

def build_weather_table(conn, cities):
    cursor = conn.cursor()
    cursor.execute("SELECT city_name FROM cities")
    existing_cities = {row[0] for row in cursor.fetchall()}
    count = 0
    for city in cities:
        if count >= 25:
            break
        data = read_weather_data(city)
        time.sleep(1)
        if "current" not in data:
            print("Skipping (no current data):", city, data)
            continue
        cursor.execute("""
            INSERT OR IGNORE INTO cities (city_name)
            VALUES (?)
                       """, (city,))
        cursor.execute("SELECT id FROM cities WHERE city_name = ?", (city,))
        city_id = cursor.fetchone()[0]
        timestamp = datetime.now().isoformat()
        cursor.execute("""
            INSERT INTO weather (
                       city_id, temperature_f, feels_like_f, humidity,
                       wind_speed_mph, weather_description,
                       observation_time, fetched_at)
                       VALUES (?,?,?,?,?,?,?,?)
                       """, (
                           city_id,
                           data["current"]["temperature"],
                           data["current"]["feelslike"],
                           data["current"]["humidity"],
                           data["current"]["wind_speed"],
                           data["current"]["weather_descriptions"][0],
                           data["location"]["localtime"],
                           timestamp
                       ))
        count += 1
    conn.commit()
    print(f"Inserted {count} NEW weather rows this run")

def build_crime_table(conn, cities):
    cursor = conn.cursor()
    count = 0
    processed_states = set()
    for city in cities:
        if count >= 25:
            break
        if city not in city_states:
            continue
        state = city_states[city]
        if state in processed_states:
            continue
        processed_states.add(state)
        cursor.execute("SELECT id FROM cities WHERE city_name =?", (city,))
        result = cursor.fetchone()
        if not result:
            continue
        city_id = result[0]
        data = read_crime_data(state)
        if not data:
            continue
        for entry in data["results"]:
            year = entry.get("year")
            offense = entry.get("offense_name", "").lower().replace(" ", "_")
            count_val = entry.get("count", 0)
            if offense in ("burglary", "robbery", "violent_crime", "property_crime"):
                cursor.execute("""
                    INSERT OR IGNORE INTO crime (city_id, offense, offense_count, year)
                    VALUES (?,?,?,?)
                               """, (city_id, offense, count_val, year))
                count += 1
                if count >= 25:
                    break
            if count>= 25:
                break
    conn.commit()
    print(f"Inserted {count} NEW crime rows this run")




### THE FOLLOWING FUNCTIONS ARE FOR THE CALCULATION PORTION OF THE PROJECT

def calculate_average_temp(conn):
    cursor = conn.cursor()
    cursor.execute("""
        SELECT cities.city_name, AVG(weather.temperature_f)
        FROM weather
        JOIN cities ON weather.city_id = cities.id
        GROUP BY cities.city_name
        ORDER BY cities.city_name
                   """)
    results = cursor.fetchall()
    avg_temps = {city: round(avg, 2) for city, avg in results}
    return sorted(avg_temps.items(), key=lambda x: x[1], reverse=True)

def calculate_average_feels_like(conn):
    cursor = conn.cursor()
    cursor.execute("""
        SELECT cities.city_name, AVG(weather.feels_like_f)
        FROM weather
        JOIN cities ON weather.city_id = cities.id
        GROUP BY cities.city_name
        ORDER BY cities.city_name
                   """)
    results = cursor.fetchall()
    avg_feels = {city: round(avg, 2) for city, avg in results}
    return sorted(avg_feels.items(), key=lambda x: x[1], reverse=True)

def find_most_common_crime(conn):
    cursor = conn.cursor()
    cursor.execute("""
        SELECT cities.city_name, crime.offense, SUM(crime.offense_count) as total
        FROM crime 
        JOIN cities on crime.city_id = cities.id
        GROUP BY cities.city_name, crime.offense
                   """)
    results = cursor.fetchall()
    city_crime = {}
    for city, offense, total in results:
        if city not in city_crime or total > city_crime[city][1]:
            city_crime[city] = (offense, total)
    return city_crime

def weather_crime_relationship(conn):
    cursor = conn.cursor()
    avg_temps = dict(calculate_average_temp(conn))
    avg_feels = dict(calculate_average_feels_like(conn))
    common_crimes = find_most_common_crime(conn)
    cursor.execute("""
        SELECT cities.city_name, SUM(crime.offense_count)
        FROM crime
        JOIN cities ON crime.city_id = cities.id
        GROUP BY cities.city_name
                   """)
    crime_totals = {city: total for city, total in cursor.fetchall()}
    results = []
    for city in avg_temps:
        if city in crime_totals and city in common_crimes:
            results.append({
                "city": city,
                "avg_temp": avg_temps[city],
                "avg_feels_like": avg_feels.get(city),
                "total_crime": crime_totals[city],
                "most_common_crime": common_crimes[city][0]
            })

    return sorted(results, key=lambda x: x["total_crime"], reverse=True)

if __name__ == "__main__":
    # conn = setup_database()
    # build_weather_table(conn, cities)
    # build_crime_table(conn, cities)
    # conn.close()
    print('hi')


