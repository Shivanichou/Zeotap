CREATE DATABASE IF NOT EXISTS weather_data;

USE weather_data;

CREATE TABLE IF NOT EXISTS daily_summary (
    id INT AUTO_INCREMENT PRIMARY KEY,
    city VARCHAR(100),
    avg_temp FLOAT,
    max_temp FLOAT,
    min_temp FLOAT,
    dominant_condition VARCHAR(50),
    date DATE,
    avg_feels_like FLOAT,
    avg_humidity FLOAT,
    avg_wind_speed FLOAT
);

CREATE TABLE IF NOT EXISTS alerts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    city VARCHAR(100),
    temp FLOAT,
    timestamp DATETIME
);

CREATE TABLE IF NOT EXISTS forecasts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    city VARCHAR(100),
    timestamp DATETIME,
    temp FLOAT,
    feels_like FLOAT,
    humidity INT,
    wind_speed FLOAT,
    weather_condition VARCHAR(50)
);
