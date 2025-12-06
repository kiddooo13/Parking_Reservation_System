-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Nov 24, 2025 at 07:17 AM
-- Server version: 10.4.32-MariaDB
-- PHP Version: 8.0.30

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `parking_system`
--

-- --------------------------------------------------------

--
-- Table structure for table `bookings`
--

CREATE TABLE `bookings` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `lot_id` int(11) NOT NULL,
  `slot_number` int(11) NOT NULL,
  `vehicle` varchar(50) DEFAULT NULL,
  `start_time` datetime NOT NULL,
  `end_time` datetime NOT NULL,
  `status` enum('reserved','active','expired') NOT NULL DEFAULT 'reserved',
  `payment_id` varchar(100) DEFAULT NULL,
  `amount` decimal(10,2) NOT NULL DEFAULT 0.00,
  `created_at` datetime DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `bookings`
--

INSERT INTO `bookings` (`id`, `user_id`, `lot_id`, `slot_number`, `vehicle`, `start_time`, `end_time`, `status`, `payment_id`, `amount`, `created_at`) VALUES
(2, 12, 6, 1, 'KA34ED9855', '2025-11-23 17:32:00', '2025-11-23 18:32:00', 'expired', 'pay_RjArxc8sV8gQKs', 40.00, '2025-11-23 17:31:40'),
(4, 14, 7, 12, 'KA34ED985', '2025-11-23 19:53:00', '2025-11-23 20:53:00', 'expired', 'pay_RjCGihoZ1L187F', 30.00, '2025-11-23 18:53:48'),
(5, 12, 7, 2, 'KA34ED9855', '2025-11-23 20:07:00', '2025-11-23 21:07:00', 'expired', 'pay_RjCVGFv07RhGwH', 30.00, '2025-11-23 19:07:34'),
(6, 12, 6, 1, 'KA34ED985', '2025-11-23 23:06:00', '2025-11-24 02:06:00', 'reserved', 'pay_RjFZ1XnAcoLY0d', 120.00, '2025-11-23 22:07:12'),
(7, 14, 7, 13, 'KA34DS0192', '2025-11-23 22:51:00', '2025-11-23 23:51:00', 'reserved', 'pay_RjGJMelv4WuVsb', 30.00, '2025-11-23 22:51:04');

-- --------------------------------------------------------

--
-- Table structure for table `parking_lots`
--

