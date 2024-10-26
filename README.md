This repository contains two distinct projects and both projects come with Docker images, making it easy to get started without manual installations. Below is a brief description of each:  

1. **Rule Engine**: The Rule Engine project is designed to handle dynamic rule evaluation.  

**Docker Instructions**: To ensure smooth operation of the Rule Engine, please verify that ports 8502 and 3307 are not currently in use. If these ports are occupied, kindly terminate the associated processes using the provided commands in powershell:  

   netstat -aon | findstr :[port]   
   taskkill /PID <process_id> 
   
Once the ports are free, proceed to run the Docker image and access the Rule Engine application at http://localhost:8502.  


2. **Weather Monitoring System** :The Weather Monitoring System is a real-time weather tracking tool using the OpenWeatherMap API.  

**Docker Instructions**: To ensure smooth operation of the Weather monitorinng app, please verify that ports 8501 and 3306 are not currently in use. If these ports are occupied, kindly terminate the associated processes using the provided commands in powershell:  

   netstat -aon | findstr :[port]   
   taskkill /PID <process_id> 
   
Once the ports are free, proceed to run the Docker image and access the weather monitor application at http://localhost:8501.  
   
