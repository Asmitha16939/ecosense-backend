-- EcoSense Database Setup Script
-- Run this once: mysql -u root -p < init_db.sql

CREATE DATABASE IF NOT EXISTS ecosense CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE ecosense;

-- Electricity usage logs
CREATE TABLE IF NOT EXISTS electricity_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    appliance_type VARCHAR(50) NOT NULL,
    appliance_count INT NOT NULL DEFAULT 1,
    hours_per_day FLOAT NOT NULL,
    days_per_week INT NOT NULL,
    occupancy FLOAT NOT NULL DEFAULT 1.0,
    tariff FLOAT NOT NULL DEFAULT 6.0,
    monthly_kwh FLOAT NOT NULL,
    monthly_cost FLOAT NOT NULL,
    carbon_kg FLOAT NOT NULL,
    efficiency VARCHAR(20) NOT NULL,
    waste_percentage FLOAT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Water usage logs
CREATE TABLE IF NOT EXISTS water_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    activity_type VARCHAR(50) NOT NULL,
    flow_rate FLOAT NOT NULL,
    duration_minutes FLOAT NOT NULL,
    sessions_per_day INT NOT NULL,
    days_per_week INT NOT NULL,
    water_rate FLOAT NOT NULL DEFAULT 10.0,
    daily_liters FLOAT NOT NULL,
    monthly_liters FLOAT NOT NULL,
    monthly_cost FLOAT NOT NULL,
    comparison_rating VARCHAR(20) NOT NULL,
    ratio FLOAT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Eco-cleaning logs
CREATE TABLE IF NOT EXISTS cleaning_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    product_type VARCHAR(100) NOT NULL,
    usage_frequency VARCHAR(50) NOT NULL,
    rooms INT NOT NULL DEFAULT 1,
    eco_score INT NOT NULL,
    chemical_load VARCHAR(20) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Achievements / Badges table
CREATE TABLE IF NOT EXISTS achievements (
    id INT AUTO_INCREMENT PRIMARY KEY,
    badge_key VARCHAR(50) UNIQUE NOT NULL,
    title VARCHAR(100) NOT NULL,
    description TEXT NOT NULL,
    icon VARCHAR(10) NOT NULL,
    category VARCHAR(30) NOT NULL,
    threshold_value FLOAT NOT NULL DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE
);

-- Seed achievements
INSERT IGNORE INTO achievements (badge_key, title, description, icon, category, threshold_value) VALUES
('first_calc',       'First Step',         'Completed your first energy calculation',                  '🌱', 'general',     1),
('eco_warrior',      'Eco Warrior',         'Calculated electricity 10 times',                         '⚡', 'electricity',  10),
('water_keeper',     'Water Keeper',        'Analyzed water usage 10 times',                           '💧', 'water',        10),
('clean_green',      'Clean & Green',       'Analyzed eco-cleaning 5 times',                           '🧹', 'cleaning',     5),
('efficiency_pro',   'Efficiency Pro',      'Achieved "Efficient" rating 5 times in electricity',      '🏆', 'electricity',  5),
('water_saver',      'Water Saver',         'Achieved "Good" rating 5 times in water usage',           '💦', 'water',        5),
('carbon_fighter',   'Carbon Fighter',      'Logged total carbon footprint over 100 kg CO₂ tracked',  '🌍', 'electricity',  100),
('data_analyst',     'Data Analyst',        'Used the Analysis page (10+ records in history)',         '📊', 'general',      10),
('consistent_user',  'Consistent User',     'Logged activity 7 days in a row',                        '📅', 'general',      7),
('green_home',       'Green Home',          'Used all three analyzers (electricity, water, cleaning)', '🏡', 'general',      3);
