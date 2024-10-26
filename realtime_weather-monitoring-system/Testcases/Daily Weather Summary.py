import unittest
from code_without_streamlit_logic import summarize_forecast_data

# Utility function to convert Kelvin to Celsius
def kelvin_to_celsius(temp_kelvin):
    return temp_kelvin - 273.15

class TestWeatherSummary(unittest.TestCase):

    def test_daily_summary(self):
        """
        Test daily summary calculation for weather data over multiple entries.
        """
        # Simulated weather forecast data for a day (multiple temperature entries and weather conditions)
        forecast_data_day_1 = [
            {'timestamp': '2024-10-22 00:00:00', 'temp': 300.0, 'feels_like': 303.15, 'humidity': 65, 'wind_speed': 3.5, 'weather_condition': 'Clear'},  # 26.85°C
            {'timestamp': '2024-10-22 06:00:00', 'temp': 303.15, 'feels_like': 305.15, 'humidity': 60, 'wind_speed': 4.0, 'weather_condition': 'Clouds'},  # 30°C
            {'timestamp': '2024-10-22 12:00:00', 'temp': 305.15, 'feels_like': 307.15, 'humidity': 55, 'wind_speed': 3.0, 'weather_condition': 'Clear'},  # 32°C
            {'timestamp': '2024-10-22 18:00:00', 'temp': 302.15, 'feels_like': 304.15, 'humidity': 60, 'wind_speed': 3.2, 'weather_condition': 'Clear'}  # 29°C
        ]

        # Expected daily summary in Celsius
        expected_summary_day_1 = {
            'avg_temp': (26.85 + 30 + 32 + 29) / 4,  # Average temperature in Celsius
            'max_temp': 32.0,  # Maximum temperature in Celsius
            'min_temp': 26.85,  # Minimum temperature in Celsius
            'dominant_condition': 'Clear'  # Dominant weather condition
        }

        # Calculate the summary using the summarize_forecast_data function
        daily_summaries = summarize_forecast_data(forecast_data_day_1)
        actual_summary_day_1 = daily_summaries['2024-10-22']  # Get the summary for the specific day

        # Convert the temperatures from Kelvin to Celsius for comparison
        actual_temps_celsius = [kelvin_to_celsius(temp) for temp in actual_summary_day_1['temps']]

        # Assertions to check if the summary is calculated correctly
        self.assertAlmostEqual(sum(actual_temps_celsius) / len(actual_temps_celsius), expected_summary_day_1['avg_temp'], places=2,
                               msg="Average temperature calculation is incorrect.")
        self.assertAlmostEqual(max(actual_temps_celsius), expected_summary_day_1['max_temp'], places=2,
                               msg="Maximum temperature calculation is incorrect.")
        self.assertAlmostEqual(min(actual_temps_celsius), expected_summary_day_1['min_temp'], places=2,
                               msg="Minimum temperature calculation is incorrect.")
        self.assertEqual(max(set(actual_summary_day_1['weather_conditions']), key=actual_summary_day_1['weather_conditions'].count), expected_summary_day_1['dominant_condition'],
                         msg="Dominant weather condition calculation is incorrect.")

        print(f"Daily Summary Test Passed: {actual_summary_day_1}")

    def test_multiple_days_summary(self):
        """
        Test daily summaries over multiple days of simulated weather data.
        """
        # Simulated weather forecast data for 3 days
        forecast_data_day_2 = [
            {'timestamp': '2024-10-23 00:00:00', 'temp': 295.15, 'feels_like': 298.15, 'humidity': 70, 'wind_speed': 2.0, 'weather_condition': 'Rain'},  # 22°C
            {'timestamp': '2024-10-23 06:00:00', 'temp': 296.15, 'feels_like': 299.15, 'humidity': 72, 'wind_speed': 2.5, 'weather_condition': 'Rain'},  # 23°C
            {'timestamp': '2024-10-23 12:00:00', 'temp': 297.15, 'feels_like': 300.15, 'humidity': 68, 'wind_speed': 3.0, 'weather_condition': 'Rain'},  # 24°C
            {'timestamp': '2024-10-23 18:00:00', 'temp': 299.15, 'feels_like': 302.15, 'humidity': 65, 'wind_speed': 3.2, 'weather_condition': 'Clouds'}  # 26°C
        ]

        forecast_data_day_3 = [
            {'timestamp': '2024-10-24 00:00:00', 'temp': 310.15, 'feels_like': 313.15, 'humidity': 50, 'wind_speed': 5.0, 'weather_condition': 'Clear'},  # 37°C
            {'timestamp': '2024-10-24 06:00:00', 'temp': 308.15, 'feels_like': 311.15, 'humidity': 55, 'wind_speed': 4.5, 'weather_condition': 'Clouds'},  # 35°C
            {'timestamp': '2024-10-24 12:00:00', 'temp': 311.15, 'feels_like': 314.15, 'humidity': 48, 'wind_speed': 5.2, 'weather_condition': 'Clear'},  # 38°C
            {'timestamp': '2024-10-24 18:00:00', 'temp': 307.15, 'feels_like': 310.15, 'humidity': 60, 'wind_speed': 4.8, 'weather_condition': 'Clear'}  # 34°C
        ]

        # Expected summaries for each day in Celsius
        expected_summary_day_2 = {
            'avg_temp': (22 + 23 + 24 + 26) / 4,
            'max_temp': 26.0,
            'min_temp': 22.0,
            'dominant_condition': 'Rain'
        }

        expected_summary_day_3 = {
            'avg_temp': (37 + 35 + 38 + 34) / 4,
            'max_temp': 38.0,
            'min_temp': 34.0,
            'dominant_condition': 'Clear'
        }

        # Calculate summaries using the summarize_forecast_data function
        daily_summaries_day_2 = summarize_forecast_data(forecast_data_day_2)
        daily_summaries_day_3 = summarize_forecast_data(forecast_data_day_3)

        actual_summary_day_2 = daily_summaries_day_2['2024-10-23']
        actual_summary_day_3 = daily_summaries_day_3['2024-10-24']

        # Convert the temperatures from Kelvin to Celsius for comparison
        actual_temps_day_2_celsius = [kelvin_to_celsius(temp) for temp in actual_summary_day_2['temps']]
        actual_temps_day_3_celsius = [kelvin_to_celsius(temp) for temp in actual_summary_day_3['temps']]

        # Assertions for day 2
        self.assertAlmostEqual(sum(actual_temps_day_2_celsius) / len(actual_temps_day_2_celsius), expected_summary_day_2['avg_temp'], places=2)
        self.assertEqual(max(actual_temps_day_2_celsius), expected_summary_day_2['max_temp'])
        self.assertEqual(min(actual_temps_day_2_celsius), expected_summary_day_2['min_temp'])
        self.assertEqual(max(set(actual_summary_day_2['weather_conditions']), key=actual_summary_day_2['weather_conditions'].count), expected_summary_day_2['dominant_condition'])

        # Assertions for day 3
        self.assertAlmostEqual(sum(actual_temps_day_3_celsius) / len(actual_temps_day_3_celsius), expected_summary_day_3['avg_temp'], places=2)
        self.assertEqual(max(actual_temps_day_3_celsius), expected_summary_day_3['max_temp'])
        self.assertEqual(min(actual_temps_day_3_celsius), expected_summary_day_3['min_temp'])
        self.assertEqual(max(set(actual_summary_day_3['weather_conditions']), key=actual_summary_day_3['weather_conditions'].count), expected_summary_day_3['dominant_condition'])

        print(f"Multiple Days Summary Test Passed for Day 2: {actual_summary_day_2}")
        print(f"Multiple Days Summary Test Passed for Day 3: {actual_summary_day_3}")

if __name__ == '__main__':
    unittest.main()
