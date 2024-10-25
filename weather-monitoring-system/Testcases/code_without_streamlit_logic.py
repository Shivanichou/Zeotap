import requests
import schedule
import mysql.connector
import time
import matplotlib.pyplot as plt
from datetime import datetime, timezone

# OpenWeatherMap API Key and URL
API_KEY = '484b2b352eae133bc2d7abced19a421c'
CITIES = ['Delhi', 'Mumbai', 'Chennai', 'Bangalore', 'Kolkata', 'Hyderabad']

# City-wise threshold for temperature alerts (in Celsius)
CITY_THRESHOLDS = {
    'Delhi': 35,
    'Mumbai': 34,
    'Chennai': 36,
    'Bangalore': 33,
    'Kolkata': 35,
    'Hyderabad': 34
}


# MySQL Database connection
def connect_to_database():
    try:
        connection = mysql.connector.connect(
            host='mysql',
            user='root',
            password='9961',
            database='weather_data'
        )
        return connection
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None


# Convert Kelvin to Celsius
def kelvin_to_celsius(temp_kelvin):
    return temp_kelvin - 273.15


# Fetch weather data from OpenWeatherMap API
def fetch_weather_data(city):
    url = f'http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}'
    response = requests.get(url).json()

    if 'main' in response and 'wind' in response:
        temp = kelvin_to_celsius(response['main']['temp'])
        feels_like = kelvin_to_celsius(response['main']['feels_like'])
        humidity = response['main']['humidity']
        wind_speed = response['wind']['speed']
        weather_condition = response['weather'][0]['main']
        timestamp = datetime.fromtimestamp(response['dt'], tz=timezone.utc).strftime('%Y-%m-%d %H:%M:%S')

        print(
            f"City: {city}, Temp: {temp:.2f}°C, Feels Like: {feels_like:.2f}°C, "
            f"Humidity: {humidity}%, Wind Speed: {wind_speed} m/s, Condition: {weather_condition}, Time: {timestamp}"
        )
        return temp, feels_like, humidity, wind_speed, weather_condition
    else:
        print(f"Failed to retrieve weather data for {city}. API response: {response}")
        return None, None, None, None, None


# Fetch weather forecast data from OpenWeatherMap API
def fetch_weather_forecast(city):
    url = f'http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={API_KEY}'
    response = requests.get(url).json()

    if 'list' in response:
        forecast_data = [
            {
                'timestamp': datetime.fromtimestamp(entry['dt'], tz=timezone.utc).strftime('%Y-%m-%d %H:%M:%S'),
                'temp': kelvin_to_celsius(entry['main']['temp']),
                'feels_like': kelvin_to_celsius(entry['main']['feels_like']),
                'humidity': entry['main']['humidity'],
                'wind_speed': entry['wind']['speed'],
                'weather_condition': entry['weather'][0]['main']
            }
            for entry in response['list']
        ]
        return forecast_data
    else:
        print(f"Failed to retrieve forecast data for {city}. API response: {response}")
        return []


# Store weather data in the database
def store_in_database(query, data):
    connection = connect_to_database()
    if connection is None:
        print("Failed to connect to the database.")
        return

    try:
        cursor = connection.cursor()
        cursor.executemany(query, data)
        connection.commit()
    except mysql.connector.Error as err:
        print(f"Database error: {err}")
    finally:
        cursor.close()
        connection.close()

def store_daily_summary(city, date, avg_temp, max_temp, min_temp, dominant_condition, avg_feels_like, avg_humidity, avg_wind_speed):
    try:
        connection = connect_to_database()
        if connection is None:
            print("Failed to connect to the database, cannot store daily summary.")
            return
        cursor = connection.cursor()

        # Insert into daily_summary table
        cursor.execute('''INSERT INTO daily_summary 
                          (city, date, avg_temp, max_temp, min_temp, dominant_condition, avg_feels_like, avg_humidity, avg_wind_speed) 
                          VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)''',
                       (city, date, avg_temp, max_temp, min_temp, dominant_condition, avg_feels_like, avg_humidity, avg_wind_speed))

        connection.commit()  # Commit the transaction
        cursor.close()
        connection.close()
    except mysql.connector.Error as err:
        print(f"Error inserting daily summary data: {err}")


# Store weather forecast in the database
def store_weather_forecast(city, forecast_data):
    query = '''
        INSERT INTO forecasts (city, timestamp, temp, feels_like, humidity, wind_speed, weather_condition) 
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    '''
    data = [(city, entry['timestamp'], entry['temp'], entry['feels_like'], entry['humidity'],
             entry['wind_speed'], entry['weather_condition']) for entry in forecast_data]
    store_in_database(query, data)


# Store triggered alert in the database
def store_alert(city, temp):
    query = '''INSERT INTO alerts (city, temp, timestamp) VALUES (%s, %s, %s)'''
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    data = [(city, temp, timestamp)]
    store_in_database(query, data)


