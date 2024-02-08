def updatedb():
  api_key = creds.NASA_API_KEY

  today = datetime.today().strftime("%Y-%m-%d")

  # Define the endpoint URL for the APOD API
  apod_url = f'https://api.nasa.gov/planetary/apod?api_key={api_key}&date={today}'

  # Make a GET request to the APOD API
  response = requests.get(apod_url)

  apod_data = {}

  if response.status_code == 200:
    apod_data = response.json()
  else:
    print("Failed to retrieve data from the APOD API.")
    return

  # Extract relevant information
  title = apod_data.get('title', '')
  date = apod_data.get('date', '')
  explanation = apod_data.get('explanation', '')
  image_url = apod_data.get('url', '')

  # Connect to MongoDB
  client = MongoClient(creds.MONGO_URI)
  db = client["astronomy"]
  collection = db["apod"]

  # Check if the record for today already exists in the database
  if collection.find_one({"Date": date}):
    print("Record for today already exists in the database.")

  # Create a pandas DataFrame with the data for today's image
  df = pd.DataFrame({
      'Title': [title],
      'Date': [date],
      'Explanation': [explanation],
      'Image URL': [image_url]
  })

  # Convert DataFrame to dictionary
  data_dict = df.to_dict(orient='records')

  # Insert the record into the MongoDB collection
  collection.insert_many(data_dict)

  print("Data inserted successfully into MongoDB.")


def schedule_daily_update():
  schedule.every().day.at("23:00").do(updatedb)

  # Keep the program running to allow the scheduler to continue executing
  while True:
    schedule.run_pending()
    time.sleep(1)


# Start the scheduler in a separate thread
scheduler_thread = threading.Thread(target=schedule_daily_update)
scheduler_thread.start()