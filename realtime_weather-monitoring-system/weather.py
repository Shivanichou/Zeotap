import streamlit as st
import requests
import mysql.connector
import time
import matplotlib.pyplot as plt
from datetime import datetime, timezone
from mysql.connector import pooling
import plotly.graph_objects as go
from datetime import datetime, timedelta
from streamlit_autorefresh import st_autorefresh





# OpenWeatherMap API Key and URL
DEFAULT_API_KEY = '484b2b352eae133bc2d7abced19a421c'
CITIES = ['Delhi', 'Mumbai', 'Chennai', 'Bangalore', 'Kolkata', 'Hyderabad']


# Initialize the session state for API key if not already set
if "api_key" not in st.session_state:
    st.session_state.api_key = DEFAULT_API_KEY

if "last_run_time" not in st.session_state:
    st.session_state.last_run_time = datetime.now() - timedelta(minutes=1)
    # Initialize to 2 minutes in the past

if "alert_times" not in st.session_state:
    st.session_state.alert_times = {}


# Function to validate API Key by making a test request
def validate_api_key(api_key):
    test_city = 'Delhi'
    url = f'http://api.openweathermap.org/data/2.5/weather?q={test_city}&appid={api_key}'
    response = requests.get(url)
    if response.status_code == 401:  # Unauthorized or invalid API key
        return False
    return True

dbconfig = {
    "host": "mysql",
    "user": "root",
    "password": "9961",
    "database": "weather_data"
}
pool = pooling.MySQLConnectionPool(pool_name="mypool", pool_size=5, **dbconfig)

if "city_thresholds" not in st.session_state:
    st.session_state.city_thresholds = {city: 35 for city in CITIES}

def get_connection():
    try:
        connection = pool.get_connection()
        return connection
    except mysql.connector.Error as err:
        st.error(f"Error: {err}")
        return None

# Convert Kelvin to Celsius
def kelvin_to_celsius(temp_kelvin):
    return temp_kelvin - 273.15