# Check if temperature exceeds the city-specific threshold
def check_thresholds(city, current_temp):
    threshold = CITY_THRESHOLDS.get(city, 35)
    if current_temp > threshold:
        print(f"ALERT! {city} temperature exceeds {threshold}°C: Current Temp: {current_temp:.2f}°C")
        store_alert(city, current_temp)


# Process real-time weather data
# Process real-time weather data and generate daily summary
def process_weather_data():
    daily_data = {}

    for city in CITIES:
        temp, feels_like, humidity, wind_speed, weather_condition = fetch_weather_data(city)
        if temp is None:
            continue

        if city not in daily_data:
            daily_data[city] = {'temps': [], 'feels_like': [], 'humidities': [], 'wind_speeds': [], 'weather_conditions': []}

        # Append data for the city
        daily_data[city]['temps'].append(temp)
        daily_data[city]['feels_like'].append(feels_like)
        daily_data[city]['humidities'].append(humidity)
        daily_data[city]['wind_speeds'].append(wind_speed)
        daily_data[city]['weather_conditions'].append(weather_condition)

        # Check if temperature exceeds thresholds
        check_thresholds(city, temp)

    # Now, calculate the daily summary and insert it into the database
    for city, data in daily_data.items():
        avg_temp = sum(data['temps']) / len(data['temps'])
        max_temp = max(data['temps'])
        min_temp = min(data['temps'])
        avg_feels_like = sum(data['feels_like']) / len(data['feels_like'])
        avg_humidity = sum(data['humidities']) / len(data['humidities'])
        avg_wind_speed = sum(data['wind_speeds']) / len(data['wind_speeds'])
        dominant_condition = max(set(data['weather_conditions']), key=data['weather_conditions'].count)

        # Insert the daily summary into the table
        date = datetime.now().strftime('%Y-%m-%d')
        store_daily_summary(city, date, avg_temp, max_temp, min_temp, dominant_condition, avg_feels_like, avg_humidity, avg_wind_speed)



# Process forecast data for all cities
def process_forecast_data():
    for city in CITIES:
        forecast_data = fetch_weather_forecast(city)
        if forecast_data:
            store_weather_forecast(city, forecast_data)
            daily_summaries = summarize_forecast_data(forecast_data)
            print(f"Forecast data for {city} has been stored.")
            print_forecast_summaries(city, daily_summaries)


# Generate daily summaries from forecast data
def summarize_forecast_data(forecast_data):
    daily_summaries = {}
    for entry in forecast_data:
        day = entry['timestamp'].split(' ')[0]
        daily_summaries.setdefault(day, {'temps': [], 'feels_like': [], 'humidities': [], 'wind_speeds': [],
                                         'weather_conditions': []})
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
        print(
            f"Forecast Summary for {city} on {day}: Avg Temp: {avg_temp:.2f}°C, "
            f"Avg Feels Like: {avg_feels_like:.2f}°C, Avg Humidity: {avg_humidity}%, "
            f"Avg Wind Speed: {avg_wind_speed} m/s, Dominant Condition: {dominant_condition}"
        )


# Visualization Functions (Daily Summary, Temperature Trends, Alerts)
# Get daily summary data
# Get daily summary data
def get_daily_summary_data(city, date):
    connection = connect_to_database()
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


# Get temperature trends data
def get_temperature_trends_data(city):
    connection = connect_to_database()
    cursor = connection.cursor()
    try:
        cursor.execute('''SELECT date, avg_temp 
                          FROM daily_summary 
                          WHERE city=%s 
                          ORDER BY date DESC 
                          LIMIT 7''', (city,))

        # Fetch all data
        data = cursor.fetchall()
        return data
    except mysql.connector.Error as err:
        print(f"Error fetching temperature trends: {err}")
        return None
    finally:
        if cursor.with_rows:  # Clear any remaining unread results
            cursor.fetchall()
        cursor.close()
        connection.close()


# Get triggered alerts data
def get_triggered_alerts_data(city):
    connection = connect_to_database()
    cursor = connection.cursor()
    try:
        cursor.execute('''SELECT temp, timestamp 
                          FROM alerts 
                          WHERE city=%s 
                          ORDER BY timestamp DESC''', (city,))

        # Fetch all data
        data = cursor.fetchall()
        return data
    except mysql.connector.Error as err:
        print(f"Error fetching triggered alerts: {err}")
        return None
    finally:
        if cursor.with_rows:  # Clear any remaining unread results
            cursor.fetchall()
        cursor.close()
        connection.close()


