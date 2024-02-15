# Imports
import pymongo
from pymongo import MongoClient
import requests
import pandas as pd
from datetime import datetime, timedelta
import time
import os

# Your NASA API key
api_key = os.environ['NASA_API_KEY']

my_secret = os.environ['MONGO_URI']


def fetch_apod(api_key):
  # Get today's date
  today = datetime.today().strftime("%Y-%m-%d")

  # Define the endpoint URL for the APOD API
  apod_url = f'https://api.nasa.gov/planetary/apod?api_key={api_key}&date={today}'

  # Make a GET request to the APOD API
  response = requests.get(apod_url)

  # Initialize an empty dictionary to store APOD data
  apod_data = {}

  # Check if the request was successful (status code 200)
  if response.status_code == 200:
    # Parse the JSON data
    apod_data = response.json()
  else:
    print("Failed to retrieve data from the APOD API.")

  return apod_data


def update_database(apod_data):
  # Connect to MongoDB
  client = MongoClient(my_secret)
  db = client[
      'astronomy']  # Replace 'your_database_name' with your database name
  collection = db[
      'apod']  # Replace 'your_collection_name' with your collection name

  # Extract relevant information
  title = apod_data.get('title', '')
  date = apod_data.get('date', '')
  explanation = apod_data.get('explanation', '')
  image_url = apod_data.get('url', '')

  # Check if the image already exists in the database
  existing_image = collection.find_one({'Date': date})

  if existing_image:
    print("Image already exists in the database.")
    return

  # Create a pandas DataFrame with the data for today's image
  df = pd.DataFrame({
      'Title': [title],
      'Date': [date],
      'Explanation': [explanation],
      'Image URL': [image_url]
  })

  # Convert DataFrame to dictionary
  data_dict = df.to_dict(orient='records')

  # Insert data into MongoDB collection
  collection.insert_many(data_dict)

  # Confirm insertion
  print("Data inserted successfully into MongoDB.")


def main():
  while True:
    try:
      apod_data = fetch_apod(api_key)
      update_database(apod_data)
      # Wait for an hour before checking again
      time.sleep(3600)
    except Exception as e:
      print(f"An error occurred: {e}")
      # Wait for 5 minutes before retrying
      time.sleep(300)


if __name__ == "__main__":
  main()
