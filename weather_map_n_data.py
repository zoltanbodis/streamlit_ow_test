import streamlit as st
import pandas as pd
import requests
import plotly.express as px
import pprint as pp

APPID = st.secrets["ow"]["appid"]
BASE_URL = st.secrets["ow"]["base_url"]

@st.cache_data(ttl=86400)
def get_current_weather(city, unit, lang):
    print(f"Get weather for {city}, {unit}, {lang}...")

    url = f"{BASE_URL}/weather?appid={APPID}&q={city}&units={unit}&lang={lang}"

    response = requests.get(url)

    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"Failed to fetch data: {response.status_code} - {response.text}")

@st.cache_data(ttl=86400)
def get_weather_forecast(city, unit, lang):

    url = f"{BASE_URL}/forecast?appid={APPID}&q={city}&units={unit}&lang={lang}"

    response = requests.get(url)

    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"Failed to fetch data: {response.status_code} - {response.text}")

st.title("Robot Dreams Python - Weather Map & Data Visualization App")
city = st.text_input("Enter city name", value="Budapest").capitalize()

st.header(f"Current weather in {city}")

weather = get_current_weather(city, "metric", "en")

if weather:

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

weather_forecast = get_weather_forecast(city, "metric", "en")

if weather_forecast:
    if 'list' in weather_forecast:
        
        fc_data = weather_forecast['list']       
        
        forecast_list = []

        for item in fc_data:
            forecast_list.append({
                'datetime': item['dt_txt'],
                'temperature': item['main']['temp'],
                'humidity': item['main']['humidity'],
                'wind_speed': item['wind']['speed'],
                'weather_description': item['weather'][0]['description'].capitalize(),
                'icon': item['weather'][0]['icon']
            })

        df = pd.DataFrame(forecast_list)
        
        df['datetime'] = pd.to_datetime(df['datetime'])
        df['date'] = df['datetime'].dt.date
        df['hour'] = df['datetime'].dt.hour
        
        df = df[df['hour'].isin([6, 18])]
        df = df.reset_index(drop=True)
        df['h_label'] = df['datetime'].dt.strftime('%b %d, %I %p')
                
        st.header(f"Temperature trends (next 5 days)")
        
        fig = px.line(
            df,
            x='h_label',
            y='temperature',
            title='Temperature Forecast (°C)',
            labels={'h_label': 'Date and Hour', 'temperature': 'Temperature (°C)'},
            markers=True
        )

        st.plotly_chart(fig, use_container_width=True)
        
        df = df.rename(columns={
            'datetime': 'Date & Time',
            'h_label': 'Label',
            'temperature': 'Temperature (°C)',
            'humidity': 'Humidity (%)',
            'wind_speed': 'Wind Speed (m/s)',
            'weather_description': 'Weather'
        })

        with st.expander("See detailed forecast"):
            st.dataframe(
                df[['Label', 'Temperature (°C)', 'Humidity (%)', 'Wind Speed (m/s)', 'Weather']],
                hide_index=True
            )

    else:
        st.error("No forecast data available")

