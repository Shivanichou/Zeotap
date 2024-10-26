import unittest
from unittest.mock import patch
from code_without_streamlit_logic import CITY_THRESHOLDS, check_thresholds, store_alert

class TestWeatherThresholdAlerts(unittest.TestCase):

    @patch('code_without_streamlit_logic.store_alert')
    def test_temperature_breaching_threshold(self, mock_store_alert):
        """
        Test that alerts are triggered when the temperature exceeds the threshold.
        """
        # Simulate weather data where temperature exceeds the threshold for Delhi (threshold is 35°C)
        city = 'Delhi'
        current_temp = 37.0  # Exceeds the threshold for Delhi (35°C)

        # Call the function to check if an alert is triggered
        check_thresholds(city, current_temp)

        # Verify that the alert was triggered and stored
        mock_store_alert.assert_called_once_with(city, current_temp)
        print(f"Alert Test Passed: Alert triggered for {city} when temperature exceeded {CITY_THRESHOLDS[city]}°C.")

    @patch('code_without_streamlit_logic.store_alert')
    def test_temperature_not_breaching_threshold(self, mock_store_alert):
        """
        Test that no alerts are triggered when the temperature is below the threshold.
        """
        # Simulate weather data where temperature does not exceed the threshold for Mumbai (threshold is 34°C)
        city = 'Mumbai'
        current_temp = 32.0  # Below the threshold for Mumbai (34°C)

        # Call the function to check if an alert is triggered
        check_thresholds(city, current_temp)

        # Verify that no alert was triggered
        mock_store_alert.assert_not_called()
        print(f"No Alert Test Passed: No alert triggered for {city} when temperature was below {CITY_THRESHOLDS[city]}°C.")

    @patch('code_without_streamlit_logic.store_alert')
    def test_temperature_at_threshold(self, mock_store_alert):
        """
        Test that no alerts are triggered when the temperature is exactly at the threshold.
        """
        # Simulate weather data where temperature is exactly at the threshold for Bangalore (threshold is 33°C)
        city = 'Bangalore'
        current_temp = 33.0  # Exactly at the threshold for Bangalore

        # Call the function to check if an alert is triggered
        check_thresholds(city, current_temp)

        # Verify that no alert was triggered
        mock_store_alert.assert_not_called()
        print(f"Threshold Test Passed: No alert triggered for {city} when temperature was exactly {CITY_THRESHOLDS[city]}°C.")

if __name__ == '__main__':
    unittest.main()
