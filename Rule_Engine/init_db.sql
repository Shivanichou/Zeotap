-- Create the database if it does not exist
CREATE DATABASE IF NOT EXISTS rule_engine;

-- Use the created database
USE rule_engine;

-- Create the `rules` table if it does not exist
CREATE TABLE IF NOT EXISTS rules (
    id INT AUTO_INCREMENT PRIMARY KEY,
    rule_string TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create the `application_metadata` table if it does not exist
CREATE TABLE IF NOT EXISTS application_metadata (
    id INT AUTO_INCREMENT PRIMARY KEY,
    metadata_key VARCHAR(255) NOT NULL,
    metadata_value TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert initial metadata information into the `application_metadata` table
INSERT INTO application_metadata (metadata_key, metadata_value) VALUES 
('app_name', 'Rule Engine Application'),
('version', '1.0.0'),
('last_updated', '2024-10-25'),
('author', 'Shivani Choutapally'),
('description', 'An application to manage and evaluate rules for different conditions.'),
('database_connection', 'MySQL'),
('framework', 'Streamlit'),
('language', 'Python');
