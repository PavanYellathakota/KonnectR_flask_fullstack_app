# KonnectR - Academic & Professional Networking Platform

![KonnectR Logo](/img/konnectr_logo.png)

## Team Members
- Pavan Yellathakota - Developer

## Project Narrative
KonnectR is an innovative networking platform designed to bridge the gap between academia and industry. The platform facilitates meaningful connections between students, professors, and industry professionals, enabling collaboration on research projects, job opportunities, and knowledge sharing.

The application serves as a centralized hub where:
- Students can discover research opportunities and industry positions
- Professors can share research projects and find collaborators
- Industry professionals can post job opportunities and connect with talent
- Administrators can manage the platform and ensure quality interactions

## Primary Use Cases & User Roles

### User Roles Overview
![User Roles Diagram](/img/user_roles.png)

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

## Key SQL Queries

### Transactional Queries
1. Post Creation & Management
   - `create_post()` - Insert new posts
   - `update_post()` - Update existing posts
   - `toggle_post_status()` - Activate/deactivate posts

2. User Interactions
   - `handle_application()` - Process job applications
   - `toggle_follow()` - Manage user connections
   - `save_post()` - Save posts for later

### Analytical Queries
1. Dashboard Analytics
   - `get_field_analytics()` - Field-wise interaction analysis
   - `get_user_activity_analytics()` - User engagement metrics
   - `get_growth_analytics()` - Platform growth trends

2. User Analysis
   - `get_user_type_analytics()` - User type distribution
   - `get_post_interaction_stats()` - Post engagement metrics

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
- Password hashing (SHA-256)
- Session management
- CSRF protection
- Input validation
- XSS prevention

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
```

## License
This project is licensed under the MIT License.

## Contributing
Please read CONTRIBUTING.md for contribution guidelines.

## Acknowledgments
- Bootstrap for UI components
- Plotly.js for analytics visualization
- Flask community for excellent documentation