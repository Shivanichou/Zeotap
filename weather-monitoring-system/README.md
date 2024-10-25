
**Overview**  
This Python-based real-time weather monitoring system fetches and stores Indian city weather data from the OpenWeatherMap API. It offers forecasting and visualizations via Streamlit, leveraging MySQL for data storage and Docker Compose for environment setup.
**Access the Application at**: http://localhost:8501/ [ if any issues please refer access section in below ]

**Features**  
1.**Real-time Weather Data**: Automatically fetches real-time weather data for pre-defined cities at regular intervals.  
2.**Weather Forecast**: Collects weather forecast data and displays summarized insights.  
3.**Alerts**: Triggers alerts when the temperature exceeds city-specific thresholds.  
4.**Visualization**: Displays temperature trends, daily summaries, and alert history with visualizations using Plotly and Matplotlib.  
5.**Dynamic Settings**: Allows setting city-specific temperature thresholds and updates them in real-time.  

**Technologies Used :**  
**Python**.  
**Streamlit**: For the web interface.  
**MySQL**: For data storage.  
**OpenWeatherMap API**: To fetch weather data.  
**Docker & Docker Compose**: For containerized environments.  
**Plotly & Matplotlib**: For data visualization.  

**Configuration**  
The OpenWeatherMap API key [484b2b352eae133bc2d7abced19a421c] is hardcoded into the script, but you can modify it dynamically through the sidebar and validate the new key for accuracy.

**Installation**  
1.**Pull the Weather-monitor-app image**: docker pull yourusername/weather-monitor-app:latest  
2.**pull the sql image** : docker pull mysql:8.0  
3.**run the Docker image** : docker run -p 8501:8501 yourusername/weather-monitor-app:latest  

**Note**:The Docker Compose file already includes hardcoded credentials for MySQL, eliminating the need for additional configuration during deployment.

**Database Setup**:  
The MySQL database is initialized with three tables:
**daily_summary**: Stores average, maximum, and minimum temperature for each day.  
**alerts**: Stores triggered alerts when a threshold is exceeded.  
**forecasts**: Stores forecast data for each city.  

**Testing**:  
 For testing the core logic without Streamlit, use the provided **corelogic_without_streamlit_for_testing.py** file provided in testcases folder. This file includes automated API calls, weather data retrieval, and temperature conversion verification.    

 **To run the tests:**  
 **Go to docker shell from cmd**: docker exec -it rule-engine-app sh  
 **Run test cases**: python -m unittest <testcase_name>.py  

 **Troubleshooting** :
 **Common Issues** :
 **API Key Errors**: Ensure the API key is valid; you can validate it through the Streamlit sidebar.
 **Database Connection Errors**: Ensure Docker is running and the MySQL container is up.
 **Data Retrieval Issues**: If API calls fail, check the network connection or API rate limits.

 **Accessing portal Issues**:
 **Issue 1**:   Bind for 0.0.0.0:8502 failed: port is already allocate.
 **Solution** : Need to kill the existing process using below commands in host machine:
                1.**netstat -ano | findstr :8502** -> to check if it is already using. if exists run next command.
                2.**taskkill /PID <PID> /F**  -> Here <PID> referts to process id's

              
 
 

 


 






