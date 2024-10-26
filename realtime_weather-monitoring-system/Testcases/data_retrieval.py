import unittest
from unittest.mock import patch, MagicMock
import time
from code_without_streamlit_logic import fetch_weather_data, process_weather_data, CITIES  # Ensure module name is correct

class TestWeatherDataWithIntervals(unittest.TestCase):

    @patch('code_without_streamlit_logic.requests.get')
    @patch('code_without_streamlit_logic.time.sleep', return_value=None)  # Mock time.sleep to avoid delays
    def test_simulated_api_calls_at_intervals(self, mock_sleep, mock_get):
        # Mock the API response with sample data for all cities
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'main': {
                'temp': 300.15,  # Kelvin (approximately 27°C)
                'feels_like': 303.15,  # Kelvin
                'humidity': 60
            },
            'wind': {
                'speed': 5.0  # m/s
            },
            'weather': [{
                'main': 'Clear'
            }],
            'dt': 1633096795  # Unix timestamp
        }
        mock_get.return_value = mock_response

        # Simulate calling process_weather_data() at intervals
        for _ in range(3):  # Simulate 3 interval-based API calls
            process_weather_data()  # Calls fetch_weather_data for each city in CITIES
            time.sleep(2)  # Simulate interval (mocked to skip actual delay)

        # Ensure that the mock_get (API call) was made 3 times for each city
        expected_call_count = 3 * len(CITIES)  # 3 intervals, one call per city each time
        self.assertEqual(mock_get.call_count, expected_call_count)

        # Ensure that the weather data was correctly retrieved and parsed for each city
        for city in CITIES:
            mock_get.assert_any_call(f'http://api.openweathermap.org/data/2.5/weather?q={city}&appid=484b2b352eae133bc2d7abced19a421c')

        # Test the data parsing correctness
        temp, feels_like, humidity, wind_speed, weather_condition = fetch_weather_data('Delhi')
        self.assertAlmostEqual(temp, 27.0, places=1)  # 300.15K -> 27°C
        self.assertAlmostEqual(feels_like, 30.0, places=1)
        self.assertEqual(humidity, 60)
        self.assertEqual(wind_speed, 5.0)
        self.assertEqual(weather_condition, 'Clear')

if __name__ == '__main__':
    unittest.main()
