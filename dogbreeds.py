import requests
import json
import unittest
import os
import sqlite3

dog_url = "https://dogapi.dog/api/v2/breeds"

def read_dog_data_json(filename):
    conn = sqlite3.connect("final_data.db")
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM dog_breeds")
    total_rows = cur.fetchone()[0]
    if total_rows >= 100:
        print("Already have 100 breeds")
        conn.close()
        return

    rows_added = 0
    max_per_run = 25

    next_url = dog_url
    while next_url:
        response = requests.get(next_url)
        response = response.json()
        for dog in response["data"]:
            if rows_added >= max_per_run:
                break

            breed = dog["attributes"]["name"]
            male_weight = dog["attributes"]["male_weight"]
            female_weight = dog["attributes"]["female_weight"]
            print(f"Breed: {breed} | Male: {male_weight} | Female: {female_weight}")
            try:
                cur.execute("""
                    INSERT INTO dog_breeds (breed_name, male_weight, female_weight)
                    VALUES (?, ?, ?)
                            """, (breed, male_weight, female_weight))
                print(f"Added: {breed}")
                rows_added +=1
            except sqlite3.IntegrityError:
                continue
        if rows_added >= max_per_run:
            break
        next_url = response["links"]["next"]
    conn.commit()
    conn.close()


if __name__ == "__main__":
    read_dog_data_json("text")