import streamlit as st
import requests
from datetime import datetime

'''
# TaxiFareModel front
'''

# 1. Controllers
date        = st.date_input("Date", value=datetime.now())
time        = st.time_input("Time", value=datetime.now().time())
pickup_lon  = st.number_input("Pickup longitude",  value=-73.985130)
pickup_lat  = st.number_input("Pickup latitude",   value=40.758896)
dropoff_lon = st.number_input("Dropoff longitude", value=-73.985130)
dropoff_lat = st.number_input("Dropoff latitude",  value=40.648410)
passengers  = st.number_input("Passenger count",   value=1, min_value=1, max_value=8)

url = 'https://taxifare-203500939035.europe-west1.run.app/predict'

# 2. Build params dict
params = {
    "pickup_datetime":   f"{date} {time}",
    "pickup_longitude":  pickup_lon,
    "pickup_latitude":   pickup_lat,
    "dropoff_longitude": dropoff_lon,
    "dropoff_latitude":  dropoff_lat,
    "passenger_count":   passengers,
}

# 3. Call the API
response = requests.get(url, params=params)

# 4. Retrieve prediction from JSON
prediction = response.json()["fare"]

# Display prediction
st.write(f"Estimated fare: **${prediction:.2f}**")
