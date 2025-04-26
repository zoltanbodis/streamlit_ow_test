import streamlit as st
import pandas as pd
import requests
import plotly.express as px
import pprint as pp

APPID = st.secrets["ow"]["appid"]
BASE_URL = st.secrets["ow"]["base_url"]

#@st.cache_data(ttl=86400)
def get_current_weather(city, unit, lang):
    print(f"Get weather for {city}, {unit}, {lang}...")

    url = f"{BASE_URL}/weather?appid={APPID}&q={city}&units={unit}&lang={lang}"

    response = requests.get(url)

    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"Failed to fetch data: {response.status_code} - {response.text}")

st.title("Robot Dreams Python - Weather Map & Data Visualization App")
city = st.text_input("Enter city name", value="Budapest").capitalize()

st.header(f"Current weather in {city}")

weather = get_current_weather(city, "metric", "en")

if weather is not None:

    icon, temp, hum, wind = st.columns(4)

    #KPI
    with icon:
        description = weather['weather'][0]['description'].capitalize()
        icon_code = weather['weather'][0]['icon']
        icon_url = f"http://openweathermap.org/img/wn/{icon_code}@2x.png"
        
        st.markdown(
            f"<div style='text-align: center;'><div style='text-align: center; color: #252525; font-size: 0.85rem;'>{description}</div><img src='{icon_url}' width='50'/></div>",
            unsafe_allow_html=True
        )
    with temp:
        st.metric(label="Temperature (\u00B0C)", value=f"{weather['main']['temp']}")
    with hum:
        st.metric(label="Humidity (%)", value=f"{weather['main']['humidity']}")
    with wind:
        st.metric(label="Wind Speed (m/s)", value=f"{weather['wind']['speed']}")
    

    #MAP   
    df = pd.DataFrame({
        'lat': [weather['coord']['lat']],
        'lon': [weather['coord']['lon']]
    })

    st.map(df, zoom=12)    

    #st.write(weather)
