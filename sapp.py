import streamlit as st
import xgboost as xgb
import pandas as pd
from geopy.distance import geodesic
from sklearn.preprocessing import StandardScaler, LabelEncoder
import requests
import numpy as np

# Initialize OpenCage Geocoding API
class OpenCageGeocodingAPI:
    def __init__(self, api_key):
        self.api_key = api_key

    def geocode(self, query):
        url = "https://api.opencagedata.com/geocode/v1/json?q={}&key={}".format(query, self.api_key)
        response = requests.get(url)
        data = response.json()

        if data["results"]:
            latitude = data["results"][0]["geometry"]["lat"]
            longitude = data["results"][0]["geometry"]["lng"]
            return latitude, longitude
        else:
            raise Exception("No results found for query: {}".format(query))

# Load the XGBoost model
loaded_model = xgb.Booster({'nthread': 4})
loaded_model.load_model('xgb_model.dat')

# Create Streamlit app
st.title("Delivery Time Prediction")

# Get sender's and recipient's addresses
sender_address = st.text_input("Enter sender's address:")
recipient_address = st.text_input("Enter recipient's address:")

if st.button("Predict Delivery Time"):
    try:
        # Geocode sender's and recipient's addresses
        geocoding_api = OpenCageGeocodingAPI("74ef4d846c9f408fb5386665f521f3bc")
        sender_latitude, sender_longitude = geocoding_api.geocode(sender_address)
        recipient_latitude, recipient_longitude = geocoding_api.geocode(recipient_address)

        # Prepare the DataFrame for prediction
        data = {
            'Delivery_person_Age': 30.0,
            'Delivery_person_Ratings': 4.5,
            'Restaurant_latitude': sender_latitude,
            'Restaurant_longitude': sender_longitude,
            'Delivery_location_latitude': recipient_latitude,
            'Delivery_location_longitude': recipient_longitude,
            'Weather_conditions': 'Sunny',
            'Road_traffic_density': 'Medium',
            'Vehicle_condition': 0,
            'Type_of_order': 'Snack',
            'year': 2022,
            'day_of_week': 0,
            'is_month_start': 0,
            'is_month_end': 0,
            'is_quarter_start': 0,
            'is_quarter_end': 0,
            'is_year_start': 0,
            'is_year_end': 0,
            'is_weekend': 0,
            'order_prepare_time': 0.0
        }

        df = pd.DataFrame([data])

        # Calculate the distance between restaurant location & delivery location
        def calculate_distance(df):
            df['distance'] = np.zeros(len(df))
            restaurant_coordinates = df[['Restaurant_latitude', 'Restaurant_longitude']].to_numpy()
            delivery_location_coordinates = df[['Delivery_location_latitude', 'Delivery_location_longitude']].to_numpy()
            df['distance'] = np.array([geodesic(restaurant, delivery) for restaurant, delivery in zip(restaurant_coordinates, delivery_location_coordinates)])
            df['distance'] = df['distance'].astype("str").str.extract('(\d+)').astype("int64")

        calculate_distance(df)

        # Label encoding for categorical columns
        def label_encoding(df):
            categorical_columns = df.select_dtypes(include='object').columns
            label_encoder = LabelEncoder()
            df[categorical_columns] = df[categorical_columns].apply(lambda col: label_encoder.fit_transform(col))

        label_encoding(df)

        # Standardize data
        scaler = StandardScaler()
        scaler.fit(df)
        df = scaler.transform(df)

        # Make predictions using the loaded model
        predictions = loaded_model.predict(xgb.DMatrix(df))

        st.write(f"Predicted delivery time: {predictions[0]}")
    except Exception as e:
        st.error(f"An error occurred: {e}")

st.write("Note: The application uses a pre-trained model to predict delivery time based on input addresses.")
