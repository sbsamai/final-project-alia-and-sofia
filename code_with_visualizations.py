import sqlite3
import os
import requests
import json
from datetime import datetime
import time
import openmeteo_requests
import matplotlib.pyplot as plt
import pandas as pd
import requests_cache
from retry_requests import retry

cities = [
     "New York", "Los Angeles", "Chicago", "Boston", "Seattle", "Ann Arbor", 
     "Philadelphia", "Detroit", "Pittsburgh", "Houston", "Dallas", "Austin", 
     "San Francisco", "Sacramento", "Oakland", "San Diego", "Las Vegas", "Salt Lake City",
     "Jacksonville", "Miami", "Burlington", "Spokane", "San Antonio", "Charlottesville", 
     "Durham", "Hartford", "Denver", "Omaha", "Phoenix", "Columbus", "Cincinnati", 
     "Nashville", "Charlotte", "Indianapolis", "Portland", "Baltimore", "Milwaukee", 
     "Atlanta", "Minneapolis", "Tulsa", "Kansas City", "Fresno", "Tucson", "Louisville",
     "Albuquerque", "Memphis", "Chattanooga", "Fort Worth", "Boulder", "Oklahoma City", "Bozeman",
     "Bloomfield Hills", "Stratton", "Birmingham", "Selma", "Montgomery", "New Orleans",
     "Savannah", "New Haven", "New Buffalo", "Wilton", "Athens", "Fort Lauderdale", "Jackson",
     "Richmond", "Wichita", "Livonia", "Knoxville", "Ithaca", "West Bloomfield", "Royal Oak", 
     "Anaheim", "La Jolla", "Calabasas", "Darien", "Dexter", "Plymouth", "Westport", "Canton",
     "Midland", "San Jose", "San Clemente", "Aspen", "Vail", "Jackson Hole", "St. Louis", 
     "Dalton", "Troy", "Litchfield", "Providence", "Malibu", "Syracuse", "Buffalo", "Albany",
     "Tallahassee", "Anchorage", "Orlando", "Jensen Beach", "New Milford", "Trenton"
 ]


dog_url = "https://dogapi.dog/api/v2/breeds"

base_dir = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(base_dir, "final_data.db")

def setup_database():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cities (
                   city_id INTEGER PRIMARY KEY,
                   city_name TEXT,
                   latitude REAL,
                   longitude REAL)
                   """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS daily_weather (
                   id INTEGER PRIMARY KEY AUTOINCREMENT,
                   city_id INTEGER,
                   date TEXT,
                   temp_max REAL,
                   temp_min REAL,
                   UNIQUE(city_id, date))
                   """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS dog_breeds (
                   id INTEGER PRIMARY KEY AUTOINCREMENT,
                   breed_name TEXT UNIQUE,
                   male_weight TEXT,
                   female_weight TEXT)
                   """)
    # tmdb
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS movies (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT UNIQUE,
        year TEXT,
        rating TEXT,
        metascore INTEGER
    )
""")
    conn.commit()
    return conn


