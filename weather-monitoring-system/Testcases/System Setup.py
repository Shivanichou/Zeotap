import unittest
import requests

API_KEY = '484b2b352eae133bc2d7abced19a421c'  # Replace with your valid or invalid key for testing
CITIES = ['Delhi', 'Mumbai', 'Chennai', 'Bangalore', 'Kolkata', 'Hyderabad']

class TestWeatherSystemStartup(unittest.TestCase):

    def test_api_connection(self):
        """
        Test if the system connects to the OpenWeatherMap API successfully with a valid API key.
        If an invalid API key is provided, print an appropriate message.
        """
        city = CITIES[0]  # Test with the first city, e.g., 'Delhi'
        url = f'http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}'
        response = requests.get(url)

        if response.status_code == 401:
            print("Invalid API key provided.")
        else:
            # Verify that the response status code is 200 (OK)
            self.assertEqual(response.status_code, 200, "Failed to connect to OpenWeatherMap API")

            # Verify that the API key is valid by checking that the response contains weather data
            data = response.json()
            self.assertIn('main', data, "API response does not contain weather data (check API key validity)")

            # Print a success message if the API key is valid and weather data is retrieved
            print("API connection successful, weather data retrieved.")

if __name__ == '__main__':
    unittest.main()