# Get forecast summary data
def get_forecast_summary_data(city, date):
    connection = connect_to_database()
    cursor = connection.cursor()
    try:
        cursor.execute('''SELECT avg(temp), avg(feels_like), avg(humidity), avg(wind_speed), MAX(weather_condition) 
                          FROM forecasts 
                          WHERE city=%s AND DATE(timestamp)=%s 
                          GROUP BY DATE(timestamp)''', (city, date))

        # Fetch data
        data = cursor.fetchone()
        return data
    except mysql.connector.Error as err:
        print(f"Error fetching forecast summary: {err}")
        return None
    finally:
        if cursor.with_rows:  # Clear any remaining unread results
            cursor.fetchall()
        cursor.close()
        connection.close()


# Plot functions
def plot_daily_summary(city, date):
    data = get_daily_summary_data(city, date)
    if data:
        avg_temp, max_temp, min_temp, avg_feels_like, avg_humidity, avg_wind_speed = data
        labels = ['Avg Temp', 'Max Temp', 'Min Temp', 'Avg Feels Like', 'Avg Humidity', 'Avg Wind Speed']
        values = [avg_temp or 0, max_temp or 0, min_temp or 0, avg_feels_like or 0, avg_humidity or 0,
                  avg_wind_speed or 0]
        plt.bar(labels, values, color=['blue', 'red', 'green', 'orange', 'purple', 'brown'])
        plt.xlabel('Parameter')
        plt.ylabel('Value')
        plt.title(f'Daily Weather Summary for {city} on {date}')
        plt.show()
    else:
        print(f"No summary data found for {city} on {date}")


def plot_temperature_trends(city):
    data = get_temperature_trends_data(city)
    if data:
        dates, avg_temps = zip(*data)
        plt.plot(dates, avg_temps, marker='o', linestyle='-', color='blue')
        plt.xlabel('Date')
        plt.ylabel('Average Temperature (°C)')
        plt.title(f'Average Temperature Trend for {city} (Last 7 Days)')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()
    else:
        print(f"No temperature trend data found for {city}.")


def plot_triggered_alerts(city):
    data = get_triggered_alerts_data(city)
    if data:
        temps, timestamps = zip(*data)
        plt.plot(timestamps, temps, marker='x', linestyle='-', color='red')
        plt.xlabel('Timestamp')
        plt.ylabel('Temperature (°C)')
        plt.title(f'Triggered Alerts for {city}')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()
    else:
        print(f"No alert data found for {city}.")


def plot_forecast_summary(city, date):
    data = get_forecast_summary_data(city, date)
    if data:
        avg_temp, avg_feels_like, avg_humidity, avg_wind_speed, weather_condition = data
        labels = ['Avg Temp', 'Avg Feels Like', 'Avg Humidity', 'Avg Wind Speed', 'Condition']
        values = [avg_temp or 0, avg_feels_like or 0, avg_humidity or 0, avg_wind_speed or 0,
                  0]  # 0 for non-numeric weather_condition
        plt.bar(labels, values, color=['blue', 'orange', 'green', 'red', 'purple'])
        plt.xlabel('Parameter')
        plt.ylabel('Value')
        plt.title(f'Forecast Summary for {city} on {date}')
        plt.show()
    else:
        print(f"No forecast summary data found for {city} on {date}")


# Scheduler
def start_scheduler():
    schedule.every(0.1).minutes.do(process_weather_data)
    #schedule.every(5).minutes.do(process_forecast_data)
    while True:
        schedule.run_pending()
        time.sleep(0.1)


# Menu and user input
def main():
    print("Available cities for forecasting:")
    for i, city in enumerate(CITIES, 1):
        print(f"{i}. {city}")

    city_choice = get_valid_choice("Enter the number corresponding to the city: ", len(CITIES))
    city = CITIES[city_choice - 1]

    print("Select the plot type:")
    print("1. Daily Summary")
    print("2. Historical Temperature Trends")
    print("3. Triggered Alerts")
    print("4. Forecast Summary")

    plot_choice = get_valid_choice("Enter the number of your choice: ", 4)

    if plot_choice == 1:
        date = input("Enter the date (YYYY-MM-DD) for daily summary: ")
        plot_daily_summary(city, date)
    elif plot_choice == 2:
        plot_temperature_trends(city)
    elif plot_choice == 3:
        plot_triggered_alerts(city)
    elif plot_choice == 4:
        date = input("Enter the date (YYYY-MM-DD) for forecast summary: ")
        plot_forecast_summary(city, date)


def get_valid_choice(prompt, max_choice):
    while True:
        choice = input(prompt)
        if choice.isdigit() and 1 <= int(choice) <= max_choice:
            return int(choice)
        print("Invalid input. Please try again.")


if __name__ == "__main__":
    user_choice = input("Enter '1' to start data collection \n\t '2' for forecast data \n\t '3'  for visualization: ")

    if user_choice == '1':
        process_weather_data()
        start_scheduler()
    elif user_choice == '2':
        process_forecast_data()
    elif user_choice == '3':
        main()
    else:
        print("Invalid choice. Exiting...")
