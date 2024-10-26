import unittest
from code_without_streamlit_logic import kelvin_to_celsius  # Import the kelvin_to_celsius function from your main code


class TestTemperatureConversion(unittest.TestCase):

    def test_kelvin_to_celsius(self):
        """
        Test conversion of temperature from Kelvin to Celsius.
        """
        temp_kelvin = 300.0  # Example temperature in Kelvin
        expected_celsius = 26.85  # 300K is 26.85°C

        converted_temp = kelvin_to_celsius(temp_kelvin)

        self.assertAlmostEqual(converted_temp, expected_celsius, places=2,
                               msg="Temperature conversion from Kelvin to Celsius is incorrect.")
        print(f"Kelvin to Celsius Test Passed: {temp_kelvin}K = {converted_temp:.2f}°C")


if __name__ == '__main__':
    unittest.main()
