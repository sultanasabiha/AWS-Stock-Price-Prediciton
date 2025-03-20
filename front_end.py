
import streamlit as st
import requests
import yfinance as yf
import pandas as pd
import numpy as np
import json


ENDPOINT_API_URL = "enter_endpoint_api_url_here"
SUBSCRIPTION_API_URL = "enter_subscription_api_url_here"

st.title("Stock Price Prediction")

# Button to fetch prediction
if st.button("Get Prediction"):
    start_date = "2024-01-05"
    duration=1
    real_time_data = yf.download('AAPL', start=start_date, end=pd.Timestamp(start_date)+pd.Timedelta(days=duration))
    real_time_data.columns = real_time_data.columns.droplevel(1)
    real_time_data=np.array(real_time_data.reset_index(drop=True))
    input_data={"data":real_time_data.tolist()}

    with st.spinner("Fetching prediction..."):
        try:
       
            response = requests.post(ENDPOINT_API_URL, json=input_data)
            if response.status_code == 200:  
                #Parse the json
                response_data = response.json()
                body_data=response_data.get('body')
                body=json.loads(body_data)

                st.success(f"Prediction for AAPL : ${','.join([str(n) for n in body['result']])}")

            else:
                st.error(f"Failed to fetch prediction. Status Code: {response.status_code}")
        except Exception as e:
            st.error(f"Error: {e}")

# Subscription Section
st.subheader("Subscribe for Updates")

# Input field for email
email = st.text_input("Enter your email:", "")

# Subscription button
if st.button("Subscribe"):
    if not email:
        st.error("Please enter your email")
    else:
        with st.spinner("Subscribing..."):
            try:
                json={"email":email}
                
                response = requests.post(SUBSCRIPTION_API_URL, json=json)
                if response.status_code == 200:
                    st.success("Successfully subscribed! You'll receive stock updates via email.")
                else:
                    st.error(f"Failed to subscribe. Status Code: {response.status_code}")
            except Exception as e:
                st.error(f"Error: {e}")