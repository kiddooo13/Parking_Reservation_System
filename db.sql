CREATE DATABASE IF NOT EXISTS parking_system;
USE parking_system;

CREATE TABLE IF NOT EXISTS users (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(100) NOT NULL,
  email VARCHAR(100) UNIQUE NOT NULL,
  password VARCHAR(100) NOT NULL,
  role ENUM('owner','user') NOT NULL
);

CREATE TABLE IF NOT EXISTS parking_lots (
  id INT AUTO_INCREMENT PRIMARY KEY,
  owner_id INT NOT NULL,
  name VARCHAR(100) NOT NULL,
  location VARCHAR(255) NOT NULL,
  latitude DECIMAL(10,7) DEFAULT NULL,
  longitude DECIMAL(10,7) DEFAULT NULL,
  price DECIMAL(10,2) NOT NULL,
  slots INT NOT NULL,
  FOREIGN KEY (owner_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS slot_status (
  id INT AUTO_INCREMENT PRIMARY KEY,
  lot_id INT NOT NULL,
  slot_number INT NOT NULL,
  status ENUM('available','occupied','reserved') NOT NULL DEFAULT 'available',
  FOREIGN KEY (lot_id) REFERENCES parking_lots(id),
  UNIQUE KEY uniq_slot (lot_id, slot_number)
);

CREATE TABLE IF NOT EXISTS bookings (
  id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT NOT NULL,
  lot_id INT NOT NULL,
  slot_number INT NOT NULL,
  vehicle VARCHAR(50),
  start_time DATETIME NOT NULL,
  end_time DATETIME NOT NULL,
  status ENUM('reserved','active','expired') NOT NULL DEFAULT 'reserved',
  payment_id VARCHAR(100),
  amount DECIMAL(10,2) NOT NULL DEFAULT 0.00,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id),
  FOREIGN KEY (lot_id) REFERENCES parking_lots(id)
);

CREATE TABLE IF NOT EXISTS temp_booking_context (
  id INT AUTO_INCREMENT PRIMARY KEY,
  razorpay_order_id VARCHAR(100) NOT NULL,
  user_id INT NOT NULL,
  lot_id INT NOT NULL,
  slot_number INT NOT NULL,
  vehicle VARCHAR(50),
  start_time DATETIME NOT NULL,
  end_time DATETIME NOT NULL,
  amount DECIMAL(10,2) NOT NULL DEFAULT 0.00,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id),
  FOREIGN KEY (lot_id) REFERENCES parking_lots(id)
);