# Fetch weather data from OpenWeatherMap API
def fetch_weather_data(city):
    url = f'http://api.openweathermap.org/data/2.5/weather?q={city}&appid={st.session_state.api_key}'
    try:
        response = requests.get(url, timeout=10)  # 10 seconds timeout
        if response.status_code != 200:
            st.error(f"Failed to retrieve weather data for {city}. Status code: {response.status_code}")
            return None, None, None, None, None
        data = response.json()
        if 'main' in data and 'wind' in data:
            temp = kelvin_to_celsius(data['main']['temp'])
            feels_like = kelvin_to_celsius(data['main']['feels_like'])
            humidity = data['main']['humidity']
            wind_speed = data['wind']['speed']
            weather_condition = data['weather'][0]['main']
            timestamp = datetime.fromtimestamp(data['dt'], tz=timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
            return temp, feels_like, humidity, wind_speed, weather_condition
        else:
            st.error(f"Failed to retrieve valid data for {city}. Response: {data}")
            return None, None, None, None, None
    except requests.exceptions.Timeout:
        st.error(f"Request to OpenWeatherMap API timed out for {city}.")
        return None, None, None, None, None

# Fetch weather forecast data from OpenWeatherMap API
def fetch_weather_forecast(city):
    url = f'http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={st.session_state.api_key}'
    try:
        response = requests.get(url)
        if response.status_code != 200:
            st.error(f"Failed to retrieve forecast data for {city}. Status code: {response.status_code}")
            return []
        data = response.json()
        if 'list' in data:
            forecast_data = [
                {
                    'timestamp': datetime.fromtimestamp(entry['dt'], tz=timezone.utc).strftime('%Y-%m-%d %H:%M:%S'),
                    'temp': kelvin_to_celsius(entry['main']['temp']),
                    'feels_like': kelvin_to_celsius(entry['main']['feels_like']),
                    'humidity': entry['main']['humidity'],
                    'wind_speed': entry['wind']['speed'],
                    'weather_condition': entry['weather'][0]['main']
                }
                for entry in data['list']
            ]
            return forecast_data
        else:
            st.error(f"Failed to retrieve valid forecast data for {city}.")
            return []
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching forecast data: {e}")
        return []


# Summarize forecast data
def summarize_forecast_data(forecast_data):
    daily_summaries = {}
    for entry in forecast_data:
        day = entry['timestamp'].split(' ')[0]
        daily_summaries.setdefault(day, {'temps': [], 'feels_like': [], 'humidities': [], 'wind_speeds': [], 'weather_conditions': []})
        daily_summaries[day]['temps'].append(entry['temp'])
        daily_summaries[day]['feels_like'].append(entry['feels_like'])
        daily_summaries[day]['humidities'].append(entry['humidity'])
        daily_summaries[day]['wind_speeds'].append(entry['wind_speed'])
        daily_summaries[day]['weather_conditions'].append(entry['weather_condition'])
    return daily_summaries

# Print summarized forecast data
def print_forecast_summaries(city, daily_summaries):
    for day, data in daily_summaries.items():
        avg_temp = sum(data['temps']) / len(data['temps'])
        avg_feels_like = sum(data['feels_like']) / len(data['feels_like'])
        avg_humidity = sum(data['humidities']) / len(data['humidities'])
        avg_wind_speed = sum(data['wind_speeds']) / len(data['wind_speeds'])
        dominant_condition = max(set(data['weather_conditions']), key=data['weather_conditions'].count)
        st.write(
            f"**{city} - {day}:**\n"
            f"Avg Temp: {avg_temp:.1f}°C, Feels Like: {avg_feels_like:.1f}°C\n"
            f"Humidity: {avg_humidity:.0f}%, Wind Speed: {avg_wind_speed:.1f} m/s\n"
            f"Condition: {dominant_condition}\n"
        )


# Store weather data in the database
def store_in_database(query, data):
    connection = get_connection()
    if connection is None:
        st.error("Failed to connect to the database.")
        return
    try:
        cursor = connection.cursor()
        cursor.executemany(query, data)
        connection.commit()
    except mysql.connector.Error as err:
        st.error(f"Database error: {err}")
        connection.rollback()
    finally:
        cursor.close()
        connection.close()


# Store daily summary in the database
def get_daily_summary_data(city, date):
    connection = get_connection()
    cursor = connection.cursor()
    try:
        cursor.execute('''SELECT avg_temp, max_temp, min_temp, avg_feels_like, avg_humidity, avg_wind_speed 
                          FROM daily_summary 
                          WHERE city=%s AND date=%s''', (city, date))

        # Ensure all data is fetched to avoid 'unread result' error
        data = cursor.fetchone()
        if data is None:
            print(f"No data found for {city} on {date}")
        return data
    except mysql.connector.Error as err:
        print(f"Error fetching daily summary: {err}")
        return None
    finally:
        if cursor.with_rows:  # Check if there are unread results and clear them
            cursor.fetchall()
        cursor.close()
        connection.close()

# Store weather forecast in the database
def store_daily_summary(city, date, avg_temp, max_temp, min_temp, dominant_condition, avg_feels_like, avg_humidity, avg_wind_speed):
    query = '''INSERT INTO daily_summary 
               (city, avg_temp, max_temp, min_temp, dominant_condition, date, avg_feels_like, avg_humidity, avg_wind_speed) 
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)'''

    # Handle None values
    if avg_temp is None: avg_temp = 0
    if max_temp is None: max_temp = 0
    if min_temp is None: min_temp = 0
    if dominant_condition is None: dominant_condition = 'Unknown'
    if avg_feels_like is None: avg_feels_like = 0
    if avg_humidity is None: avg_humidity = 0
    if avg_wind_speed is None: avg_wind_speed = 0

    data = (city, avg_temp, max_temp, min_temp, dominant_condition, date, avg_feels_like, avg_humidity, avg_wind_speed)

    connection = get_connection()
    if connection is None:
        st.error("Failed to connect to the database.")
        return

    try:
        cursor = connection.cursor()
        cursor.execute(query, data)
        connection.commit()
        #st.success(f"Successfully inserted daily summary for {city} on {date}")
    except mysql.connector.Error as err:
        st.error(f"Database error while inserting daily summary: {err}")
        connection.rollback()
    finally:
        cursor.close()
        connection.close()


def store_weather_forecast(city, forecast_data):
    query = '''
        INSERT INTO forecasts (city, timestamp, temp, feels_like, humidity, wind_speed, weather_condition) 
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    '''

    # Log forecast data before insertion for debugging
    #st.write(f"Storing forecast data for {city}: {forecast_data}")  # Debugging output

    # Prepare the data for database insertion
    data = [(city, entry['timestamp'], entry['temp'], entry['feels_like'], entry['humidity'],
             entry['wind_speed'], entry['weather_condition']) for entry in forecast_data]

    # Log the data to be inserted
    #st.write(f"Data to be inserted into the database: {data}")  # Debugging output

    store_in_database(query, data)  # Insert into the database


# Store triggered alert in the database
def store_alert(city, temp):
    query = '''INSERT INTO alerts (city, temp, timestamp) VALUES (%s, %s, %s)'''
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    data = [(city, temp, timestamp)]

    # Log the data to be inserted for debugging
    #st.write(f"Inserting alert into database: {data}")  # Debugging output

    store_in_database(query, data)  # Insert into database


# Check if temperature exceeds the city-specific threshold
import time


# Function to check if thresholds are breached and handle alerts
def check_thresholds(city, current_temp):
    # Use the dynamic threshold from session state, default to 35°C if not set
    threshold = st.session_state.city_thresholds.get(city, 35)

    # Check if the current temperature exceeds the threshold
    if current_temp > threshold:
        store_alert(city, current_temp)
        # Trigger alert and store the alert time for the city if not already triggered
        if city not in st.session_state.alert_times:
            st.session_state.alert_times[city] = datetime.now()

        # Calculate the duration from the alert trigger time
        alert_duration = datetime.now() - st.session_state.alert_times[city]

        # Display the alert if within the 1-minute window
        if alert_duration <= timedelta(minutes=1):
            with st.sidebar:
                st.warning(f"ALERT TRIGGERED for {city}: {current_temp:.1f}°C exceeds the threshold of {threshold}°C")
        else:
            # Remove the alert after 1 minute
            del st.session_state.alert_times[city]
    else:
        # If temperature is within threshold, clear any existing alert for the city
        if city in st.session_state.alert_times:
            del st.session_state.alert_times[city]

# Process real-time weather data
def process_weather_data():
    st.write("Processing real-time weather data...")  # Added logging
    for city in CITIES:
        temp, feels_like, humidity, wind_speed, weather_condition = fetch_weather_data(city)
        if temp is None:
            st.error(f"Skipping {city} due to failed data retrieval.")
            continue
        check_thresholds(city, temp)
        #st.write(f"Collected data for {city}: Temp={temp}, Feels Like={feels_like}")  # Added logging

        # Example: Storing daily summary with fetched data (you might want to compute these values over time)
        store_daily_summary(
            city=city,
            date=datetime.now().strftime('%Y-%m-%d'),  # Store current date
            avg_temp=temp,
            max_temp=temp,  # Example, replace with actual max logic
            min_temp=temp,  # Example, replace with actual min logic
            dominant_condition=weather_condition,
            avg_feels_like=feels_like,
            avg_humidity=humidity,
            avg_wind_speed=wind_speed
        )

# Process forecast data for all cities
def process_forecast_data():
    for city in CITIES:
        forecast_data = fetch_weather_forecast(city)
        if forecast_data:
            store_weather_forecast(city, forecast_data)
            daily_summaries = summarize_forecast_data(forecast_data)
            print_forecast_summaries(city, daily_summaries)

# Get temperature trends data
def get_temperature_trends_data(city):
    connection = get_connection()
    cursor = connection.cursor()
    try:
        cursor.execute('''SELECT date, avg_temp 
                          FROM daily_summary 
                          WHERE city=%s 
                          ORDER BY date DESC 
                          LIMIT 7''', (city,))
        data = cursor.fetchall()
        return data
    except mysql.connector.Error as err:
        st.error(f"Error fetching temperature trends: {err}")
        return None
    finally:
        cursor.fetchall()  # Ensure all results are fetched
        cursor.close()
        connection.close()

# Get triggered alerts data
def get_triggered_alerts_data(city):
    connection = get_connection()
    cursor = connection.cursor()
    try:
        cursor.execute('''SELECT temp, timestamp 
                          FROM alerts 
                          WHERE city=%s 
                          ORDER BY timestamp DESC''', (city,))
        data = cursor.fetchall()
        return data
    except mysql.connector.Error as err:
        st.error(f"Error fetching triggered alerts: {err}")
        return None
    finally:
        cursor.fetchall()  # Ensure all results are fetched
        cursor.close()
        connection.close()

# Get forecast summary data
def get_forecast_summary_data(city, date):
    connection = get_connection()
    cursor = connection.cursor()
    try:
        cursor.execute('''SELECT avg(temp), avg(feels_like), avg(humidity), avg(wind_speed), MAX(weather_condition) 
                          FROM forecasts 
                          WHERE city=%s AND DATE(timestamp)=%s 
                          GROUP BY DATE(timestamp)''', (city, date))
        data = cursor.fetchone()
        return data
    except mysql.connector.Error as err:
        st.error(f"Error fetching forecast summary: {err}")
        return None
    finally:
        cursor.fetchall()  # Ensure all results are fetched
        cursor.close()
        connection.close()

# Plot functions
def plot_daily_summary(city, date):
    data = get_daily_summary_data(city, date)
    if data:
        avg_temp, max_temp, min_temp, avg_feels_like, avg_humidity, avg_wind_speed = data
        labels = ['Avg Temp', 'Max Temp', 'Min Temp', 'Avg Feels Like', 'Avg Humidity', 'Avg Wind Speed']
        values = [avg_temp or 0, max_temp or 0, min_temp or 0, avg_feels_like or 0, avg_humidity or 0, avg_wind_speed or 0]
        plt.bar(labels, values, color=['blue', 'red', 'green', 'orange', 'purple', 'brown'])
        plt.xlabel('Parameter')
        plt.ylabel('Value')
        plt.title(f'Daily Weather Summary for {city} on {date}')
        st.pyplot(plt)
        plt.clf()
    else:
        st.write("No data available for this city and date.")

def plot_temperature_trends(city):
    data = get_temperature_trends_data(city)
    if data:
        dates, avg_temps = zip(*data)
        fig = go.Figure([go.Scatter(x=dates, y=avg_temps, mode='lines+markers')])
        fig.update_layout(
            title=f"Temperature Trends for {city} (Last 7 Days)",
            xaxis_title="Date",
            yaxis_title="Average Temperature (°C)",
            xaxis=dict(tickangle=-45)
        )
        st.plotly_chart(fig)
    else:
        st.write("No temperature trend data available for this city.")

def plot_triggered_alerts(city):
    data = get_triggered_alerts_data(city)
    if data:
        temps, timestamps = zip(*data)
        plt.plot(timestamps, temps, marker='x', linestyle='-', color='red')
        plt.xlabel('Timestamp')
        plt.ylabel('Temperature (°C)')
        plt.title(f'Triggered Alerts for {city}')
        plt.xticks(rotation=45)
        st.pyplot(plt)
        plt.clf()
    else:
        st.write("No triggered alerts data available for this city.")

def plot_forecast_summary(city, date):
    data = get_forecast_summary_data(city, date)
    if data:
        avg_temp, avg_feels_like, avg_humidity, avg_wind_speed, weather_condition = data
        fig = go.Figure([go.Bar(
            x=['Avg Temp', 'Avg Feels Like', 'Avg Humidity', 'Avg Wind Speed'],
            y=[avg_temp, avg_feels_like, avg_humidity, avg_wind_speed]
        )])
        fig.update_layout(
            title=f"Forecast Summary for {city} on {date}",
            xaxis_title="Parameter",
            yaxis_title="Value"
        )
        st.plotly_chart(fig)
    else:
        st.write("Please collect the forecast data by clicking the 'Collect Forecast' button.")

# Create a Folium map centered on India

# Scheduler for automated data collection
def should_run():
    now = datetime.now()
    if now - st.session_state.last_run_time > timedelta(minutes=1):
        st.session_state.last_run_time = now  # Update the last run time
        return True
    return False

# Main Streamlit UI

# Title
st.title("Weather Monitoring Dashboard")

st.info("Scheduler will automatically run every 1 minute to process weather data.")

# Automatically process data if 2 minutes have passed
if should_run():
    process_weather_data()

st.header("Available Cities for Weather Forecast")

# Display the available cities clearly using st.info
available_cities_str = ', '.join(CITIES)  # Create a string of available cities
st.info(f"Cities: {available_cities_str}")  # Display available cities as info

# Section: Real-time Data Collection
st.header("Real-time Weather Data")
if st.button("Show Real-time Weather Data"):
    st.write("Processing real-time weather data...")  # Show the processing message
    collected_data = []  # Store the data to be displayed later

    # Loop through all the cities and fetch weather data
    for city in CITIES:
        temp, feels_like, humidity, wind_speed, weather_condition = fetch_weather_data(city)
        if temp is not None:
            # If data is successfully fetched, store it in the list
            collected_data.append((city, temp, feels_like, humidity, wind_speed, weather_condition))

    # Now display the collected data after the processing message
    if collected_data:
        # Loop through the collected data and display each city's weather data
        for data in collected_data:
            city, temp, feels_like, humidity, wind_speed, weather_condition = data
            st.write(f"**{city}:**\n"
                     f"Temperature: {temp:.1f}°C\n"
                     f"Feels Like: {feels_like:.1f}°C\n"
                     f"Humidity: {humidity}%\n"
                     f"Wind Speed: {wind_speed} m/s\n"
                     f"Condition: {weather_condition}")
    else:
        st.error("No data was retrieved.")

# Section: Forecast Data Collection
st.header("Weather Forecast Data")
city = st.selectbox("Select City", CITIES)
if st.button(f"Collect Forecast Data for {city}"):
    forecast_data = fetch_weather_forecast(city)  # Fetch forecast data for selected city
    if forecast_data:
        store_weather_forecast(city, forecast_data)  # Store forecast data in database
        daily_summaries = summarize_forecast_data(forecast_data)  # Summarize forecast data
        print_forecast_summaries(city, daily_summaries)  # Display forecast summaries

# Section: Visualization
# Section: Visualization
st.header("Weather Data Visualization")

# Provide city selection for the visualization section
city_for_visualization = st.selectbox("Select City for Visualization", CITIES)

plot_type = st.selectbox("Select Plot Type", ["Daily Summary", "Temperature Trends", "Triggered Alerts", "Forecast Summary"])

if plot_type == "Daily Summary":
    date = st.date_input("Select Date", datetime.now())
    if st.button("Plot Daily Summary"):
        plot_daily_summary(city_for_visualization, str(date))

elif plot_type == "Temperature Trends":
    if st.button("Plot Temperature Trends"):
        plot_temperature_trends(city_for_visualization)

elif plot_type == "Triggered Alerts":
    if st.button("Plot Triggered Alerts"):
        plot_triggered_alerts(city_for_visualization)

elif plot_type == "Forecast Summary":
    date = st.date_input("Select Date", datetime.now())
    if st.button("Plot Forecast Summary"):
        plot_forecast_summary(city_for_visualization, str(date))


# Sidebar for API key input with validation
# Sidebar for API key input with validation
# Sidebar for API key input with validation
with st.sidebar:
    new_api_key = st.text_input(
        "Enter OpenWeatherMap API Key",
        value=st.session_state.api_key,  # Populate with existing session state API key
        key="api_key_input"  # Temporary key for the input field
    )

    # Button to validate the API key and update session state
    if st.button("Validate API Key"):
        if validate_api_key(new_api_key):
            st.success("API Key is valid!")
            st.session_state.api_key = new_api_key  # Update session state
        else:
            st.error("Invalid API Key. Please enter a valid key.")


# Dynamic threshold inputs for each city
with st.sidebar:

    st.write("")
    st.write("")
    st.header("Set City-Specific Temperature Threshold")
    selected_city = st.selectbox("Select a City", CITIES)

    # Number input for the selected city's threshold
    st.session_state.city_thresholds[selected_city] = st.number_input(
        f"Threshold for {selected_city} (°C)",
        value=st.session_state.city_thresholds.get(selected_city, 35),  # Default to 35°C
        step=1,  # Step size of 1 degree
        key=f"threshold_{selected_city}"  # Unique key for each input field
    )

    # Display updated city thresholds
    st.write(f"**current Threshold for {selected_city}:** {st.session_state.city_thresholds[selected_city]}°C")



st.write(f"Last checked: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
st_autorefresh(interval=60 * 1000, key="data_refresh")