def read_weather_data_json():
    setup_database()
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    city_id = 0
    max_cities_per_run = 25
    cur.execute("SELECT COUNT (*) FROM cities")
    cities_already_stored = cur.fetchone()[0]
    if cities_already_stored >= 100:
        print("Already have 100 cities, skipping 25 rule.")
        conn.close()
        return

    cache_session = requests_cache.CachedSession('.cache', expire_after = -1)
    retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
    openmeteo = openmeteo_requests.Client(session = retry_session)
    url = "https://archive-api.open-meteo.com/v1/archive"
    params = {
        "latitude": [40.7143, 34.0522, 41.85, 42.3584, 47.6062, 42.2776, 39.9524, 42.3314, 40.4406, 29.7633, 32.7831, 30.2672, 37.7749, 38.5816, 37.8044, 32.7157, 36.175, 40.7608, 30.3322, 25.7743, 44.4759, 47.6597, 29.4241, 38.0293, 35.994, 41.7637, 39.7392, 41.2563, 33.4484, 39.9612, 39.1271, 36.1659, 35.2271, 39.7684, 45.5234, 39.2904, 43.0389, 33.749, 44.98, 36.154, 39.0997, 36.7477, 32.2217, 38.2542, 35.0845, 35.1495, 35.0456, 32.7254, 40.015, 35.4676, 45.6797, 42.5836, 43.0429, 33.5207, 32.4074, 32.3668, 29.9547, 32.0835, 41.3081, 41.7939, 41.1954, 33.9609, 26.1223, 32.2988, 37.5538, 37.6922, 42.3684, 35.9606, 42.4406, 42.5689, 42.4895, 33.8353, 32.8473, 34.1578, 41.0787, 42.3383, 42.3714, 41.1415, 42.3087, 31.9974, 37.3394, 33.427, 39.1911, 39.6403, 43.6066, 38.6273, 34.7698, 42.6056, 41.7473, 41.824, 34.0258, 43.0481, 42.8865, 42.6526, 30.4383, 61.2181, 28.5383, 27.2545, 41.577, 40.2171],
        "longitude": [-74.006, -118.2437, -87.65, -71.0598, -122.3321, -83.7409, -75.1636, -83.0457, -79.9959, -95.3633, -96.8067, -97.7431, -122.4194, -121.4944, -122.2708, -117.1647, -115.1372, -111.8911, -81.6556, -80.1937, -73.2121, -117.4291, -98.4936, -78.4767, -78.8986, -72.6851, -104.9847, -95.9404, -112.074, -82.9988, -84.5144, -86.7844, -80.8431, -86.158, -122.6762, -76.6122, -87.9065, -84.388, -93.2638, -95.9928, -94.5786, -119.7724, -110.9265, -85.7594, -106.6511, -90.049, -85.3097, -97.3208, -105.2706, -97.5164, -111.0386, -83.2455, -72.9109, -86.8025, -87.0211, -86.3, -90.0751, -81.0998, -72.9282, -86.7439, -73.4379, -83.3779, -80.1434, -90.1848, -77.4603, -97.3375, -83.3527, -83.9207, -76.4966, -83.3836, -83.1446, -117.9145, -117.2742, -118.6384, -73.4693, -83.8895, -83.4702, -73.3579, -83.4822, -102.0779, -121.895, -117.612, -106.8175, -106.3742, -110.7385, -90.1979, -84.9702, -83.1499, -73.1887, -71.4128, -118.7804, -76.1474, -78.8784, -73.7562, -84.2807, -149.9003, -81.3792, -80.2298, -73.4085, -74.7429],
        "start_date": "2026-03-30",
        "end_date": "2026-03-30",
        "daily": ["temperature_2m_max", "temperature_2m_min"],
        "timezone": "auto",
        "temperature_unit": "fahrenheit",
        "wind_speed_unit": "mph",
    }
    responses = openmeteo.weather_api(url, params = params)
    for response in responses:
        city_id += 1
        if city_id <= cities_already_stored:
            continue
        if city_id > cities_already_stored + max_cities_per_run:
            break
        cur.execute("""
            INSERT OR IGNORE INTO cities (city_id, city_name, latitude, longitude)
                    VALUES (?,?,?,?)
                    """, (city_id, cities[city_id -1], response.Latitude(), response.Longitude()))
        
        # print(f"\nCoordinates: {response.Latitude()}°N {response.Longitude()}°E")
        # print(f"Elevation: {response.Elevation()} m asl")
        # print(f"Timezone: {response.Timezone()}{response.TimezoneAbbreviation()}")
        # print(f"Timezone difference to GMT+0: {response.UtcOffsetSeconds()}s")
        
        daily = response.Daily()
        daily_temperature_2m_max = daily.Variables(0).ValuesAsNumpy()
        daily_temperature_2m_min = daily.Variables(1).ValuesAsNumpy()
        
        daily_data = {"date": pd.date_range(
            start = pd.to_datetime(daily.Time() + response.UtcOffsetSeconds(), unit = "s", utc = True),
            end =  pd.to_datetime(daily.TimeEnd() + response.UtcOffsetSeconds(), unit = "s", utc = True),
            freq = pd.Timedelta(seconds = daily.Interval()),
            inclusive = "left"
        )}
        
        daily_data["temperature_2m_max"] = daily_temperature_2m_max
        daily_data["temperature_2m_min"] = daily_temperature_2m_min
        
        daily_dataframe = pd.DataFrame(data = daily_data)
        for _, row in daily_dataframe.iterrows():
            try:
                cur.execute("""
                    INSERT INTO daily_weather (city_id, date, temp_max, temp_min)
                            VALUES (?, ?, ?, ?)
                            """, (city_id,
                                  str(row["date"]),
                                  float(row["temperature_2m_max"]),
                                  float(row["temperature_2m_min"])))
            except sqlite3.IntegrityError:
                continue
    conn.commit()
    conn.close()


