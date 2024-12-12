# KonnectR - Job Board and Networking Platform for R&D Enthusiasts


![KonnectR Logo](/img/KonnectR_logo.svg)

## Team Members
- Design & Developed by - PAVAN YELLATHAKOTA.

## Project Narrative
KonnectR is an innovative networking platform designed to bridge the gap between academia and industry. The platform facilitates meaningful connections between students, professors, and industry professionals, enabling collaboration on research projects, job opportunities, and knowledge sharing.

The application serves as a centralized hub where:
- Students can discover research opportunities and industry positions
- Professors can share research projects and find collaborators
- Industry professionals can post job opportunities and connect with talent
- Administrators can manage the platform and ensure quality interactions

## Primary Use Cases & User Roles

### User Roles Overview

1. **Students**
   - Search for research projects and job opportunities
   - Connect with professors and industry professionals
   - Apply for positions and save interesting posts
   - Participate in academic discussions

2. **Professors**
   - Post research opportunities
   - Connect with students and other professors
   - Share academic resources
   - Collaborate on research projects

3. **Company Recruiters**
   - Post job opportunities
   - Search for potential candidates
   - Connect with academic talent
   - View candidate profiles

4. **Admin**
   - Monitor platform activity
   - Manage user accounts
   - Handle password reset requests
   - View analytics and generate reports

## Database Design

### Relational Diagram
![Database Schema](/img/db_schema.png)

### Key Tables
- Users
- Posts
- Messages
- Organizations
- Post_Analytics
- Post_Interactions
- Password_requests
- Followers

## User Credentials

| Role               | Username                        | Password      | Access Level |
|--------------------|---------------------------------|---------------|--------------|
| Admin 1            | superadmin01@konnectr.com       | Qwerty@123    | Full         |
| Admin 1            | admin02@konnectr.com            | Qwerty@123    | Full         |
| Student            | paone@zurich.edu                | Qwerty@123    | Moderate     |
| Company Recruiter  | harithra@google.com             | Qwerty@123    | Moderate     |

# KonnectR Platform Overview :

KonnectR is a comprehensive platform designed for Research and Development enthusiasts across academic, professional, and startup ecosystems. It serves as both a job board and a networking platform.

## User and Admin Interfaces

### User Interface:
- **Post Management**: Users can create and manage their posts.
- **Networking**: Users can connect with other users, build their network, and engage in messaging to share thoughts.
- **Profile Management**: Users can update certain fields in their profiles to keep information current.

### Admin Interface:
- **Platform Monitoring**: The admin has full control over the platform, with the ability to monitor user and application traffic.
- **User and Post Management**: The admin can modify user statuses, manage post statistics, and oversee platform activities.
- **Data Insights**: The admin dashboard provides data insights, allowing the admin to observe trends and analyze platform metrics.

### Front-End:
- **HTML5**, **CSS**, and **Bootstrap**: Used for building an interactive, responsive UI.
- **JavaScript**: Adds interactivity and dynamic features to the platform.
- **Jinja Templates**: Used for rendering dynamic content with the Flask back-end.

### Back-End:
- **Python**: The core programming language powering the application.
- **Flask**: A lightweight web framework that helps manage the routing, user paths, and server-side logic.
- **MySQL (MyISAM)**: Chosen for data storage due to its efficiency in handling non-referential integrity relationships.

### Features:
- **User Sessions**: Maintains the user session across the platform until sign-out.
- **Encryption**: Utilizes the MD5 hashing algorithm to protect user passwords.
- **RESTful APIs**: Facilitates seamless data transfer across the platform with JSON format.

## Key SQL Queries
## Transactional Queries

### 1. Post Creation & Management
Users can effortlessly manage their posts on the platform. They have the ability to:
- Create new posts to showcase opportunities.
- Edit existing posts to keep content up-to-date.
- Delete posts that are no longer relevant.

This feature ensures that the platform remains dynamic and accurate.

![Creating new Posts](/img/create_post.png)

![Managing Posts](/img/manage_posts.png)

### 2. User Interactions
Users can interact with each other seamlessly through:
- **Asynchronous Chat:** Enabling users to connect and communicate throughout their sessions.
- **Search and Network Building:** Users can search for others on the platform and build their network by following peers, recruiters, and professors, fostering a collaborative environment.

![Messaging](/img/Chat1.png)

![Connections](/img/peers.png)

---

## Analytical Queries

### 1. Dashboard Analytics
Admins have access to a dedicated dashboard offering a comprehensive overview of platform performance. The dashboard includes:
- **Platform Statistics:** Total number of users and posts created.
- **Recent Activities:** Highlights of recently joined users and latest posts.
- **User Inflow Monitoring:** Tracks the number of new users joining daily, weekly, monthly, or yearly.
- **Post Analysis:** Displays the frequency of posts created over specific time periods.

