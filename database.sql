CREATE DATABASE civic_ai;

USE civic_ai;

CREATE TABLE complaints (

    id INT AUTO_INCREMENT PRIMARY KEY,

    image VARCHAR(255),

    issue_type VARCHAR(100),

    severity VARCHAR(50),

    description TEXT,

    description_marathi TEXT,

    solution TEXT,

    latitude VARCHAR(50),

    longitude VARCHAR(50),

    status VARCHAR(50),

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
SET SQL_SAFE_UPDATES = 0;
DELETE FROM complaints;

CREATE TABLE users (

    id INT AUTO_INCREMENT PRIMARY KEY,

    name VARCHAR(100),

    email VARCHAR(100) UNIQUE,

    password VARCHAR(100),

    role VARCHAR(50)

);