def read_dog_data_json():
    setup_database()
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM dog_breeds")
    total_rows = cur.fetchone()[0]
    if total_rows >= 100:
        print("Already have 100 breeds")
        conn.close()
        return

    rows_added = 0
    max_per_run = min(25, 100 - total_rows)

    next_url = dog_url
    while next_url and rows_added < max_per_run:
        response = requests.get(next_url).json()
        for dog in response["data"]:
            if rows_added >= max_per_run:
                break

            breed = dog["attributes"]["name"]
            male_weight = json.dumps(dog["attributes"]["male_weight"])
            female_weight = json.dumps(dog["attributes"]["female_weight"])
            try:
                cur.execute("""
                    INSERT INTO dog_breeds (breed_name, male_weight, female_weight)
                    VALUES (?, ?, ?)
                            """, (breed, male_weight, female_weight))
                # print(f"Added: {breed}")
                rows_added +=1
            except sqlite3.IntegrityError:
                continue
        next_url = response["links"].get("next")
    conn.commit()
    conn.close()



### THE FOLLOWING FUNCTIONS ARE FOR THE CALCULATION PORTION OF THE PROJECT

def calculate_average_high():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT city_id, AVG(temp_max)
        FROM daily_weather
        GROUP BY city_id
                   """)
    results = cursor.fetchall()
    conn.close()
    return results
    


def calculate_average_low():
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("""
        SELECT city_id, AVG(temp_min)
        FROM daily_weather
        GROUP BY city_id
                """)
    results = cur.fetchall()
    conn.close()
    return results

def total_male_small_dogs():
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT male_weight FROM dog_breeds")
    rows = cur.fetchall()
    conn.close
    count = 0
    for row in rows:
        weight = json.loads(row[0])
        if weight["max"] < 20:
            count += 1
    return count



def total_male_large_dogs():
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT male_weight FROM dog_breeds")
    rows = cur.fetchall()
    conn.close()
    count = 0
    for row in rows:
        weight = json.loads(row[0])
        if weight["max"] > 50:
            count += 1
    return count



### THESE ARE VISUALIZATION FUNCTIONS

def plot_avg_temps():
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT city_id, city_name FROM cities ORDER BY city_id")
    city_rows = cur.fetchall()
    conn.close
    
    highs = calculate_average_high()
    lows = calculate_average_low()
    city_names = [row[1] for row in city_rows]
    avg_highs = [row[1] for row in highs]
    avg_lows = [row[1] for row in lows]

    plt.figure(figsize=(12,6))
    plt.scatter(city_names, avg_highs, color="purple", s=20, label="Average High")
    plt.scatter(city_names, avg_lows, color="red", s=20, label="Average Low")
    plt.xlabel("City ID")
    plt.ylabel("Temperature (Farenheight)")
    plt.title("Average High and Low Temps Across 100 Cities (3/2025 to 3/2026)")
    plt.legend()
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.show()

def plot_male_dog_weights():
    small = total_male_small_dogs()
    large = total_male_large_dogs()
    categories = ["Small (under 20 lbs)", "Large (over 50 lbs)"]
    values = [small, large]
    plt.bar(categories, values, color=["blue", "red"])
    plt.xlabel("Dog Size")
    plt.ylabel("Number of Breeds")
    plt.title("Total Large and Small Male Dogs")
    plt.ylim(0,100)
    plt.tight_layout()
    plt.show()

# bonus movie API
def read_movie_data_json():
    setup_database()
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    # check how many movies already stored
    cur.execute("SELECT COUNT(*) FROM movies")
    total_rows = cur.fetchone()[0]

    if total_rows >= 100:
        print("Already have 100 movies")
        conn.close()
        return

    # enforce 25 per run rule
    max_per_run = min(25, 100 - total_rows)
    rows_added = 0

    # list of movies (runs through these over multiple runs)
    movie_titles = [
        "Inception", "Titanic", "Avatar", "The Dark Knight", "Interstellar",
        "Frozen", "Gladiator", "The Matrix", "Joker", "Toy Story",
        "The Lion King", "Forrest Gump", "Avengers", "Up", "Shrek",
        "Finding Nemo", "Black Panther", "Iron Man", "Cars", "Coco",
        "Brave", "Moana", "Soul", "Ratatouille", "Monsters Inc",
        "The Godfather", "Pulp Fiction", "Fight Club", "The Shawshank Redemption",
        "La La Land", "Whiplash", "Parasite", "1917", "Dune",
        "Oppenheimer", "Barbie", "The Social Network", "Get Out", "Her"
    ]

    for title in movie_titles:
        if rows_added >= max_per_run:
            break

        url = f"http://www.omdbapi.com/?apikey=1846eeb9&t={title}"

        try:
            data = requests.get(url).json()

            if data["Response"] == "True":
                metascore = data.get("Metascore")
                metascore = int(metascore) if metascore != "N/A" else None

                cur.execute("""
                    INSERT OR IGNORE INTO movies (title, year, rating, metascore)
                    VALUES (?, ?, ?, ?)
                """, (
                    data.get("Title"),
                    data.get("Year"),
                    data.get("imdbRating"),
                    metascore
                ))

                rows_added += 1

        except Exception as e:
            print(f"Error with {title}: {e}")
            continue

    conn.commit()
    conn.close()


def average_movie_score():
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    cur.execute("""
        SELECT AVG(metascore) FROM movies
        WHERE metascore IS NOT NULL
    """)

    result = cur.fetchone()[0]
    conn.close()
    return result


def write_movie_results():
    avg = average_movie_score()

    with open("movie_results.txt", "w") as f:
        f.write(f"Average Metascore across movies: {avg}\n")

# movie visualization       
def plot_movie_scores():
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    cur.execute("""
        SELECT title, metascore FROM movies
        WHERE metascore IS NOT NULL
    """)
    data = cur.fetchall()
    conn.close()

    titles = [row[0] for row in data]
    scores = [row[1] for row in data]

    plt.figure(figsize=(10,5))
    plt.bar(titles, scores)

    plt.xticks(rotation=45)
    plt.xlabel("Movies")
    plt.ylabel("Metascore")
    plt.title("Movie Metascores")

    plt.tight_layout()
    plt.show()

# second bonus visual for max pts
def plot_movie_years():
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    cur.execute("""
        SELECT year FROM movies
        WHERE year IS NOT NULL
    """)
    data = cur.fetchall()
    conn.close()

    # convert to decades
    decades = []

    for row in data:
        year = row[0]
        if year != "N/A":
            y = int(year[:4])
            decade = (y // 10) * 10   # turns 1997 → 1990
            decades.append(decade)

    # count how many per decade
    counts = {}
    for d in decades:
        counts[d] = counts.get(d, 0) + 1

    # sort for clean graph
    sorted_decades = sorted(counts.keys())
    values = [counts[d] for d in sorted_decades]

    # make labels like "1990s"
    labels = [str(d) + "s" for d in sorted_decades]

    plt.figure(figsize=(8,5))
    plt.bar(labels, values, color="pink", edgecolor="black")

    plt.xlabel("Decade")
    plt.ylabel("Number of Movies")
    plt.title("Movies by Decade")

    plt.tight_layout()
    plt.show()
    
if __name__ == "__main__":
    read_weather_data_json()
    read_dog_data_json()
    calculate_average_high()
    calculate_average_low()
    total_male_small_dogs()
    total_male_large_dogs()
    plot_male_dog_weights()
    plot_avg_temps()
    read_movie_data_json()
    write_movie_results()
    plot_movie_scores() 
    plot_movie_years()