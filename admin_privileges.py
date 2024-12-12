#admin_privileges.py
from typing import Tuple
from baseObject import BaseObject
from datetime import datetime, timedelta
import pymysql, pymysql.cursors
import yaml

def load_config():
    """Load configuration from Config.yaml."""
    try:
        with open('Config.yaml', 'r') as file:
            config = yaml.safe_load(file)
        return config
    except FileNotFoundError:
        print("Config.yaml not found. Ensure the file exists in the working directory.")
        raise
    except yaml.YAMLError as e:
        print(f"Error reading Config.yaml: {e}")
        raise

class AdminPrivileges(BaseObject):
    """Class for Admin Privileges with database access."""
    def __init__(self):
        super().__init__()  # Ensure parent class initialization
        self.config = load_config()

    def get_db(self):
        """Establish and return a database connection."""
        try:
            db_config = self.config['db']
            conn = pymysql.connect(
                host=db_config['host'],
                user=db_config['user'],
                password=db_config['passwd'],
                database=db_config['db'],
                port=db_config['port'],
                cursorclass=pymysql.cursors.DictCursor  # Ensure DictCursor is used
            )
            return conn
        except pymysql.MySQLError as e:
            print(f"Database connection error: {e}")
            raise
    
    def validate_admin_session(self, session):
        """Validate that the current session is an admin session"""
        if not session.get('user_id') or session.get('user_type') != 'Admin':
            return False
        return True
    
    
    def reset_password(self, form_data):
        try:
            conn = self.get_db()
            with conn.cursor() as cursor:
                cursor.execute("SELECT email FROM Users WHERE email = %s", (form_data['email'],))
                user = cursor.fetchone()
                if user:
                    cursor.execute("INSERT INTO Password_requests (email, status) VALUES (%s, 'pending')", (form_data['email'],))
                    conn.commit()
                    return {'success': True, 'message': 'Password reset request has been stored.'}
                return {'success': False, 'message': 'Email not found.'}
        except pymysql.Error as e:
            return {'success': False, 'message': f"Database error: {str(e)}"}

    def get_password_reset_requests(self):
        try:
            conn = self.get_db()
            with conn.cursor() as cursor:
                cursor.execute("SELECT pass_id, email, status, created_at FROM Password_requests WHERE status = 'pending'")
                requests = cursor.fetchall()
                return requests
        except pymysql.Error as e:
            return {'success': False, 'message': f"Database error: {str(e)}"}


    # def get_password_reset_requests(self):
    #     try:
    #         conn = self.get_db() # Assuming `get_db()` gets the DB connection
    #         with conn.cursor() as cursor:
    #             cursor.execute("SELECT pass_id, email, status, created_at FROM Password_requests ORDER BY created_at DESC")
    #             requests = cursor.fetchall()
    #         conn.close()
    #         return requests
    #     except pymysql.MySQLError as e:
    #         return {'success': False, 'message': f"Error fetching password requests: {str(e)}"}

    def _hash_password(self, password: str) -> str:
        """Hash a password using MD5"""
        import hashlib
        return hashlib.md5(password.encode()).hexdigest()

    def handle_password_request(self, request_id: int, action: str) -> dict:
        """Handle password reset request approval/rejection"""
        try:
            conn = self.get_db()
            with conn.cursor() as cursor:
                # Get request details with user info
                cursor.execute("""
                    SELECT pr.*, u.user_id 
                    FROM Password_requests pr
                    JOIN Users u ON pr.email = u.email
                    WHERE pr.pass_id = %s AND pr.status = 'pending'
                """, (request_id,))
                request = cursor.fetchone()
                
                if not request:
                    return {
                        'success': False,
                        'message': 'Request not found or already processed'
                    }
                
                if action == 'approve':
                    # Generate a temporary password
                    temp_password = 'Konnectr@123'  # Should be randomly generated in production
                    
                    # Update user's password
                    cursor.execute("""
                        UPDATE Users 
                        SET hashed_password = %s
                        WHERE user_id = %s
                    """, (self._hash_password(temp_password), request['user_id']))
                    
                    # Update request status
                    cursor.execute("""
                        UPDATE Password_requests 
                        SET status = 'approved'
                        WHERE pass_id = %s
                    """, (request_id,))
                    
                    conn.commit()
                    return {
                        'success': True,
                        'message': f'Password reset approved. Temporary password: {temp_password}'
                    }
                
                elif action == 'reject':
                    cursor.execute("""
                        UPDATE Password_requests 
                        SET status = 'rejected'
                        WHERE pass_id = %s
                    """, (request_id,))
                    
                    conn.commit()
                    return {
                        'success': True,
                        'message': 'Password reset request rejected'
                    }
                
                return {
                    'success': False,
                    'message': 'Invalid action'
                }
                
        except Exception as e:
            print(f"Error in handle_password_request: {e}")
            return {
                'success': False,
                'message': f'Database error: {str(e)}'
            }
        finally:
            if conn:
                conn.close()

    # def handle_password_request(self, request_id: int, action: str) -> dict:
    #     """Handle password reset request approval/rejection"""
    #     try:
    #         conn = self.get_db()
    #         with conn.cursor() as cursor:
    #             # Get request details with user info
    #             cursor.execute("""
    #                 SELECT pr.*, u.user_id 
    #                 FROM Password_requests pr
    #                 JOIN Users u ON pr.email = u.email
    #                 WHERE pr.pass_id = %s AND pr.status = 'pending'
    #             """, (request_id,))
    #             request = cursor.fetchone()
                
    #             if not request:
    #                 return {
    #                     'success': False,
    #                     'message': 'Request not found or already processed'
    #                 }
                
    #             if action == 'approve':
    #                 # Generate a temporary password
    #                 temp_password = 'Konnectr@123'  # Should be randomly generated in production
                    
    #                 # Update user's password
    #                 cursor.execute("""
    #                     UPDATE Users 
    #                     SET hashed_password = %s
    #                     WHERE user_id = %s
    #                 """, (self._hash_password(temp_password), request['user_id']))
                    
    #                 # Update request status
    #                 cursor.execute("""
    #                     UPDATE Password_requests 
    #                     SET status = 'approved',
    #                         processed_at = NOW()
    #                     WHERE pass_id = %s
    #                 """, (request_id,))
                    
    #                 conn.commit()
    #                 return {
    #                     'success': True,
    #                     'message': f'Password reset approved. Temporary password: {temp_password}'
    #                 }
                
    #             elif action == 'reject':
    #                 cursor.execute("""
    #                     UPDATE Password_requests 
    #                     SET status = 'rejected',
    #                         processed_at = NOW()
    #                     WHERE pass_id = %s
    #                 """, (request_id,))
                    
    #                 conn.commit()
    #                 return {
    #                     'success': True,
    #                     'message': 'Password reset request rejected'
    #                 }
                
    #             return {
    #                 'success': False,
    #                 'message': 'Invalid action'
    #             }
                
    #     except Exception as e:
    #         print(f"Error in handle_password_request: {e}")
    #         return {
    #             'success': False,
    #             'message': f'Database error: {str(e)}'
    #         }
    #     finally:
    #         if conn:
    #             conn.close()
    

    # # Add this method to AdminPrivileges class
    # def handle_password_request(self, request_id: int, action: str) -> dict:
    #     """Handle password reset request approval/rejection"""
    #     try:
    #         conn = self.get_db()
    #         with conn.cursor() as cursor:
    #             # First verify request exists and is pending
    #             cursor.execute("""
    #                 SELECT * FROM Password_requests 
    #                 WHERE pass_id = %s AND status = 'pending'
    #             """, (request_id,))
    #             request = cursor.fetchone()
                
    #             if not request:
    #                 return {
    #                     'success': False,
    #                     'message': 'Request not found or already processed'
    #                 }
                
    #             new_status = 'approved' if action == 'approve' else 'rejected'
                
    #             # Update request status
    #             cursor.execute("""
    #                 UPDATE Password_requests 
    #                 SET status = %s, 
    #                     processed_at = NOW() 
    #                 WHERE pass_id = %s
    #             """, (new_status, request_id))
                
    #             conn.commit()
    #             return {
    #                 'success': True,
    #                 'message': f'Password reset request {new_status} successfully'
    #             }
                
    #     except pymysql.Error as e:
    #         print(f"Database error in handle_password_request: {e}")
    #         return {
    #             'success': False,
    #             'message': 'Database error occurred'
    #         }
    #     finally:
    #         if conn:
    #             conn.close()


    def get_field_analytics(self):
        """Get field interaction analytics"""
        try:
            conn = self.get_db()
            with conn.cursor() as cursor:
                # Get combined analytics for each field
                cursor.execute("""
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
                    ORDER BY p.field_of_interest
                """)
                field_stats = cursor.fetchall()

                return {
                    'success': True,
                    'field_stats': field_stats
                }
        except Exception as e:
            print(f"Error in get_field_analytics: {e}")
            return {
                'success': False,
                'error': str(e)
            }
        finally:
            if conn:
                conn.close()

    # def get_field_analytics(self):
    #     """Get field interaction analytics"""
    #     try:
    #         conn = self.get_db()
    #         with conn.cursor() as cursor:
    #             # Get field interactions
    #             cursor.execute("""
    #                 SELECT 
    #                     p.field_of_interest,
    #                     COUNT(DISTINCT pi.post_id) as total_posts,
    #                     SUM(CASE WHEN pi.interaction_type = 'apply' THEN 1 ELSE 0 END) as apply_count,
    #                     SUM(CASE WHEN pi.interaction_type = 'save' THEN 1 ELSE 0 END) as save_count,
    #                     SUM(CASE WHEN pi.interaction_type = 'view' THEN 1 ELSE 0 END) as view_count
    #                 FROM Posts p
    #                 LEFT JOIN Post_Interactions pi ON p.post_id = pi.post_id
    #                 WHERE p.deleted = 0
    #                 GROUP BY p.field_of_interest
    #                 ORDER BY apply_count DESC
    #             """)
    #             field_stats = cursor.fetchall()

    #             # Get additional analytics from Post_Analytics
    #             cursor.execute("""
    #                 SELECT 
    #                     field_of_interest,
    #                     SUM(view_count) as total_views,
    #                     SUM(apply_count) as total_applies,
    #                     SUM(save_count) as total_saves
    #                 FROM Post_Analytics
    #                 GROUP BY field_of_interest
    #             """)
    #             analytics_stats = cursor.fetchall()

    #             return {
    #                 'success': True,
    #                 'field_stats': field_stats,
    #                 'analytics_stats': analytics_stats
    #             }
    #     except Exception as e:
    #         print(f"Error getting field analytics: {e}")
    #         return {'success': False, 'error': str(e)}
    #     finally:
    #         if conn:
    #             conn.close()   

    def get_dashboard_analytics(self):
        try:
            conn = self.get_db()
            with conn.cursor() as cursor:
                # 1. Post Type Distribution
                cursor.execute("""
                    SELECT post_type, COUNT(*) as count
                    FROM Posts
                    WHERE deleted = 0
                    GROUP BY post_type
                """)
                post_types = cursor.fetchall()

                # 2. User Activity by Organization
                cursor.execute("""
                    SELECT o.org_name, COUNT(p.post_id) as post_count,
                           COUNT(DISTINCT u.user_id) as active_users
                    FROM Organizations o
                    JOIN Users u ON o.org_id = u.org_id
                    LEFT JOIN Posts p ON u.user_id = p.user_id
                    WHERE u.deleted = 0
                    GROUP BY o.org_name
                    ORDER BY post_count DESC
                    LIMIT 10
                """)
                org_activity = cursor.fetchall()

                # 3. Interaction Trends
                cursor.execute("""
                    SELECT 
                        DATE_FORMAT(pi.created_at, '%Y-%m-%d') as date,
                        pi.interaction_type,
                        COUNT(*) as count
                    FROM Post_Interactions pi
                    WHERE pi.created_at >= DATE_SUB(NOW(), INTERVAL 30 DAY)
                    GROUP BY date, interaction_type
                    ORDER BY date
                """)
                interaction_trends = cursor.fetchall()

                # 4. User Engagement Metrics
                cursor.execute("""
                    SELECT 
                        u.user_type,
                        COUNT(DISTINCT p.post_id) as posts_created,
                        COUNT(DISTINCT pi.interaction_id) as interactions_made,
                        COUNT(DISTINCT m.message_id) as messages_sent
                    FROM Users u
                    LEFT JOIN Posts p ON u.user_id = p.user_id
                    LEFT JOIN Post_Interactions pi ON u.user_id = pi.user_id
                    LEFT JOIN Messages m ON u.user_id = m.sender_id
                    WHERE u.deleted = 0
                    GROUP BY u.user_type
                """)
                user_engagement = cursor.fetchall()

                return {
                    'success': True,
                    'post_types': post_types,
                    'org_activity': org_activity,
                    'interaction_trends': interaction_trends,
                    'user_engagement': user_engagement
                }

        except Exception as e:
            print(f"Error getting dashboard analytics: {e}")
            return {'success': False, 'error': str(e)}
        finally:
            if conn:
                conn.close()    
    
    def get_dashboard_stats(self):
        try:
            conn = self.get_db()
            with conn.cursor() as cursor:
                # Get user statistics
                cursor.execute("""
                    SELECT 
                        COUNT(*) as total_users,
                        SUM(CASE WHEN created_at >= DATE_SUB(NOW(), INTERVAL 7 DAY) THEN 1 ELSE 0 END) as new_users,
                        SUM(CASE WHEN last_login >= DATE_SUB(NOW(), INTERVAL 24 HOUR) THEN 1 ELSE 0 END) as active_users
                    FROM Users
                    WHERE deleted = 0 AND user_type != 'Admin'
                """)
                user_stats = cursor.fetchone() or {'total_users': 0, 'new_users': 0, 'active_users': 0}

                # Get recent users
                cursor.execute("""
                    SELECT user_id, username, user_type, created_at
                    FROM Users
                    WHERE deleted = 0 AND user_type != 'Admin'
                    ORDER BY created_at DESC
                    LIMIT 5
                """)
                recent_users = cursor.fetchall() or []

                # Get post statistics
                cursor.execute("""
                    SELECT COUNT(*) as total_posts
                    FROM Posts
                    WHERE deleted = 0
                """)
                post_stats = cursor.fetchone() or {'total_posts': 0}

                # Get recent posts
                cursor.execute("""
                    SELECT p.*, u.username
                    FROM Posts p
                    JOIN Users u ON p.user_id = u.user_id
                    WHERE p.deleted = 0
                    ORDER BY p.post_created_at DESC
                    LIMIT 5
                """)
                recent_posts = cursor.fetchall() or []

                return {
                    'total_users': user_stats['total_users'],
                    'new_users': user_stats['new_users'],
                    'active_users': user_stats['active_users'],
                    'total_posts': post_stats['total_posts'],
                    'recent_users': recent_users,
                    'recent_posts': recent_posts
                }
        except pymysql.Error as e:
            print(f"Error getting dashboard stats: {e}")
            return None
        finally:
            if conn:
                conn.close()

    def get_all_users(self):
        try:
            conn = self.get_db()
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT u.*, o.org_name 
                    FROM Users u
                    LEFT JOIN Organizations o ON u.org_id = o.org_id
                    WHERE u.deleted = 0
                    ORDER BY u.created_at DESC
                """)
                users = cursor.fetchall()
                return users
        except pymysql.Error as e:
            print(f"Error fetching users: {e}")
            return None
        finally:
            if conn:
                conn.close()


    def get_user(self, user_id):
        try:
            conn = self.get_db()
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT * FROM Users 
                    WHERE user_id = %s AND user_type != 'Admin'
                """, (user_id,))
                return cursor.fetchone()
        except pymysql.Error as e:
            print(f"Error getting user: {e}")
            return None
        finally:
            if conn:
                conn.close()

    def update_user(self, user_id, data):
        try:
            conn = self.get_db()
            with conn.cursor() as cursor:
                cursor.execute("""
                    UPDATE Users 
                    SET username = %s, 
                        email = %s, 
                        user_type = %s
                    WHERE user_id = %s 
                    AND user_type != 'Admin'
                """, (data['username'], data['email'], data['user_type'], user_id))
                conn.commit()
                return True
        except pymysql.Error as e:
            print(f"Error updating user: {e}")
            return False
        finally:
            if conn:
                conn.close()

    def toggle_user_status(self, user_id):
        try:
            conn = self.get_db()
            with conn.cursor() as cursor:
                cursor.execute("""
                    UPDATE Users 
                    SET deleted = NOT deleted
                    WHERE user_id = %s 
                    AND user_type != 'Admin'
                """, (user_id,))
                conn.commit()
                return True
        except pymysql.Error as e:
            print(f"Error toggling user status: {e}")
            return False
        finally:
            if conn:
                conn.close()

    def get_all_posts(self):
        try:
            conn = self.get_db()
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT p.*, u.username, o.org_name, o.org_logo
                    FROM Posts p
                    JOIN Users u ON p.user_id = u.user_id
                    LEFT JOIN Organizations o ON u.org_id = o.org_id
                    WHERE p.deleted = 0
                    ORDER BY p.post_created_at DESC
                """)
                posts = cursor.fetchall()
                return posts
        except pymysql.Error as e:
            print(f"Error fetching posts: {e}")
            return None
        finally:
            if conn:
                conn.close()

    def toggle_post_status(self, post_id):
        try:
            conn = self.get_db()
            with conn.cursor() as cursor:
                cursor.execute("""
                    UPDATE Posts 
                    SET deleted = NOT deleted
                    WHERE post_id = %s
                """, (post_id,))
                conn.commit()
                return True
        except pymysql.Error as e:
            print(f"Error toggling post status: {e}")
            return False
        finally:
            if conn:
                conn.close()

    def get_analytics_data(self):
        try:
            conn = self.get_db()
            with conn.cursor() as cursor:
                analytics = {}
                
                # User Growth Over Time
                cursor.execute("""
                    SELECT DATE_FORMAT(created_at, '%Y-%m') as month,
                        COUNT(*) as user_count
                    FROM Users
                    WHERE deleted = 0
                    GROUP BY month
                    ORDER BY month
                    LIMIT 12
                """)
                analytics['user_growth'] = cursor.fetchall()
                
                # User Type Distribution
                cursor.execute("""
                    SELECT user_type, COUNT(*) as count
                    FROM Users
                    WHERE deleted = 0 AND user_type != 'Admin'
                    GROUP BY user_type
                """)
                analytics['user_type_distribution'] = cursor.fetchall()
                
                # Posts by Field
                cursor.execute("""
                    SELECT field_of_interest,
                        COUNT(*) as post_count,
                        SUM(CASE WHEN status = 'active' THEN 1 ELSE 0 END) as active_posts
                    FROM Posts
                    WHERE deleted = 0
                    GROUP BY field_of_interest
                """)
                analytics['posts_by_field'] = cursor.fetchall()
                
                # Post Interactions
                cursor.execute("""
                    SELECT pi.interaction_type,
                        COUNT(*) as count
                    FROM Post_Interactions pi
                    JOIN Posts p ON pi.post_id = p.post_id
                    WHERE p.deleted = 0
                    GROUP BY pi.interaction_type
                """)
                analytics['post_interactions'] = cursor.fetchall()
                
                # Monthly Engagement
                cursor.execute("""
                    SELECT 
                        DATE_FORMAT(created_at, '%Y-%m') as month,
                        COUNT(DISTINCT sender_id) as active_users,
                        COUNT(*) as message_count
                    FROM Messages
                    WHERE deleted = 0
                    GROUP BY month
                    ORDER BY month
                    LIMIT 12
                """)
                analytics['monthly_engagement'] = cursor.fetchall()
                
                return analytics
                
        except Exception as e:
            print(f"Error getting analytics data: {e}")
            return None
        finally:
            if conn:
                conn.close()

    def get_field_analytics(self):
        """Get analytics data for different fields of interest"""
        try:
            conn = self.get_db()
            with conn.cursor() as cursor:
                # Hot fields based on post count
                cursor.execute("""
                    SELECT field_of_interest, COUNT(*) as post_count
                    FROM Posts 
                    WHERE deleted = 0
                    GROUP BY field_of_interest 
                    ORDER BY post_count DESC
                """)
                hot_fields = cursor.fetchall()
                
                # Most saved posts by field
                cursor.execute("""
                    SELECT p.field_of_interest, COUNT(sp.saved_id) as save_count
                    FROM Posts p
                    JOIN Saved_Posts sp ON p.post_id = sp.post_id
                    WHERE p.deleted = 0
                    GROUP BY p.field_of_interest
                    ORDER BY save_count DESC
                """)
                saved_by_field = cursor.fetchall()
                
                # Most applied posts by field
                cursor.execute("""
                    SELECT p.field_of_interest, SUM(pa.apply_count) as apply_count
                    FROM Posts p
                    JOIN Post_Analytics pa ON p.post_id = pa.post_id
                    WHERE p.deleted = 0
                    GROUP BY p.field_of_interest
                    ORDER BY apply_count DESC
                """)
                applied_by_field = cursor.fetchall()
                
                return {
                    'success': True,
                    'hot_fields': hot_fields,
                    'saved_by_field': saved_by_field,
                    'applied_by_field': applied_by_field
                }
        except Exception as e:
            print(f"Error getting field analytics: {e}")
            return {'success': False, 'error': str(e)}
        finally:
            if conn:
                conn.close()

    def get_post_type_analytics(self):
        """Get analytics data for different post types"""
        try:
            conn = self.get_db()
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT post_type, COUNT(*) as count
                    FROM Posts
                    WHERE deleted = 0
                    GROUP BY post_type
                    ORDER BY count DESC
                """)
                post_types = cursor.fetchall()
                
                return {
                    'success': True,
                    'post_types': post_types
                }
        except Exception as e:
            print(f"Error getting post type analytics: {e}")
            return {'success': False, 'error': str(e)}
        finally:
            if conn:
                conn.close()

    def get_growth_analytics(self):
        """Get growth analytics data for users and posts"""
        try:
            conn = self.get_db()
            with conn.cursor() as cursor:
                # User growth over time
                cursor.execute("""
                    SELECT 
                        DATE_FORMAT(created_at, '%Y-%m') as month,
                        COUNT(*) as new_users
                    FROM Users
                    WHERE deleted = 0
                    GROUP BY month
                    ORDER BY month
                    LIMIT 12
                """)
                user_growth = cursor.fetchall()
                
                # Post growth over time
                cursor.execute("""
                    SELECT 
                        DATE_FORMAT(post_created_at, '%Y-%m') as month,
                        COUNT(*) as new_posts
                    FROM Posts
                    WHERE deleted = 0
                    GROUP BY month
                    ORDER BY month
                    LIMIT 12
                """)
                post_growth = cursor.fetchall()
                
                return {
                    'success': True,
                    'user_growth': user_growth,
                    'post_growth': post_growth
                }
        except Exception as e:
            print(f"Error getting growth analytics: {e}")
            return {'success': False, 'error': str(e)}
        finally:
            if conn:
                conn.close()

    def get_user_activity_analytics(self, period='daily'):
        """Get user activity analytics data"""
        try:
            conn = self.get_db()
            with conn.cursor() as cursor:
                date_format = {
                    'daily': '%Y-%m-%d',
                    'weekly': '%Y-%u',
                    'monthly': '%Y-%m',
                    'yearly': '%Y'
                }.get(period, '%Y-%m-%d')
                
                cursor.execute("""
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
                    LIMIT 12
                """, (date_format,))
                activity = cursor.fetchall()
                
                return {
                    'success': True,
                    'activity': activity
                }
        except Exception as e:
            print(f"Error getting user activity analytics: {e}")
            return {'success': False, 'error': str(e)}
        finally:
            if conn:
                conn.close()

    def get_user_type_analytics(self):
        """Get user statistics by user type"""
        try:
            conn = self.get_db()
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT 
                        user_type,
                        COUNT(*) as total_users,
                        SUM(CASE WHEN last_login >= DATE_SUB(NOW(), INTERVAL 30 DAY) THEN 1 ELSE 0 END) as active_users,
                        SUM(CASE WHEN created_at >= DATE_SUB(NOW(), INTERVAL 30 DAY) THEN 1 ELSE 0 END) as new_users,
                        AVG(login_count) as avg_logins
                    FROM Users
                    WHERE deleted = 0 AND user_type != 'Admin'
                    GROUP BY user_type
                """)
                user_stats = cursor.fetchall()
                
                return {
                    'success': True,
                    'user_stats': user_stats
                }
        except Exception as e:
            print(f"Error getting user type analytics: {e}")
            return {'success': False, 'error': str(e)}
        finally:
            if conn:
                conn.close()

# Add this method to the AdminPrivileges class:

    def get_field_interaction_stats(self):
        """Get field-wise interaction statistics"""
        try:
            conn = self.get_db()
            with conn.cursor() as cursor:
                # Get field-wise view statistics
                cursor.execute("""
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
                    ORDER BY total_applies DESC
                """)
                field_stats = cursor.fetchall()

                return {
                    'success': True,
                    'field_stats': field_stats
                }
        except Exception as e:
            print(f"Error getting field statistics: {e}")
            return {
                'success': False,
                'error': str(e)
            }
        finally:
            if conn:
                conn.close()
                
            
    # # Helper function to get user activity
    # def get_user_activity(self, user_id):
    #     try:
    #         conn = self.get_db()
    #         with conn.cursor() as cursor:
    #             cursor.execute("""
    #                 SELECT p.*, u.username
    #                 FROM Posts p
    #                 JOIN Users u ON p.user_id = u.user_id
    #                 WHERE p.user_id = %s
    #                 AND p.deleted = 0
    #                 ORDER BY p.post_created_at DESC
    #             """, (user_id,))
    #             posts = cursor.fetchall()

    #             cursor.execute("""
    #                 SELECT m.*, u.username as sender
    #                 FROM Messages m
    #                 JOIN Users u ON m.sender_id = u.user_id
    #                 WHERE m.receiver_id = %s
    #                 AND m.deleted = 0
    #                 ORDER BY m.created_at DESC
    #             """, (user_id,))
    #             messages = cursor.fetchall()

    #             return {
    #                 'posts': posts,
    #                 'messages': messages
    #             }
    #     except pymysql.Error as e:
    #         print(f"Error getting user activity: {e}")
    #         return None
    #     finally:
    #         if conn:
    #             conn.close()
    