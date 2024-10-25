**Overview**  
This project is a real-time rule-based engine that defines, modifies, evaluates, and manages business rules. It leverages a Streamlit GUI and MySQL database for user interface and data storage, respectively.  

**Features**
**Create New Rules**       : Define rules with logical and comparison operators.  
**View and Delete Rules**  : Manage existing rules directly from the interface.  
**Update Rules**           : Modify rules that are already stored in the database.  
**Combine Rules**          : Merge multiple rules with a selected logical operator.  
**Evaluate Rules**         : Check if user-provided input values satisfy existing rules.  
**Dynamic Attribute Input**: User-friendly form for entering evaluation data.  

**Technologies Used:**
**Frontend**        : Streamlit for building a web-based interface.  
**Backend**         : Python 3.12.3 for rule evaluation logic.  
**Databas**e        : MySQL for storing rules.  
**Containerization**: Docker & Docker Compose for containerized environments.

**System Architecture**  
The system is divided into four components:  
**Database Layer**: Handles rule storage and management using MySQL.    
**Rule Processing**: Includes parsing, validation, and combination of rules.    
**Rule Evaluation**: Evaluates user input data against defined rules.    
**User Interface**: Built with Streamlit for rule creation, modification, and evaluation.  

**Installation**    
We leverage Docker to ensure seamless deployment and portability of the application across different environments.  
1.**Pull the Rule image**: docker pull yourusername/weather-monitor-app:latest.   
2.**pull the sql image** : docker pull mysql:8.0.  
3.**run the Docker image** : docker run -p 8501:8501 yourusername/weather-monitor-app:latest.  

**Database Setup**  
The MySQL database is initialized with two tables:    
**rules table**   : Store Business Rules,Organize Rules by ID,Facilitate Rule Management.  
**metadata table**: Store Application Configuration,Version Control.  

**Evaluation logic**: lets say there are four rules,
 Rule 1: age=10
 Rule 2: age>10 or salary=1000
 Rule 3: age>10 and salary=1000 and experience=5
 Rule 4: age>10 and salary=1000 or experience=5 
 Rule 5: age>10 and salary=1000 and experience=5 and department ='HR'

 case 1: If user entered only age attribute then only Rule 1 executes.
 case 2: if user enetered only 
 

**Testing**:  
 For testing the core logic without Streamlit, use the provided **corelogic_without_streamlit_for_testing** file provided in testcases folder. This file create rule,evaluate rule,combine_rule verification.       

 **To run the tests:**   
 **Go to docker shell from cmd**: docker exec -it <container_name> sh    
 **Run test cases**: python -m unittest <testcase_name>.py    

**Accessing portal Issue**s:  
**Issue 1**: Bind for 0.0.0.0:8502 failed: port is already allocate.  
**Solution** : Need to kill the existing process using below commands in host machine:    
              1.**netstat -ano | findstr :8502 **-> to check if it is already using. if exists run next command.    
              2.**taskkill /PID <process_id> /F **-> Here <process_id> referts to process id's    
              
**If you encounter issues with the Docker image, please set up the environment on your local machine and use pycharm:**  
**Clone Repository**: git clone https://github.com/yourusername/yourrepository.git  
                      cd yourrepository  

**Install Python Dependencies**:   
python -m venv venv  
venv\Scripts\activate activate the environment   
pip install -r requirements.txt  

**Set Up MySQL**:   
Install MySQL and create a database as per the configuration. change the password and username in rule_engine.py  

****Run Application**:  
streamlit run rule_engine.py  

**GUI Overview** 
![image](https://github.com/user-attachments/assets/aae1894a-492c-4e64-b199-9f9e526703a4)


