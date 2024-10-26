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
**Database**        : MySQL for storing rules.  
**Containerization**: Docker & Docker Compose for containerized environments.

**System Architecture**  
The system is divided into four components:  
**Database Layer**: Handles rule storage and management using MySQL.    
**Rule Processing**: Includes parsing, validation, and combination of rules.    
**Rule Evaluation**: Evaluates user input data against defined rules.    
**User Interface**: Built with Streamlit for rule creation, modification, and evaluation.  

**Installation**    
We leverage Docker to ensure seamless deployment and portability of the application across different environments. 

To deploy and run the Rule Engine application, we follow these steps:  

1.**Pull the Image**: We retrieve the latest Rule Engine image from the Docker registry using the command

                      docker pull shivanichoutapally/rule-engine-app:v1.0  
                      
2.**Create a Network**: A new Docker network named choutapally-network is established to facilitate communication between containers using the command 

                      docker network create choutapally-network 
                      
3.**Start the MySQL Container**: A MySQL container is launched with the specified database credentials and port mapping. It's connected to the network using the commmand

                      docker run -d --name rule-engine-db --network choutapally-network -e MYSQL_ROOT_PASSWORD=9961 -e MYSQL_DATABASE=rule_engine -e MYSQL_USER=user -e MYSQL_PASSWORD=userpassword -p 3307:3306 mysql:8.0  
                                  
4.**Start the Rule Engine Container**: Finally, the Rule Engine container is started, linked to the MySQL container, and exposed on port 8502 using the command

                     docker run -d -p 8502:8501 --name vigilant_ellit --network choutapally-network -e MYSQL_HOST=rule-engine-db -e MYSQL_USER=user -e MYSQL_PASSWORD=userpassword -e MYSQL_DATABASE=rule_engine shivanichoutapally/rule-engine-app:v1.0 
                                 
Access the application at  http://localhost:8502/   # If having access issues please refer **Accessing portal Issues** in below.

**Database Setup**  
The MySQL database is initialized with two tables:    
**rules table**   : Store Business Rules,Organize Rules by ID,Facilitate Rule Management.  
**metadata table**: Store Application Configuration,Version Control.  

**Evaluation logic**:  
 **Rule Definitions**  
 **Rule 1**: age=10     
 **Rule 2**: age>10 or salary=1000     
 **Rule 3**: age>10 and salary=1000 and experience=5     
 **Rule 4**: age>10 and salary=1000 or experience=5       
 **Rule 5**: age>10 and salary=1000 and experience=5 and department ='HR'   

Execution Scenarios:  

**Single Attribute**: If the user only provides the age attribute, only **Rule 1** is evaluated.   

**Multiple Attributes**: 

If the user provides age, salary, and experience, **Rules 3 and 4** are evaluated.   
If the user provides age, salary,experience, and department, **Rule 5** is evaluated.   

**Combined logic**:  

 When two rules are combined, the system determines the most frequent logical operator (AND or OR) present in both rules. This operator is then used to combine the conditions of the two rules.     
 Note: Combined rules are not persisted in the database. They are evaluated dynamically based on the user's input and the specified rules.     
 Example:   
 If Rule 3 and Rule 4 are combined, the resulting combined rule would be:    
 (age > 10 AND salary = 1000 AND experience = 5) AND (age > 10 AND salary = 1000 OR experience = 5)    
   
**Testing**:    
To test the core logic independently of Streamlit, utilize the pre-integrated corelogic_without_streamlit_for_testing file within the rule engine image. This file facilitates the verification of rule creation, evaluation, and combination          

 **To run the tests:**    
 **Access the Docker container shell** : docker exec -it <container_name> sh      
 **Execute the test cases**:   
                             tc1: python -m unittest tc_create_rule.py  
                             tc2: python -m unittest tc_combine_rule.py  
                             tc3: python -m unittest tc_evaluate_rule.py  
                             tc4: python -m unittest tc_combining_additional_rule.py  

**Accessing portal Issues**: 

**Issue **: Bind for 0.0.0.0:8502 or 3307 failed: port is already allocate.  or unable to access the application.   
**Solution** : Docker Instructions: To ensure smooth operation of the Rule Engine, please verify that ports 8502 and 3307 are not currently in use. If these ports are occupied, kindly terminate the associated processes using the provided commands in powershell:  

netstat -aon | findstr :[port]  # To check availablity of ports.  
taskkill /PID <process_id> /F   # If ports busy kill them.  

Once the ports are free, proceed to run the Docker image and access the Rule Engine application at http://localhost:8502.  

  
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


