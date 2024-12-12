-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: db:3306
-- Generation Time: Dec 12, 2024 at 04:34 AM
-- Server version: 8.0.34
-- PHP Version: 8.2.8

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `yellatp_KonnectR`
--

-- --------------------------------------------------------

--
-- Table structure for table `Followers`
--

CREATE TABLE `Followers` (
  `follower_id` int NOT NULL,
  `followed_id` int NOT NULL,
  `followed_at` datetime NOT NULL
) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_as_ci;

--
-- Dumping data for table `Followers`
--

INSERT INTO `Followers` (`follower_id`, `followed_id`, `followed_at`) VALUES
(5, 7, '2024-11-23 22:29:19'),
(5, 9, '2024-11-23 22:29:25'),
(5, 4, '2024-11-23 22:29:29'),
(7, 2, '2024-12-07 02:23:13'),
(7, 5, '2024-12-07 02:39:53'),
(16, 7, '2024-12-09 06:24:20'),
(20, 8, '2024-12-09 07:41:10'),
(20, 14, '2024-12-09 07:41:12'),
(20, 12, '2024-12-09 07:41:16'),
(20, 26, '2024-12-09 07:41:23'),
(20, 11, '2024-12-09 07:41:27'),
(20, 16, '2024-12-09 07:41:29'),
(20, 21, '2024-12-09 08:52:27'),
(20, 25, '2024-12-09 08:52:31'),
(27, 10, '2024-12-09 10:37:14');

-- --------------------------------------------------------

--
-- Table structure for table `Messages`
--

