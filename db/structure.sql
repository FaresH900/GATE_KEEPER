-- Structure
CREATE DATABASE gatekeeping_db;
USE gatekeeping_db;

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    role ENUM('admin', 'resident', 'gatekeeper') NOT NULL,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL
);

CREATE TABLE residents (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT UNIQUE,
    face_data_ref BLOB,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE home(
    id INT AUTO_INCREMENT PRIMARY KEY,
    home_section varchar(20),
    home_num varchar(20),
    home_appart varchar(20),
    res_id int not null,
    FOREIGN KEY (res_id) REFERENCES residents(id)
);

CREATE TABLE cars (
    id INT AUTO_INCREMENT PRIMARY KEY,
    resident_id INT,
    license_plate VARCHAR(50) UNIQUE,
    FOREIGN KEY (resident_id) REFERENCES residents(id)
);

CREATE TABLE token_blocklist (
    id INT AUTO_INCREMENT PRIMARY KEY,
    jti VARCHAR(36) NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    user_id INT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Initial Data
-- Clear existing data
SET FOREIGN_KEY_CHECKS = 0;
TRUNCATE TABLE cars;
TRUNCATE TABLE home;
TRUNCATE TABLE residents;
TRUNCATE TABLE users;
SET FOREIGN_KEY_CHECKS = 1;

-- Insert users with bcrypt hashed password (password123)
INSERT INTO users (role, name, email, password_hash) 
VALUES 
    ('admin', 'Admin User', 'hossam@admin.com', '$2b$12$ctJiz1HyBMYbNxFs9HRoOe0Db53Q.pm7lipoH38g5tJF8Mp5CPBQq'),
    ('gatekeeper', 'Gatekeeper User', 'hossam@keeper.com', '$2b$12$ctJiz1HyBMYbNxFs9HRoOe0Db53Q.pm7lipoH38g5tJF8Mp5CPBQq'),
    ('resident', 'Resident User', 'hossam@resident.com', '$2b$12$ctJiz1HyBMYbNxFs9HRoOe0Db53Q.pm7lipoH38g5tJF8Mp5CPBQq');

-- Get the resident's user ID
SET @resident_user_id = (SELECT id FROM users WHERE email = 'hossam@resident.com');

-- Create resident record with NULL face_data_ref
INSERT INTO residents (user_id, face_data_ref) 
VALUES (@resident_user_id, NULL);

-- Get the resident ID
SET @resident_id = LAST_INSERT_ID();

-- Add home information
INSERT INTO home (home_section, home_num, home_appart, res_id) 
VALUES ('A', '101', '1', @resident_id);

-- Add car for the resident
INSERT INTO cars (resident_id, license_plate) 
VALUES (@resident_id, 'ABC123');