CREATE TABLE `parking_lots` (
  `id` int(11) NOT NULL,
  `owner_id` int(11) NOT NULL,
  `name` varchar(100) NOT NULL,
  `location` varchar(255) NOT NULL,
  `latitude` decimal(10,7) DEFAULT NULL,
  `longitude` decimal(10,7) DEFAULT NULL,
  `price` decimal(10,2) NOT NULL,
  `slots` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `parking_lots`
--

INSERT INTO `parking_lots` (`id`, `owner_id`, `name`, `location`, `latitude`, `longitude`, `price`, `slots`) VALUES
(6, 11, 'Infantry Parking', 'Beside Hot Breads, Infantry Road, Ballari', 15.1518370, 76.9026110, 40.00, 20),
(7, 13, 'SN Parking', 'Beside Cool corner, SN Pet, Ballari', 15.1471670, 76.9338320, 30.00, 30);

-- --------------------------------------------------------

--
-- Table structure for table `slot_status`
--

CREATE TABLE `slot_status` (
  `id` int(11) NOT NULL,
  `lot_id` int(11) NOT NULL,
  `slot_number` int(11) NOT NULL,
  `status` enum('available','occupied','reserved') NOT NULL DEFAULT 'available'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `slot_status`
--

INSERT INTO `slot_status` (`id`, `lot_id`, `slot_number`, `status`) VALUES
(76, 6, 1, 'reserved'),
(77, 6, 2, 'available'),
(78, 6, 3, 'available'),
(79, 6, 4, 'available'),
(80, 6, 5, 'available'),
(81, 6, 6, 'available'),
(82, 6, 7, 'available'),
(83, 6, 8, 'available'),
(84, 6, 9, 'available'),
(85, 6, 10, 'available'),
(86, 6, 11, 'available'),
(87, 6, 12, 'available'),
(88, 6, 13, 'available'),
(89, 6, 14, 'available'),
(90, 6, 15, 'available'),
(91, 6, 16, 'available'),
(92, 6, 17, 'available'),
(93, 6, 18, 'available'),
(94, 6, 19, 'available'),
(95, 6, 20, 'available'),
(107, 7, 1, 'available'),
(108, 7, 2, 'available'),
(109, 7, 3, 'available'),
(110, 7, 4, 'available'),
(111, 7, 5, 'available'),
(112, 7, 6, 'available'),
(113, 7, 7, 'available'),
(114, 7, 8, 'available'),
(115, 7, 9, 'available'),
(116, 7, 10, 'available'),
(117, 7, 11, 'available'),
(118, 7, 12, 'available'),
(119, 7, 13, 'reserved'),
(120, 7, 14, 'available'),
(121, 7, 15, 'available'),
(122, 7, 16, 'available'),
(123, 7, 17, 'available'),
(124, 7, 18, 'available'),
(125, 7, 19, 'available'),
(126, 7, 20, 'available'),
(127, 7, 21, 'available'),
(128, 7, 22, 'available'),
(129, 7, 23, 'available'),
(130, 7, 24, 'available'),
(131, 7, 25, 'available'),
(132, 7, 26, 'available'),
(133, 7, 27, 'available'),
(134, 7, 28, 'available'),
(135, 7, 29, 'available'),
(136, 7, 30, 'available');

-- --------------------------------------------------------

--
-- Table structure for table `temp_booking_context`
--

CREATE TABLE `temp_booking_context` (
  `id` int(11) NOT NULL,
  `razorpay_order_id` varchar(100) NOT NULL,
  `user_id` int(11) NOT NULL,
  `lot_id` int(11) NOT NULL,
  `slot_number` int(11) NOT NULL,
  `vehicle` varchar(50) DEFAULT NULL,
  `start_time` datetime NOT NULL,
  `end_time` datetime NOT NULL,
  `amount` decimal(10,2) NOT NULL DEFAULT 0.00,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `users`
--

CREATE TABLE `users` (
  `id` int(11) NOT NULL,
  `name` varchar(100) NOT NULL,
  `email` varchar(100) NOT NULL,
  `password` varchar(100) NOT NULL,
  `role` enum('owner','user') NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `users`
--

INSERT INTO `users` (`id`, `name`, `email`, `password`, `role`) VALUES
(11, 'kamran', 'kamran@gmail.com', '123456', 'owner'),
(12, 'kamran1', 'kamran1@gmail.com', '123456', 'user'),
(13, 'apoorva', 'apoorva@gmail.com', '123456', 'owner'),
(14, 'apoorva1', 'apoorva1@gmail.com', '123456', 'user');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `bookings`
--
ALTER TABLE `bookings`
  ADD PRIMARY KEY (`id`),
  ADD KEY `user_id` (`user_id`),
  ADD KEY `lot_id` (`lot_id`);

--
-- Indexes for table `parking_lots`
--
ALTER TABLE `parking_lots`
  ADD PRIMARY KEY (`id`),
  ADD KEY `owner_id` (`owner_id`);

--
-- Indexes for table `slot_status`
--
ALTER TABLE `slot_status`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `uniq_slot` (`lot_id`,`slot_number`);

--
-- Indexes for table `temp_booking_context`
--
ALTER TABLE `temp_booking_context`
  ADD PRIMARY KEY (`id`),
  ADD KEY `user_id` (`user_id`),
  ADD KEY `lot_id` (`lot_id`);

--
-- Indexes for table `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `email` (`email`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `bookings`
--
ALTER TABLE `bookings`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=8;

--
-- AUTO_INCREMENT for table `parking_lots`
--
ALTER TABLE `parking_lots`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=8;

--
-- AUTO_INCREMENT for table `slot_status`
--
ALTER TABLE `slot_status`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=137;

--
-- AUTO_INCREMENT for table `temp_booking_context`
--
ALTER TABLE `temp_booking_context`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=10;

--
-- AUTO_INCREMENT for table `users`
--
ALTER TABLE `users`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=15;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `bookings`
--
ALTER TABLE `bookings`
  ADD CONSTRAINT `bookings_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`),
  ADD CONSTRAINT `bookings_ibfk_2` FOREIGN KEY (`lot_id`) REFERENCES `parking_lots` (`id`);

--
-- Constraints for table `parking_lots`
--
ALTER TABLE `parking_lots`
  ADD CONSTRAINT `parking_lots_ibfk_1` FOREIGN KEY (`owner_id`) REFERENCES `users` (`id`);

--
-- Constraints for table `slot_status`
--
ALTER TABLE `slot_status`
  ADD CONSTRAINT `slot_status_ibfk_1` FOREIGN KEY (`lot_id`) REFERENCES `parking_lots` (`id`);

--
-- Constraints for table `temp_booking_context`
--
ALTER TABLE `temp_booking_context`
  ADD CONSTRAINT `temp_booking_context_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`),
  ADD CONSTRAINT `temp_booking_context_ibfk_2` FOREIGN KEY (`lot_id`) REFERENCES `parking_lots` (`id`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