![Application Statistics](/img/App_stats.png)

![Recent Activities on Application](/img/Recent_activity.png)

#### Example Queries:

- `get_field_analytics()` - Field-wise interaction analysis:

```sql
SELECT 
    p.field_of_interest,
    COUNT(DISTINCT p.post_id) as post_count,
    COALESCE(SUM(pa.apply_count), 0) as apply_count,
    COALESCE(SUM(pa.save_count), 0) as save_count,
    COALESCE(SUM(pa.view_count), 0) as view_count
FROM Posts p
LEFT JOIN Post_Analytics pa ON p.post_id = pa.post_id
WHERE p.deleted = 0
GROUP BY p.field_of_interest
ORDER BY p.field_of_interest;
```

- `get_user_activity_analytics()` - User engagement metrics:

```sql
SELECT 
    DATE_FORMAT(last_login, %s) as period,
    COUNT(DISTINCT user_id) as active_users,
    AVG(TIMESTAMPDIFF(MINUTE, last_login, last_logout)) as avg_session_duration
FROM Users
WHERE last_login IS NOT NULL 
AND last_logout IS NOT NULL
AND deleted = 0
GROUP BY period
ORDER BY period DESC
LIMIT 12;
```

- `get_growth_analytics()` - Platform growth trends:

```sql
SELECT 
    DATE_FORMAT(created_at, '%Y-%m') as month,
    COUNT(*) as new_users
FROM Users
WHERE deleted = 0
GROUP BY month
ORDER BY month
LIMIT 12;
```

### 2. User Analysis
Admins can analyze platform usage and user behavior through:
- **Active User Monitoring:** Review login and logout records to identify active users.
- **User Interest and Engagement:** Gain insights into the user types (students, professors, recruiters) who are most likely to join and actively engage with the platform.

![User Statistics](/img/User_stats.png)

![Active Users](/img/Active_users_stats.png)

#### Example Queries:

- `get_user_type_analytics()` - User type distribution:

```sql
SELECT 
    user_type,
    COUNT(*) as total_users,
    SUM(CASE WHEN last_login >= DATE_SUB(NOW(), INTERVAL 30 DAY) THEN 1 ELSE 0 END) as active_users,
    SUM(CASE WHEN created_at >= DATE_SUB(NOW(), INTERVAL 30 DAY) THEN 1 ELSE 0 END) as new_users,
    AVG(login_count) as avg_logins
FROM Users
WHERE deleted = 0 AND user_type != 'Admin'
GROUP BY user_type;
```

- `get_field_interaction_stats()` - Post engagement metrics:

```sql
SELECT 
    pa.field_of_interest,
    SUM(pa.view_count) as total_views,
    SUM(pa.apply_count) as total_applies,
    SUM(pa.save_count) as total_saves,
    COUNT(DISTINCT p.post_id) as post_count
FROM Post_Analytics pa
JOIN Posts p ON pa.post_id = p.post_id
WHERE p.deleted = 0
GROUP BY pa.field_of_interest
ORDER BY total_applies DESC;


## Tech Stack
- Backend: Python Flask
- Frontend: HTML, CSS, JavaScript, Bootstrap
- Database: MySQL
- Charts: Plotly.js
- Date Handling: Moment.js

## Platform Features
- Role-based access control
- Real-time messaging
- Advanced search and filtering
- Analytics dashboard
- Password reset management
- User profile management
- Post moderation system

## Security Features
- Password hashing (MD5)
- Session management
- Input validation

## Installation & Setup

1. Clone repository
```bash
git clone [repository-url]
cd KonnectR
```

2. Create virtual environment
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Configure database
```bash
# Update Config.yaml with your database credentials
mysql -u root -p < schema.sql
```

5. Run application
```bash
python app.py
```

## Project Structure
```
KONNECTR/
├── static/                  # Static assets
│   ├── CSS/                # Stylesheets
│   ├── JS/                 # JavaScript files
│   └── img/                # Images
├── templates/              # HTML templates
├── *.py                    # Python backend files
└── requirements.txt        # Dependencies

For the complete Flask project structure, refer to `KONNECTR.aurdino`

```

## License
This project is licensed under the MIT License.

## Contributing
Please read CONTRIBUTING.md for contribution guidelines.

## Acknowledgments
- Bootstrap for UI components
- Plotly.js for analytics visualization
- Flask community for excellent documentation


## Contact
- Email: pavanyellathakota@gmail.com
- GitHub: https://github.com/PavanYellathakota
- LinkedIn: https://www.linkedin.com/in/pavanyellathakota/