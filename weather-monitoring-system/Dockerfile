# Use Python 3.9 base image
FROM python:3.9

# Set the working directory inside the container
WORKDIR /app

# Copy the local project files to the container
COPY . .

# Install required Python packages from requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Install MySQL client (only if you need it for database initialization or other purposes)
RUN apt-get update && apt-get install -y default-mysql-client

# Wait for MySQL to be ready, initialize the database, and run Streamlit
CMD ["sh", "-c", "until mysqladmin ping -h \"$MYSQL_HOST\" --silent; do echo 'Waiting for MySQL...'; sleep 5; done && mysql -h \"$MYSQL_HOST\" -u \"$MYSQL_USER\" -p\"$MYSQL_PASSWORD\" \"$MYSQL_DATABASE\" < /app/init_db.sql && streamlit run weather.py --server.port=8501 --server.address=0.0.0.0"]

