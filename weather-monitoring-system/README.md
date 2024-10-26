
**Overview**  
This Python-based real-time weather monitoring system fetches and stores Indian city weather data from the OpenWeatherMap API. It offers forecasting and visualizations via Streamlit, leveraging MySQL for data storage and Docker Compose for environment setup. The scheduler will automatically run every 1 minute to process weather data, and the application will check for updates every 1 minute to trigger alerts."


**Features**  
1.**Real-time Weather Data**: Automatically fetches real-time weather data for pre-defined cities at regular intervals.  
2.**Weather Forecast**: Collects weather forecast data and displays summarized insights.  
3.**Alerts**: Triggers alerts when the temperature exceeds city-specific thresholds.  
4.**Visualization**: Displays temperature trends, daily summaries, and alert history with visualizations using Plotly and Matplotlib.  
5.**Dynamic Threshold Settings**: Allows setting city-specific temperature thresholds and updates them in real-time.  

**Technologies Used :**  
**Frontend**: Streamlit for the web interface.  
**Backend:** Python for core logic.  
**Database**: MySQL for data storage.  
**API**: OpenWeatherMap API to fetch weather data.  
**Containerizatio**n: Docker & Docker Compose for containerized environments.  
**Visualization**: Plotly & Matplotlib for data visualization.  

**Configuration**  
The OpenWeatherMap API key [484b2b352eae133bc2d7abced19a421c] is hardcoded into the script, but you can modify it dynamically through the sidebar and validate the new key for accuracy.

**Installation**  
We leverage Docker to ensure seamless deployment and portability of the application across different environments.   

To deploy and run the Rule Engine application, we follow these steps:    

1.**Pull the Image**: We retrieve the latest Weather monitoring image from the Docker registry using the command  

                      docker pull shivanichoutapally/weather-monitoring:latest  
                      
2.**Create a Network**: A new Docker network named choutapally1-network is established to facilitate communication between containers using the command  

                       docker network create choutapally1-network  

3.**Start the MySQL Container**: A MySQL container is launched with the specified database credentials and port mapping. It's connected to the network using the commmand  

                       docker run -d --name mysql --network choutapally1-network -e MYSQL_ROOT_PASSWORD=9961 -e MYSQL_DATABASE=weather_data -e MYSQL_USER=user -e MYSQL_PASSWORD=userpassword -p 3306:3306 mysql:8.0

4.**Start the Rule Engine Container**: Finally, the Rule Engine container is started, linked to the MySQL container, and exposed on port 8501 using the command

                       docker run -d -p 8501:8501 --name vigilant_ellis --network choutapally1-network  -e MYSQL_HOST=mysql -e MYSQL_USER=user -e MYSQL_PASSWORD=userpassword -e MYSQL_DATABASE=weather_data shivanichoutapally/weather-monitoring:latest

                       Access the application : http://localhost:8501/


**Database Setup**:   
The MySQL database is initialized with three tables:  
**daily_summary**: Stores average, maximum, and minimum temperature for each day.    
**alerts**: Stores triggered alerts when a threshold is exceeded.    
**forecasts**: Stores forecast data for each city.    

**Testing**:   
To test the core logic independently of Streamlit, utilize the pre-integrated code_without_streamlit_logic file within the rule engine image. This file facilitates the verification of rule creation, evaluation, and combination  

 **To run the tests:**      
 **Access the Docker container shell** : docker exec -it <container_name> sh   
 **Run test cases**: python -m unittest <testcase_name>.py  
 **Execute the test cases**:   
                             tc1: python -m unittest system_setup.py  
                             tc2: python -m unittest data_retrieval.py  
                             tc3: python -m unittest temperature_conversion.py  
                             tc4: python -m unittest daily_weather_summary.py
                             tc5: python -m unittest alerting_thresholds.py 

 **Troubleshooting** :  
 **Common Issues** :  
 **API Key Errors**: Ensure the API key is valid; you can validate it through the Streamlit sidebar.  
 **Database Connection Errors**: Ensure Docker is running and the MySQL container is up.  
 **Data Retrieval Issues**: If API calls fail, check the network connection or API rate limits.  

 **Accessing portal Issues**:  
 **Issue 1**:   Bind for 0.0.0.0:8502 failed: port is already allocate.  
 **Solution** : Need to kill the existing process using below commands in host machine:  
                1.**netstat -ano | findstr :8502** -> to check if it is already using. if exists run next command.  
                2.**taskkill /PID <process_id> /F**  -> Here <process_id> referts to process id's  


**If you encounter issues with the Docker image, please set up the environment on your local machine and use pycharm**:  
**Clone Repository:** 
git clone https://github.com/yourusername/yourrepository.git    
cd yourrepository 

**Install Python Dependencies:**
python -m venv venv  
venv\Scripts\activate  **activate the environment**  
pip install -r requirements.txt  

**Set Up MySQL:**  
Install MySQL and create a database as per the configuration.
change the password and username in weather.py

**Run Application:**  
streamlit run weather.py  

**GUI Overview**  
Pic1 ![image](https://github.com/user-attachments/assets/8bf68ec1-341b-440d-b528-eedf4f552a75)
Pic2 ![pic2](https://github.com/user-attachments/assets/604d4a8b-7bb1-4535-8487-ce1a789430d8)





              
 
 

 


 