CREATE TABLE `Messages` (
  `message_id` int NOT NULL,
  `sender_id` int NOT NULL,
  `receiver_id` int NOT NULL,
  `message_text` text COLLATE utf8mb4_0900_as_ci NOT NULL,
  `sent_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `read_status` tinyint(1) DEFAULT '0',
  `deleted` tinyint(1) DEFAULT '0',
  `pinned` tinyint(1) DEFAULT '0'
) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_as_ci;

--
-- Dumping data for table `Messages`
--

INSERT INTO `Messages` (`message_id`, `sender_id`, `receiver_id`, `message_text`, `sent_at`, `read_status`, `deleted`, `pinned`) VALUES
(1, 10, 8, 'Applied for: Research on Quantum Computing Opportunity\n\nI am interested in this opportunity and would like to discuss further.', '2024-11-22 13:46:06', 0, 0, 0),
(2, 10, 9, 'Applied for: Research on Mixed Reality\n\nI am interested in this opportunity and would like to discuss further.', '2024-11-22 13:54:06', 1, 0, 0),
(3, 10, 7, 'Applied for: Collaboration on developing an Ecommerce Recommendation System\n\nI am interested in this opportunity and would like to discuss further.', '2024-11-22 13:54:37', 1, 0, 0),
(4, 10, 6, 'Applied for: Research on Artificial General Intelligence\n\nI am interested in this opportunity and would like to discuss further.', '2024-11-22 13:54:47', 0, 0, 0),
(5, 10, 6, 'Hey', '2024-11-22 14:02:00', 0, 0, 0),
(6, 5, 7, 'Applied for: Collaboration on developing an Ecommerce Recommendation System\n\nI am interested in this opportunity and would like to discuss further.', '2024-11-22 14:04:52', 1, 0, 0),
(7, 5, 7, 'Hey Pavan', '2024-11-22 14:05:34', 1, 0, 0),
(8, 7, 10, 'Hey Skanda, Thank you for showing your interest on developing an Ecommerce Recommendation System, Could you tell us more about you..?', '2024-11-22 14:07:53', 1, 0, 0),
(9, 7, 5, 'Hey Hari..', '2024-11-22 14:08:22', 1, 0, 0),
(10, 7, 5, 'What brings you here', '2024-11-22 14:37:49', 1, 0, 0),
(11, 5, 7, 'Your project looks quite interesting', '2024-11-22 14:38:48', 1, 0, 0),
(12, 10, 7, 'Hey Pavan,', '2024-11-22 19:27:56', 1, 0, 0),
(13, 10, 7, 'Glad to Meet you here', '2024-11-22 19:28:17', 1, 0, 0),
(14, 10, 7, 'I\'ve been working on ML and DL projects under the guidence of professor Lord Boya', '2024-11-22 19:29:19', 1, 0, 0),
(15, 5, 5, 'Applied for: Research on ASI (Artificial Super Intelligence)\n\nI am interested in this opportunity and would like to discuss further.', '2024-11-23 21:53:48', 1, 0, 0),
(16, 5, 4, 'Hey..', '2024-11-23 22:29:57', 0, 0, 0),
(17, 7, 5, 'Thank you Harithra', '2024-12-05 15:37:12', 1, 0, 0),
(18, 7, 10, 'Are you kidding me? Did you just say \'Prof Boya\'? That\'s psycho, bro!', '2024-12-05 15:40:59', 0, 0, 0),
(19, 7, 5, 'Applied for: Research on ASI (Artificial Super Intelligence)\n\nI am interested in this opportunity and would like to discuss further.', '2024-12-05 17:56:20', 1, 0, 0),
(20, 7, 5, 'Hey, Could you share bit more about your profile..?', '2024-12-05 17:57:20', 1, 0, 0),
(21, 7, 10, 'BTW, could you share your Github profile..?', '2024-12-06 12:39:37', 0, 0, 0),
(22, 5, 7, 'Sure, Here you go', '2024-12-06 13:08:45', 1, 0, 0),
(23, 5, 7, 'Give me a moment Paone', '2024-12-06 13:50:00', 1, 0, 0),
(24, 7, 5, 'Sure', '2024-12-07 01:45:28', 1, 0, 0),
(25, 7, 2, 'Hi vidhya', '2024-12-07 02:23:33', 1, 0, 0),
(26, 2, 7, 'Hey Pavan', '2024-12-07 05:02:36', 1, 0, 0),
(27, 7, 2, 'How are you doing ?', '2024-12-07 05:04:32', 1, 0, 0),
(28, 2, 7, 'I am good, How abt U ...?', '2024-12-07 05:05:04', 1, 0, 0),
(29, 9, 10, 'Thank you for your Interest in this role. I am sorry to inform you that we got enough applications and we are unable to proceed with your candidature', '2024-12-09 00:51:24', 0, 0, 0),
(30, 2, 7, 'U there..?', '2024-12-09 04:59:50', 1, 0, 0),
(31, 20, 25, 'Hi', '2024-12-09 08:52:34', 0, 0, 0),
(32, 27, 10, 'Hi', '2024-12-09 10:37:17', 0, 0, 0),
(33, 7, 2, 'Yupp', '2024-12-09 10:42:41', 1, 0, 0),
(34, 7, 2, 'Hey', '2024-12-09 16:06:51', 1, 0, 0),
(35, 2, 7, 'Hi', '2024-12-09 16:07:50', 1, 0, 0),
(36, 5, 2, 'Hi', '2024-12-11 14:14:39', 1, 0, 0),
(37, 7, 5, 'Hey', '2024-12-11 14:15:16', 1, 0, 0),
(38, 5, 7, 'Hello', '2024-12-11 14:16:42', 1, 0, 0),
(39, 2, 5, 'Hey Vidhya', '2024-12-11 14:18:08', 1, 0, 0),
(40, 5, 2, 'Hey Hari', '2024-12-11 14:19:19', 0, 0, 0),
(41, 7, 5, 'Hi Hari', '2024-12-11 15:39:30', 1, 0, 0),
(42, 7, 20, 'Applied for: Dojo System\n\nI am interested in this opportunity and would like to discuss further.', '2024-12-11 15:43:28', 1, 0, 0),
(43, 7, 16, 'Applied for: Mixed Reality Exploration: Glasswing\n\nI am interested in this opportunity and would like to discuss further.', '2024-12-11 15:43:59', 0, 0, 0),
(44, 7, 7, 'Applied for: AI for Finance\n\nI am interested in this opportunity and would like to discuss further.', '2024-12-11 15:44:34', 1, 0, 0),
(45, 7, 5, 'Applied for: Explainable AI\n\nI am interested in this opportunity and would like to discuss further.', '2024-12-11 15:50:25', 1, 0, 0),
(46, 7, 20, 'Applied for: Dojo System\n\nI am interested in this opportunity and would like to discuss further.', '2024-12-11 15:51:33', 1, 0, 0),
(47, 7, 20, 'Applied for: Dojo System\n\nI am interested in this opportunity and would like to discuss further.', '2024-12-11 15:52:02', 1, 0, 0),
(48, 7, 20, 'Applied for: Code Foundations\n\nI am interested in this opportunity and would like to discuss further.', '2024-12-11 15:52:46', 1, 0, 0),
(49, 5, 7, 'Seriously, You really applied for this position..?', '2024-12-11 19:58:50', 1, 0, 0),
(50, 20, 7, 'Could you share your Portfolio', '2024-12-11 20:01:42', 1, 0, 0),
(51, 12, 6, 'Applied for: High-Speed Networking Research\n\nI am interested in this opportunity and would like to discuss further.', '2024-12-11 21:52:58', 0, 0, 0),
(52, 12, 13, 'Applied for: Quantum Networks Research\n\nI am interested in this opportunity and would like to discuss further.', '2024-12-11 21:53:22', 0, 0, 0),
(53, 12, 13, 'Applied for: Quantum Computing for Encryption\n\nI am interested in this opportunity and would like to discuss further.', '2024-12-11 21:54:30', 0, 0, 0),
(54, 12, 13, 'Applied for: Quantum Computing for Encryption\n\nI am interested in this opportunity and would like to discuss further.', '2024-12-11 21:54:57', 0, 0, 0);

-- --------------------------------------------------------

--
-- Table structure for table `Organizations`
--

CREATE TABLE `Organizations` (
  `org_id` int NOT NULL,
  `org_name` varchar(255) COLLATE utf8mb4_0900_as_ci DEFAULT NULL,
  `org_logo` varchar(255) COLLATE utf8mb4_0900_as_ci DEFAULT NULL,
  `org_type` varchar(255) COLLATE utf8mb4_0900_as_ci DEFAULT NULL
) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_as_ci;

--
-- Dumping data for table `Organizations`
--

INSERT INTO `Organizations` (`org_id`, `org_name`, `org_logo`, `org_type`) VALUES
(1, 'KonnectR', 'http://www.w3.org/2000/svg', 'Company'),
(2, 'Harvard University', 'https://th.bing.com/th/id/OIP.0_Z5OHEvCUHr9LI8cXMd6wHaEK?w=297&h=180&c=7&r=0&o=5&dpr=1.3&pid=1.7', 'Educational'),
(3, 'Massachusetts Institute of Technology', 'https://brand.mit.edu/sites/default/files/styles/tile_narrow/public/2023-08/lockup-color-BG-black.png?itok=NUotKGft', 'Educational'),
(4, 'Stanford University', 'https://th.bing.com/th/id/OIP.HFrxL3N7MY_DljdJUU_55gHaEK?pid=ImgDet&w=206&h=115&c=7&dpr=1.3', 'Educational'),
(5, 'University of Oxford', 'https://th.bing.com/th/id/OIP.wJHrJp-gi2sND5m7MDL1EQAAAA?w=271&h=81&c=7&r=0&o=5&dpr=1.3&pid=1.7', 'Educational'),
(6, 'University of Cambridge', 'https://th.bing.com/th/id/OIP.5oKmIC-3a3EqID-xWKNR4gAAAA?w=176&h=180&c=7&r=0&o=5&dpr=1.3&pid=1.7', 'Educational'),
(7, 'Clarkson University', 'https://seeklogo.com/images/C/clarkson-university-logo-4852150294-seeklogo.com.png', 'Educational'),
(8, 'ETH Zurich', 'https://designalltag.ch/wp-content/uploads/2023/01/Logo_UniversitaetZuerich.jpg', 'Educational'),
(9, 'National University of Singapore', 'https://th.bing.com/th/id/OIP.s34On_Mbvzgn6ErOXkedqQHaDa?w=343&h=161&c=7&r=0&o=5&dpr=1.3&pid=1.7', 'Educational'),
(10, 'Microsoft Corporation', 'https://th.bing.com/th/id/OIP.g-qzb46-Ic0JYI6nPZVSOgHaCu?w=317&h=128&c=7&r=0&o=5&dpr=1.3&pid=1.7', 'Company'),
(11, 'Apple Inc.', 'https://th.bing.com/th/id/OIP.-YzNxFgXai7xpeemFi5vvgHaEK?w=328&h=184&c=7&r=0&o=5&dpr=1.3&pid=1.7', 'Company'),
(12, 'Google LLC', 'https://th.bing.com/th/id/OIP.0reMc8zymWoDTY6UqiB4zwHaEK?w=287&h=180&c=7&r=0&o=5&dpr=1.3&pid=1.7', 'Company'),
(13, 'Amazon.com Inc.', 'https://th.bing.com/th?id=OIP.ArzNv7aQ_fdcIJhHBS_wrwHaGL&w=273&h=228&c=8&rs=1&qlt=90&o=6&pid=3.1&rm=2', 'Company'),
(14, 'Meta Platforms Inc.', 'https://imgs.search.brave.com/O0Ov_qFg-Ie-x5PiN4MGig2ssD2sZ-PFUboyJPb_GFs/rs:fit:500:0:0:0/g:ce/aHR0cHM6Ly9waG90/b3M1LmFwcGxlaW5z/aWRlci5jb20vZ2Fs/bGVyeS80NTMyOS04/ODIwOC1NZXRhLUxv/Z28teGwuanBn', 'Company'),
(15, 'Tesla Inc.', 'http://ts3.mm.bing.net/th?id=OIP.lwTEFjSYdwtxQzLAx6udFAHaFb&pid=15.1', 'Company'),
(16, 'IBM Corporation', 'https://upload.wikimedia.org/wikipedia/commons/5/51/IBM_logo.svg', 'Company'),
(17, 'Samsung Electronics', 'https://th.bing.com/th/id/OIP.2IJVjjyVwiAhX9kdn3ZinAAAAA?w=248&h=186&c=7&r=0&o=5&dpr=1.3&pid=1.7', 'Company'),
(18, 'Intel Corporation', 'https://th.bing.com/th/id/OIP.jo5dPgs47NBogIJiW78VkQHaE8?w=288&h=192&c=7&r=0&o=5&dpr=1.3&pid=1.7', 'Company'),
(19, 'NVIDIA Corporation', 'https://s3.amazonaws.com/cms.ipressroom.com/219/files/20237/64e3dc1a3d6332319b2dfd35_NVIDIA-logo-white-16x9/NVIDIA-logo-white-16x9_927581a6-fc31-4fa5-85c6-379680c6aa6c-prv.png', 'Company'),
(20, 'Adobe Systems', 'http://ts4.mm.bing.net/th?id=OIP.j3ilbLy4FDPhpJIbklIIFwAAAA&pid=15.1', 'Company'),
(21, 'University of California, Berkeley', 'https://th.bing.com/th/id/OIP.ae7R73uyWL-OnqeeS9iHSQHaEK?w=325&h=183&c=7&r=0&o=5&dpr=1.3&pid=1.7', 'Educational'),
(22, 'Carnegie Mellon University', 'https://th.bing.com/th?q=CMU+Carnegie+Mellon+Logo&w=120&h=120&c=1&rs=1&qlt=90&cb=1&dpr=1.3&pid=InlineBlock&mkt=en-US&cc=US&setlang=en&adlt=moderate&t=1&mw=247', 'Educational'),
(23, 'Princeton University', 'https://th.bing.com/th/id/OIP.Ue4nhfFXuxITAbLoTCjiPQHaEK?w=276&h=180&c=7&r=0&o=5&dpr=1.3&pid=1.7', 'Educational'),
(24, 'Yale University', 'https://th.bing.com/th/id/OIP.uOR9YcWf9LCaHGa3J1VzHgHaGB?w=218&h=180&c=7&r=0&o=5&dpr=1.3&pid=1.7', 'Educational'),
(25, 'Amazon Web Services', 'http://ts3.mm.bing.net/th?id=OIP.HJtSjMTb1gGA6stv-xaYNwHaEK&pid=15.1', 'Company'),
(26, 'Salesforce Inc.', 'https://th.bing.com/th/id/OIP.7wF76mX0WOm9KvCzd5JtGwHaEK?w=307&h=180&c=7&r=0&o=5&dpr=1.3&pid=1.7', 'Company'),
(27, 'Oracle Corporation', 'https://www.erpadvisorsgroup.com/hubfs/oraclesquare-1.png', 'Company'),
(28, 'X.com', 'https://media.sketchfab.com/models/8a66de89107f44e2a9524f38d9ed7110/thumbnails/3cdfc6de78e84022936d3af7127a4ecf/79590e616bd349f6b6ee0e19bda3f14e.jpeg', 'Company'),
(29, 'University of Toronto', 'https://th.bing.com/th/id/OIP.eUSMxgnZQjlqs6KPnmkbKgHaE8?w=242&h=180&c=7&r=0&o=5&dpr=1.3&pid=1.7', 'Educational'),
(30, 'McGill University', 'https://studyarchitecture.com/wp-content/uploads/mcgill-university-logo-png-transparent-cropped.png', 'Educational'),
(31, 'Purdue University', 'https://th.bing.com/th/id/OIP.O02U9zYhox6pbeCAG6z_9gHaBW?w=285&h=63&c=7&r=0&o=5&dpr=1.3&pid=1.7', 'Educational'),
(32, 'University of Chicago', 'https://heroesofadventure.com/wp-content/uploads/The-University-of-Chicago-logo.jpg', 'Educational'),
(33, 'Sony Corporation', 'https://is2-ssl.mzstatic.com/image/thumb/Purple126/v4/db/d6/33/dbd63376-f64c-62b3-df42-b0a5d3d433e1/AppIcon-1x_U007emarketing-0-7-0-0-sRGB-85-220.png/1200x630wa.png', 'Company'),
(34, 'LG Electronics', 'https://www.logolynx.com/images/logolynx/22/22355b4b924288202d32e10b85377001.jpeg', 'Company'),
(35, 'Dell Technologies', 'https://th.bing.com/th?q=Dell+Logo.png+HD&w=120&h=120&c=1&rs=1&qlt=90&cb=1&dpr=1.3&pid=InlineBlock&mkt=en-US&cc=US&setlang=en&adlt=moderate&t=1&mw=247', 'Company'),
(36, 'Cisco Systems', 'https://th.bing.com/th/id/OIP.yL7X8xEatDeJZ2bz2pgGBAHaHa?w=171&h=180&c=7&r=0&o=5&dpr=1.3&pid=1.7', 'Company'),
(37, 'HP Inc.', 'https://th.bing.com/th/id/OIP.CDeBA-YxU9lrTiY6v6UVPQHaHa?w=170&h=180&c=7&r=0&o=5&dpr=1.3&pid=1.7', 'Company'),
(38, 'Accenture', 'https://th.bing.com/th/id/OIP.qhAPWvYnIyuJMR-rdUWrJgHaEK?w=336&h=180&c=7&r=0&o=5&dpr=1.3&pid=1.7', 'Company'),
(39, 'Tata Consultancy Services', 'https://th.bing.com/th/id/OIP.ttCkj8l8aMSMG2bYt95oCgHaCD?w=337&h=96&c=7&r=0&o=5&dpr=1.3&pid=1.7', 'Company');

-- --------------------------------------------------------

--
-- Table structure for table `Password_requests`
--

CREATE TABLE `Password_requests` (
  `pass_id` int NOT NULL,
  `email` varchar(255) COLLATE utf8mb4_0900_as_ci NOT NULL,
  `status` enum('sent','pending') COLLATE utf8mb4_0900_as_ci NOT NULL DEFAULT 'pending',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `processed_at` datetime DEFAULT NULL,
  `processed_by` int DEFAULT NULL
) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_as_ci;

--
-- Dumping data for table `Password_requests`
--

INSERT INTO `Password_requests` (`pass_id`, `email`, `status`, `created_at`, `processed_at`, `processed_by`) VALUES
(1, 'paone@zurich.edu', 'sent', '2024-12-11 22:48:49', NULL, NULL),
(2, 'harithra@google.com', 'pending', '2024-12-11 22:51:33', NULL, NULL),
(3, 'vidhya@amazon.com', 'pending', '2024-12-11 22:53:38', NULL, NULL),
(4, 'prud.v@cat.com', 'pending', '2024-12-11 22:57:54', NULL, NULL),
(5, 'paone@zurich.edu', 'pending', '2024-12-11 23:00:17', NULL, NULL);

-- --------------------------------------------------------

--
-- Table structure for table `Posts`
--

CREATE TABLE `Posts` (
  `post_id` int NOT NULL,
  `user_id` int DEFAULT NULL,
  `title` varchar(255) COLLATE utf8mb4_0900_as_ci DEFAULT NULL,
  `description` text COLLATE utf8mb4_0900_as_ci,
  `post_type` varchar(255) COLLATE utf8mb4_0900_as_ci DEFAULT NULL,
  `post_created_at` timestamp NULL DEFAULT NULL,
  `status` varchar(255) COLLATE utf8mb4_0900_as_ci DEFAULT NULL,
  `field_of_interest` varchar(255) COLLATE utf8mb4_0900_as_ci DEFAULT NULL,
  `source_url` varchar(255) COLLATE utf8mb4_0900_as_ci DEFAULT NULL,
  `deleted` tinyint(1) DEFAULT '0'
) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_as_ci;

--
-- Dumping data for table `Posts`
--

INSERT INTO `Posts` (`post_id`, `user_id`, `title`, `description`, `post_type`, `post_created_at`, `status`, `field_of_interest`, `source_url`, `deleted`) VALUES
(1, 6, 'Research on Artificial General Intelligence', 'Exploring new advancements in AI and Machine Learning', 'Research', '2024-11-19 07:23:52', 'active', 'AI & ML', 'https://cloud.google.com/vertex-ai/docs/explainable-ai/overview?authuser=1#:~:text=Explainable%20AI%20is%20a%20set%20of%20tools%20and,with%20a%20number%20of%20Google%27s%20products%20and%20services.', 0),
(2, 7, 'Collaboration on developing an Ecommerce Recommendation System', 'We are looking for students with a passion for data science and Machine Learning to join our Project.', 'Project', '2024-11-19 08:11:59', 'active', 'AI & ML', 'https://www.amazon.jobs/content/en/teams/AGI', 0),
(3, 8, 'Research on Quantum Computing Opportunity', 'Looking for Researchers to explore the applications of quantum computing. Field of Interest: Quantum Computing.', 'Internship', '2024-11-19 08:16:30', 'active', 'Comp-Sci', 'https://cloud.google.com/vertex-ai/docs/explainable-ai/overview?authuser=1#:~:text=Explainable%20AI%20is%20a%20set%20of%20tools%20and,with%20a%20number%20of%20Google%27s%20products%20and%20services.', 0),
(4, 9, 'Research on Mixed Reality', 'Looking for Researchers to explore the applications of Mixed reality. Offers both  Internship and Full-time.  Field of Interest: Mixed reality', 'Full-time', '2024-11-19 08:21:12', 'active', 'Comp-Sci', 'https://cloud.google.com/vertex-ai/docs/explainable-ai/overview?authuser=1#:~:text=Explainable%20AI%20is%20a%20set%20of%20tools%20and,with%20a%20number%20of%20Google%27s%20products%20and%20services.', 0),
(5, 5, 'Research on ASI (Artificial Super Intelligence)', 'We are seeking a Research Intern to assist in the exploration of Artificial Superintelligence (ASI), focusing on its theoretical foundations, ethical implications, and potential societal impacts', 'Research', '2024-11-20 10:42:25', 'active', 'AI & ML', 'https://cloud.google.com/vertex-ai/docs/explainable-ai/overview?authuser=1#:~:text=Explainable%20AI%20is%20a%20set%20of%20tools%20and,with%20a%20number%20of%20Google%27s%20products%20and%20services.', 0),
(6, 5, 'Explainable AI', 'We are seeking researchers to develop techniques for making AI models more interpretable and understandable.', 'Research', '2024-11-24 01:30:48', 'active', 'AI & ML', 'https://cloud.google.com/vertex-ai/docs/explainable-ai/overview?authuser=1#:~:text=Explainable%20AI%20is%20a%20set%20of%20tools%20and,with%20a%20number%20of%20Google%27s%20products%20and%20services.', 0),
(7, 7, 'Neuro-Symbolic AI', 'We are seeking researchers to develop AI systems that combine the strengths of neural networks and symbolic reasoning.', 'Research', '2024-11-30 20:15:07', 'active', 'AI & ML', 'https://www.amazon.jobs/content/en/teams/AGI', 1),
(8, 7, 'AI for Finance', 'We are seeking researchers to develop AI-powered tools for financial analysis and decision-making.', 'Project', '2024-12-07 04:56:36', 'active', 'AI & ML', 'https://www.oracle.com/artificial-intelligence/', 0),
(9, 2, 'Neuro-Symbolic AI', 'We are seeking researchers to develop AI systems that combine the strengths of neural networks and symbolic reasoning.', 'Internship', '2024-12-07 05:01:14', 'active', 'AI & ML', 'https://www.amazon.com/alexa/research', 0),
(10, 2, 'Research on Human-AI Collaboration', 'We are seeking researchers to explore the potential benefits and challenges of human-AI collaboration.', 'Full-time', '2024-12-07 05:02:17', 'active', 'AI & ML', 'https://www.oracle.com/artificial-intelligence/', 0),
(11, 16, 'Mixed Reality Exploration: Glasswing', 'Adobe Research is pushing the boundaries with an early-stage mixed reality exploration called Project Glasswing.', 'Research', '2024-12-09 06:18:21', 'active', 'Virtual or Augmented Reality', 'https://research.adobe.com/research/ar-vr-360-photography/', 0),
(12, 20, 'Code Foundations', 'Throughput, latency, correctness and determinism are the main metrics we optimize our code for. Build the Autopilot software foundations up from the lowest levels of the stack, tightly integrating with our custom hardware.', 'Research', '2024-12-09 06:56:03', 'active', 'Electronics', 'https://www.tesla.com/AI', 0),
(13, 20, 'Dojo System', 'Design and build the Dojo system, from the silicon firmware interfaces to the high-level software APIs meant to control it.', 'Research', '2024-12-09 06:57:18', 'active', 'Electronics', 'https://www.tesla.com/AI', 0),
(15, 12, 'My First post', 'Just Saying hello to all', 'Research', '2024-12-11 20:59:41', 'active', 'Other', '', 0),
(14, 20, 'Hello World', 'Please, don\'t respond to this post', 'Project', '2024-12-09 08:55:05', 'active', 'Comp-Sci', '', 0),
(16, 21, 'IoT Security: Enhancing Protocols', 'A project focused on creating secure protocols for IoT devices.', 'Project', '2024-12-01 14:30:00', 'active', 'Cyber Security', NULL, 0),
(17, 24, 'Blockchain in Supply Chain', 'Developing blockchain-based solutions to improve traceability in supply chains.', 'Internship', '2024-12-02 10:15:45', 'active', 'Blockchain', 'https://blockchainjobs.com/internship', 0),
(18, 20, 'DevOps Specialist Full-Time Role', 'We are seeking candidates experienced in automation and CI/CD workflows.', 'Full-time', '2024-12-03 09:30:00', 'active', 'Cloud Computing', 'https://devopsjobs.com/fulltime', 0),
(19, 13, 'Quantum Computing for Encryption', 'Researching the applications of quantum algorithms to secure encryption systems.', 'Research', '2024-12-04 11:20:00', 'active', 'Computer Science', 'https://quantumresearch.org', 0),
(20, 25, '6G Networking Protocols', 'Creating innovative protocols to support the development of 6G networks.', 'Project', '2024-12-05 16:45:30', 'active', 'Networking', NULL, 0),
(21, 26, 'Cloud Infrastructure Developer', 'Hiring full-time cloud developers experienced in serverless architectures.', 'Full-time', '2024-12-06 12:00:00', 'active', 'IT', 'https://cloudcareers.com/fulltime', 0),
(22, 17, 'Human-Robot Collaboration', 'Exploring adaptive models for seamless human-robot interactions.', 'Research', '2024-12-07 09:15:30', 'active', 'Robotics', 'https://roboticslab.com/collaboration', 0),
(23, 19, 'Decentralized Finance and Blockchain', 'A student-led project exploring blockchain innovations in DeFi systems.', 'Project', '2024-12-08 14:20:15', 'active', 'Blockchain', NULL, 0),
(24, 24, 'ETL Pipeline Development Internship', 'Hands-on experience in developing scalable ETL pipelines.', 'Internship', '2024-12-09 13:00:00', 'active', 'Data Science', 'https://datainterns.com', 0),
(25, 6, 'High-Speed Networking Research', 'Analyzing performance improvements for high-speed data networks.', 'Research', '2024-12-10 10:00:00', 'active', 'Networking', 'https://networkresearch.com', 0),
(26, 8, 'Cyber Threat Analysis', 'An internship focused on analyzing and mitigating cyber threats.', 'Internship', '2024-12-01 09:10:00', 'active', 'Cyber Security', 'https://cyberjobs.com/internship', 0),
(27, 15, 'Blockchain and Smart Contracts', 'An in-depth research project on implementing smart contracts in blockchain.', 'Research', '2024-12-02 11:30:00', 'active', 'Blockchain', 'https://blockchainresearch.org', 0),
(28, 9, 'VR Immersive Learning', 'Developing VR-based learning modules for educational purposes.', 'Project', '2024-12-03 13:00:00', 'active', 'Virtual or Augmented Reality', NULL, 0),
(29, 7, 'Data Analytics for Financial Insights', 'An internship to uncover trends in financial data using advanced analytics.', 'Internship', '2024-12-04 14:45:15', 'active', 'Data Science', 'https://financejobs.com/internship', 0),
(30, 26, 'Cloud Security Specialist Role', 'Seeking candidates for full-time cloud security specialist positions.', 'Full-time', '2024-12-05 15:10:00', 'active', 'Cloud Computing', 'https://cloudsecurityjobs.com/fulltime', 0),
(31, 17, 'Assistive Robotics Research', 'Investigating the use of robotics in assistive technology for people with disabilities.', 'Research', '2024-12-06 11:30:00', 'active', 'Robotics', 'https://assistiverobotics.com/research', 0),
(32, 25, 'Penetration Testing Frameworks', 'Student-led project to design effective penetration testing tools.', 'Project', '2024-12-07 16:00:00', 'active', 'Cyber Security', NULL, 0),
(33, 18, 'AI in Supply Chain Management', 'Internship opportunity to explore AI-driven optimization in supply chain systems.', 'Internship', '2024-12-08 11:45:00', 'active', 'AI & ML', 'https://supplychaininterns.com', 0),
(34, 13, 'Quantum Networks Research', 'A research project on the implementation of quantum networking technologies.', 'Research', '2024-12-09 10:30:00', 'active', 'Networking', 'https://quantumnetworks.org', 0),
(35, 19, 'Digital Twin Technology', 'Collaborative project to simulate real-world environments using digital twins.', 'Project', '2024-12-10 12:15:00', 'active', 'IT', NULL, 0);

-- --------------------------------------------------------

--
-- Table structure for table `Post_Analytics`
--

CREATE TABLE `Post_Analytics` (
  `analytics_id` int NOT NULL,
  `post_id` int DEFAULT NULL,
  `view_count` int DEFAULT '0',
  `apply_count` int DEFAULT '0',
  `save_count` int DEFAULT '0',
  `field_of_interest` varchar(50) COLLATE utf8mb4_0900_as_ci DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_as_ci;

--
-- Dumping data for table `Post_Analytics`
--

INSERT INTO `Post_Analytics` (`analytics_id`, `post_id`, `view_count`, `apply_count`, `save_count`, `field_of_interest`, `created_at`) VALUES
(1, 7, 0, 0, 1, 'AI & ML', '2024-12-07 04:47:40'),
(2, 7, 0, 0, 1, 'AI & ML', '2024-12-07 04:47:42'),
(3, 5, 1, 0, 0, 'AI & ML', '2024-12-07 04:47:55'),
(4, 2, 1, 0, 0, 'AI & ML', '2024-12-07 04:48:20'),
(5, 13, 0, 0, 1, 'Electronics', '2024-12-09 07:42:32'),
(6, 12, 0, 0, 1, 'Electronics', '2024-12-09 07:42:33'),
(7, 13, 1, 0, 0, 'Electronics', '2024-12-11 15:18:24'),
(8, 13, 0, 1, 0, 'Electronics', '2024-12-11 15:43:28'),
(9, 11, 0, 1, 0, 'Virtual or Augmented Reality', '2024-12-11 15:43:59'),
(10, 8, 0, 1, 0, 'AI & ML', '2024-12-11 15:44:34'),
(11, 6, 0, 1, 0, 'AI & ML', '2024-12-11 15:50:25'),
(12, 13, 0, 1, 0, 'Electronics', '2024-12-11 15:51:33'),
(13, 13, 0, 1, 0, 'Electronics', '2024-12-11 15:52:02'),
(14, 12, 0, 1, 0, 'Electronics', '2024-12-11 15:52:46'),
(15, 9, 0, 0, 1, 'AI & ML', '2024-12-11 19:03:36'),
(16, 1, 0, 0, 1, 'AI & ML', '2024-12-11 19:03:47'),
(17, 5, 0, 0, 1, 'AI & ML', '2024-12-11 19:03:54'),
(18, 9, 0, 0, 1, 'AI & ML', '2024-12-11 19:33:21'),
(19, 12, 1, 0, 0, 'Electronics', '2024-12-11 20:15:02'),
(20, 25, 0, 1, 0, 'Networking', '2024-12-11 21:52:57'),
(21, 25, 0, 0, 1, 'Networking', '2024-12-11 21:53:04'),
(22, 34, 0, 0, 1, 'Networking', '2024-12-11 21:53:08'),
(23, 34, 0, 1, 0, 'Networking', '2024-12-11 21:53:22'),
(24, 20, 0, 0, 1, 'Networking', '2024-12-11 21:54:18'),
(25, 19, 0, 0, 1, 'Computer Science', '2024-12-11 21:54:29'),
(26, 19, 0, 1, 0, 'Computer Science', '2024-12-11 21:54:30'),
(27, 35, 0, 0, 1, 'IT', '2024-12-11 21:54:48'),
(28, 19, 0, 1, 0, 'Computer Science', '2024-12-11 21:54:57');

-- --------------------------------------------------------

--
-- Table structure for table `Post_Interactions`
--

CREATE TABLE `Post_Interactions` (
  `interaction_id` int NOT NULL,
  `user_id` int DEFAULT NULL,
  `post_id` int DEFAULT NULL,
  `interaction_type` enum('view','apply','save') COLLATE utf8mb4_0900_as_ci DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_as_ci;

--
-- Dumping data for table `Post_Interactions`
--

INSERT INTO `Post_Interactions` (`interaction_id`, `user_id`, `post_id`, `interaction_type`, `created_at`) VALUES
(1, 7, 7, 'save', '2024-12-07 04:47:40'),
(2, 7, 7, 'save', '2024-12-07 04:47:42'),
(3, 7, 5, 'view', '2024-12-07 04:47:55'),
(4, 7, 2, 'view', '2024-12-07 04:48:20'),
(5, 20, 13, 'save', '2024-12-09 07:42:32'),
(6, 20, 12, 'save', '2024-12-09 07:42:33'),
(7, 7, 13, 'view', '2024-12-11 15:18:24'),
(8, 7, 13, 'apply', '2024-12-11 15:43:28'),
(9, 7, 11, 'apply', '2024-12-11 15:43:59'),
(10, 7, 8, 'apply', '2024-12-11 15:44:34'),
(11, 7, 6, 'apply', '2024-12-11 15:50:25'),
(12, 7, 13, 'apply', '2024-12-11 15:51:33'),
(13, 7, 13, 'apply', '2024-12-11 15:52:02'),
(14, 7, 12, 'apply', '2024-12-11 15:52:46'),
(15, 7, 9, 'save', '2024-12-11 19:03:36'),
(16, 7, 1, 'save', '2024-12-11 19:03:47'),
(17, 7, 5, 'save', '2024-12-11 19:03:54'),
(18, 7, 9, 'save', '2024-12-11 19:33:21'),
(19, 20, 12, 'view', '2024-12-11 20:15:02'),
(20, 12, 25, 'apply', '2024-12-11 21:52:57'),
(21, 12, 25, 'save', '2024-12-11 21:53:04'),
(22, 12, 34, 'save', '2024-12-11 21:53:08'),
(23, 12, 34, 'apply', '2024-12-11 21:53:22'),
(24, 12, 20, 'save', '2024-12-11 21:54:18'),
(25, 12, 19, 'save', '2024-12-11 21:54:29'),
(26, 12, 19, 'apply', '2024-12-11 21:54:30'),
(27, 12, 35, 'save', '2024-12-11 21:54:48'),
(28, 12, 19, 'apply', '2024-12-11 21:54:57');

-- --------------------------------------------------------

--
-- Table structure for table `Saved_Posts`
--

CREATE TABLE `Saved_Posts` (
  `saved_id` int NOT NULL,
  `post_id` int NOT NULL,
  `user_id` int NOT NULL,
  `saved_at` datetime NOT NULL
) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_as_ci;

--
-- Dumping data for table `Saved_Posts`
--

INSERT INTO `Saved_Posts` (`saved_id`, `post_id`, `user_id`, `saved_at`) VALUES
(5, 5, 5, '2024-11-23 16:53:46'),
(3, 4, 5, '2024-11-22 20:43:36'),
(7, 3, 5, '2024-11-24 09:50:14'),
(8, 6, 5, '2024-11-24 09:50:24'),
(10, 7, 7, '2024-12-06 23:47:43'),
(11, 13, 20, '2024-12-09 02:42:31'),
(12, 12, 20, '2024-12-09 02:42:33'),
(16, 25, 12, '2024-12-11 16:53:05'),
(14, 1, 7, '2024-12-11 14:03:48'),
(15, 5, 7, '2024-12-11 14:03:55'),
(17, 34, 12, '2024-12-11 16:53:08'),
(18, 20, 12, '2024-12-11 16:54:18'),
(19, 19, 12, '2024-12-11 16:54:29'),
(20, 35, 12, '2024-12-11 16:54:49');

-- --------------------------------------------------------

--
-- Table structure for table `Users`
--

CREATE TABLE `Users` (
  `user_id` int NOT NULL,
  `username` varchar(249) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `email` varchar(255) COLLATE utf8mb4_0900_as_ci DEFAULT NULL,
  `hashed_password` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_as_ci DEFAULT NULL,
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `user_type` enum('Student','Professor','Company_recruiter','Admin') COLLATE utf8mb4_0900_as_ci DEFAULT NULL,
  `org_name` varchar(255) COLLATE utf8mb4_0900_as_ci DEFAULT NULL,
  `org_id` int DEFAULT NULL,
  `majors` varchar(255) COLLATE utf8mb4_0900_as_ci DEFAULT NULL,
  `level_of_study` varchar(255) COLLATE utf8mb4_0900_as_ci DEFAULT NULL,
  `deleted` tinyint(1) DEFAULT '0',
  `location` varchar(255) COLLATE utf8mb4_0900_as_ci DEFAULT NULL,
  `skills` text COLLATE utf8mb4_0900_as_ci,
  `experience` varchar(50) COLLATE utf8mb4_0900_as_ci DEFAULT NULL,
  `last_logout` datetime DEFAULT NULL,
  `last_login` datetime DEFAULT NULL,
  `login_count` int DEFAULT '0',
  `passphrase` varchar(20) COLLATE utf8mb4_0900_as_ci NOT NULL
) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_as_ci;

--
-- Dumping data for table `Users`
--

INSERT INTO `Users` (`user_id`, `username`, `email`, `hashed_password`, `created_at`, `user_type`, `org_name`, `org_id`, `majors`, `level_of_study`, `deleted`, `location`, `skills`, `experience`, `last_logout`, `last_login`, `login_count`, `passphrase`) VALUES
(1, 'SuperAdmin', 'superadmin01@konnectr.com', '8dd43ae0638e1ce2690e2e3cfa653923', NULL, 'Admin', 'KonnectR', 1, '', NULL, 0, NULL, NULL, NULL, '2024-12-12 04:29:12', '2024-12-12 04:26:14', 0, ''),
(2, 'Vidhya', 'vidhya@amazon.com', 'da5bcbfb2d26c8a150fe7c4eda941111', '2024-11-18 13:36:35', 'Company_recruiter', 'Amazon.com Inc.', 13, '', '', 0, NULL, NULL, NULL, '2024-12-11 14:20:25', '2024-12-11 14:17:41', 0, ''),
(3, 'Bhagi', 'bhagi@ms.com', '8dd43ae0638e1ce2690e2e3cfa653923', '2024-11-20 08:28:30', 'Student', 'Microsoft Corporation', 10, NULL, NULL, 0, NULL, NULL, NULL, NULL, NULL, 0, ''),
(4, 'Pavan Yellathakota', 'yelp@oxford.edu', '8dd43ae0638e1ce2690e2e3cfa653923', '2024-11-19 04:49:19', 'Student', 'University of Oxford', 5, NULL, NULL, 0, NULL, NULL, NULL, NULL, NULL, 0, ''),
(5, 'Harithra', 'harithra@google.com', '8dd43ae0638e1ce2690e2e3cfa653923', '2024-11-19 05:04:14', 'Company_recruiter', 'Google LLC', 12, NULL, NULL, 0, NULL, NULL, NULL, '2024-12-11 20:00:18', '2024-12-11 19:55:54', 0, ''),
(6, 'Tyler Conlon', 'tyler.c@clarkson.edu', '8dd43ae0638e1ce2690e2e3cfa653923', '2024-11-19 07:22:37', 'Professor', 'Clarkson University', 7, NULL, NULL, 0, NULL, NULL, NULL, NULL, NULL, 0, ''),
(7, 'Paone', 'paone@zurich.edu', '8dd43ae0638e1ce2690e2e3cfa653923', '2024-11-19 08:10:51', 'Student', 'ETH Zurich', 8, NULL, NULL, 0, NULL, NULL, NULL, '2024-12-12 04:22:40', '2024-12-12 04:08:44', 0, ''),
(8, 'Aravind Krishna', 'aravind.k@ibm.com', '8dd43ae0638e1ce2690e2e3cfa653923', '2024-11-19 08:14:26', 'Company_recruiter', 'IBM Corporation', 16, NULL, NULL, 0, NULL, NULL, NULL, NULL, NULL, 0, ''),
(9, 'MadV', 'mad.v@meta.com', '8dd43ae0638e1ce2690e2e3cfa653923', '2024-11-19 08:19:24', 'Company_recruiter', 'Meta Platforms Inc.', 14, NULL, NULL, 0, NULL, NULL, NULL, '2024-12-09 00:54:04', '2024-12-09 00:50:04', 0, ''),
(10, 'Skanda', 'skanda@stanford.edu', '8dd43ae0638e1ce2690e2e3cfa653923', '2024-11-20 10:49:30', 'Student', 'Stanford University', 4, NULL, NULL, 0, NULL, NULL, NULL, NULL, NULL, 0, ''),
(11, 'HeyU', 'hey@you.com', '8dd43ae0638e1ce2690e2e3cfa653923', '2024-11-25 11:09:57', 'Company_recruiter', 'Others', NULL, NULL, NULL, 0, NULL, NULL, NULL, NULL, NULL, 0, ''),
(12, 'Bill Gates', 'bill.g@microsoft.com', '8dd43ae0638e1ce2690e2e3cfa653923', '2024-11-18 14:01:25', 'Company_recruiter', 'Microsoft Corporation', 10, NULL, NULL, 0, NULL, NULL, NULL, '2024-12-11 21:55:16', '2024-12-11 20:57:14', 0, ''),
(13, 'Sarah Lee', 'sarah.lee@harvard.edu', '8dd43ae0638e1ce2690e2e3cfa653923', '2024-11-19 10:11:15', 'Professor', 'Harvard University', 2, NULL, NULL, 0, NULL, NULL, NULL, '2024-11-19 10:17:00', '2024-11-19 10:11:30', 0, ''),
(14, 'Mike Tanaka', 'mike.tanaka@sony.com', '8dd43ae0638e1ce2690e2e3cfa653923', '2024-11-20 09:25:10', 'Company_recruiter', 'Sony Corporation', 33, NULL, NULL, 0, NULL, NULL, NULL, '2024-11-20 09:30:20', '2024-11-20 09:25:30', 0, ''),
(15, 'Emily Wong', 'emily.wong@mit.edu', '8dd43ae0638e1ce2690e2e3cfa653923', '2024-11-21 08:55:05', 'Student', 'Massachusetts Institute of Technology', 3, NULL, NULL, 0, NULL, NULL, NULL, '2024-11-21 09:00:45', '2024-11-21 08:55:30', 0, ''),
(16, 'Daniel Smith', 'daniel.smith@adobe.com', '8dd43ae0638e1ce2690e2e3cfa653923', '2024-11-22 11:45:00', 'Company_recruiter', 'Adobe Systems', 20, NULL, NULL, 0, NULL, NULL, NULL, '2024-12-09 06:52:47', '2024-12-09 06:14:11', 0, ''),
(17, 'Laura Baker', 'laura.baker@berkeley.edu', '8dd43ae0638e1ce2690e2e3cfa653923', '2024-11-23 10:35:45', 'Professor', 'University of California, Berkeley', 21, NULL, NULL, 0, NULL, NULL, NULL, '2024-11-23 10:40:55', '2024-11-23 10:36:30', 0, ''),
(18, 'Tom Holland', 'tom.holland@intel.com', '8dd43ae0638e1ce2690e2e3cfa653923', '2024-11-24 15:30:15', 'Company_recruiter', 'Intel Corporation', 18, NULL, NULL, 0, NULL, NULL, NULL, '2024-11-24 15:36:00', '2024-11-24 15:31:30', 0, ''),
(19, 'Jessica Patel', 'jessica.patel@clarkson.edu', '8dd43ae0638e1ce2690e2e3cfa653923', '2024-11-25 12:20:50', 'Student', 'Clarkson University', 7, NULL, NULL, 0, NULL, NULL, NULL, '2024-11-25 12:26:10', '2024-11-25 12:21:30', 0, ''),
(20, 'Chris Johnson', 'chris.johnson@tesla.com', '8dd43ae0638e1ce2690e2e3cfa653923', '2024-11-26 14:40:35', 'Company_recruiter', 'Tesla Inc.', 15, NULL, NULL, 0, NULL, NULL, NULL, '2024-12-11 20:19:09', '2024-12-11 20:00:59', 0, ''),
(21, 'Anjali Sharma', 'anjali.sharma@cambridge.edu', '8dd43ae0638e1ce2690e2e3cfa653923', '2024-11-27 13:25:05', 'Student', 'University of Cambridge', 6, NULL, NULL, 0, NULL, NULL, NULL, '2024-11-27 13:30:55', '2024-11-27 13:25:30', 0, ''),
(22, 'Ryan Evans', 'ryan.evans@meta.com', '8dd43ae0638e1ce2690e2e3cfa653923', '2024-11-28 16:15:20', 'Company_recruiter', 'Meta Platforms Inc.', 14, NULL, NULL, 0, NULL, NULL, NULL, '2024-11-28 16:20:45', '2024-11-28 16:16:30', 0, ''),
(23, 'Lila Torres', 'lila.torres@stanford.edu', '8dd43ae0638e1ce2690e2e3cfa653923', '2024-11-29 09:50:00', 'Professor', 'Stanford University', 4, NULL, NULL, 0, NULL, NULL, NULL, '2024-11-29 09:56:20', '2024-11-29 09:51:30', 0, ''),
(24, 'Ahmed Khan', 'ahmed.khan@nvidia.com', '8dd43ae0638e1ce2690e2e3cfa653923', '2024-11-30 18:10:05', 'Company_recruiter', 'NVIDIA Corporation', 19, NULL, NULL, 0, NULL, NULL, NULL, '2024-11-30 18:15:55', '2024-11-30 18:10:30', 0, ''),
(25, 'Sophia Lee', 'sophia.lee@toronto.edu', '8dd43ae0638e1ce2690e2e3cfa653923', '2024-12-01 17:05:45', 'Student', 'University of Toronto', 29, NULL, NULL, 0, NULL, NULL, NULL, '2024-12-01 17:11:00', '2024-12-01 17:06:30', 0, ''),
(26, 'Vikram Menon', 'vikram.menon@tcs.com', '8dd43ae0638e1ce2690e2e3cfa653923', '2024-12-02 14:00:00', 'Company_recruiter', 'Tata Consultancy Services', 39, NULL, NULL, 0, NULL, NULL, NULL, '2024-12-02 14:05:55', '2024-12-02 14:01:30', 0, ''),
(27, 'Prudhvi Yellathakota', 'prud.v@cat.com', 'da5bcbfb2d26c8a150fe7c4eda941111', '2024-12-09 05:32:58', 'Company_recruiter', 'Others', NULL, NULL, NULL, 0, NULL, NULL, NULL, '2024-12-09 10:41:12', '2024-12-09 10:39:48', 0, ''),
(28, 'Admin02', 'admin02@konnectr.com', '8dd43ae0638e1ce2690e2e3cfa653923', '2024-12-11 15:33:13', 'Admin', 'KonnectR', NULL, NULL, NULL, 0, NULL, NULL, NULL, '2024-12-11 23:44:55', '2024-12-12 01:26:40', 0, '');

--
-- Triggers `Users`
--
DELIMITER $$
CREATE TRIGGER `after_last_login_update` AFTER UPDATE ON `Users` FOR EACH ROW BEGIN

    IF NEW.last_login IS NOT NULL AND NEW.last_login != OLD.last_login THEN
        INSERT INTO User_logs (user_id, action, timestamp)
        VALUES (NEW.user_id, 'login', NEW.last_login);
    END IF;
END
$$
DELIMITER ;
DELIMITER $$
CREATE TRIGGER `after_last_logout_update` AFTER UPDATE ON `Users` FOR EACH ROW BEGIN

    IF NEW.last_logout IS NOT NULL AND NEW.last_logout != OLD.last_logout THEN
        INSERT INTO User_logs (user_id, action, timestamp)
        VALUES (NEW.user_id, 'logout', NEW.last_logout);
    END IF;
END
$$
DELIMITER ;

--
-- Indexes for dumped tables
--

--
-- Indexes for table `Followers`
--
ALTER TABLE `Followers`
  ADD PRIMARY KEY (`follower_id`,`followed_id`),
  ADD KEY `idx_follower` (`follower_id`),
  ADD KEY `idx_followed` (`followed_id`);

--
-- Indexes for table `Messages`
--
ALTER TABLE `Messages`
  ADD PRIMARY KEY (`message_id`),
  ADD KEY `sender_id` (`sender_id`),
  ADD KEY `receiver_id` (`receiver_id`),
  ADD KEY `sent_at` (`sent_at`);

--
-- Indexes for table `Organizations`
--
ALTER TABLE `Organizations`
  ADD PRIMARY KEY (`org_id`);

--
-- Indexes for table `Password_requests`
--
ALTER TABLE `Password_requests`
  ADD PRIMARY KEY (`pass_id`);

--
-- Indexes for table `Posts`
--
ALTER TABLE `Posts`
  ADD PRIMARY KEY (`post_id`),
  ADD KEY `idx_posts_created` (`post_created_at`),
  ADD KEY `idx_post_created_at` (`post_created_at`);

--
-- Indexes for table `Post_Analytics`
--
ALTER TABLE `Post_Analytics`
  ADD PRIMARY KEY (`analytics_id`),
  ADD KEY `post_id` (`post_id`),
  ADD KEY `field_of_interest` (`field_of_interest`);

--
-- Indexes for table `Post_Interactions`
--
ALTER TABLE `Post_Interactions`
  ADD PRIMARY KEY (`interaction_id`),
  ADD KEY `user_id` (`user_id`),
  ADD KEY `post_id` (`post_id`),
  ADD KEY `interaction_type` (`interaction_type`);

--
-- Indexes for table `Saved_Posts`
--
ALTER TABLE `Saved_Posts`
  ADD PRIMARY KEY (`saved_id`),
  ADD UNIQUE KEY `unique_save` (`post_id`,`user_id`);

--
-- Indexes for table `Users`
--
ALTER TABLE `Users`
  ADD PRIMARY KEY (`user_id`),
  ADD UNIQUE KEY `idx_username` (`username`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `Messages`
--
ALTER TABLE `Messages`
  MODIFY `message_id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=55;

--
-- AUTO_INCREMENT for table `Organizations`
--
ALTER TABLE `Organizations`
  MODIFY `org_id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=40;

--
-- AUTO_INCREMENT for table `Password_requests`
--
ALTER TABLE `Password_requests`
  MODIFY `pass_id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;

--
-- AUTO_INCREMENT for table `Posts`
--
ALTER TABLE `Posts`
  MODIFY `post_id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=36;

--
-- AUTO_INCREMENT for table `Post_Analytics`
--
ALTER TABLE `Post_Analytics`
  MODIFY `analytics_id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=29;

--
-- AUTO_INCREMENT for table `Post_Interactions`
--
ALTER TABLE `Post_Interactions`
  MODIFY `interaction_id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=29;

--
-- AUTO_INCREMENT for table `Saved_Posts`
--
ALTER TABLE `Saved_Posts`
  MODIFY `saved_id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=21;

--
-- AUTO_INCREMENT for table `Users`
--
ALTER TABLE `Users`
  MODIFY `user_id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=29;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
