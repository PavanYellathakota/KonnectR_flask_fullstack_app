# services.py
import pymysql
from datetime import datetime, timedelta
from user import User
from flask import jsonify, request, session
import yaml

def load_config(config_file='Config.yaml'):
    """Load configuration from a YAML file."""
    try:
        with open(config_file, 'r') as file:
            config = yaml.safe_load(file)
        return config
    except FileNotFoundError:
        raise FileNotFoundError(f"{config_file} not found. Ensure the file exists in the working directory.")
    except yaml.YAMLError as e:
        raise ValueError(f"Error parsing {config_file}: {e}")

class BaseService:
    def __init__(self, config):
        """
        Initialize the base service with the configuration dictionary.
        Args:
            config (dict): Configuration dictionary containing database details.
        """
        if not isinstance(config, dict):
            raise TypeError("Configuration should be a dictionary.")
        self.config = config

    def get_db(self):
        """
        Establish a database connection using the configuration.
        Returns:
            pymysql.connections.Connection: The database connection object.
        """
        try:
            db_config = self.config.get('db')
            if not db_config:
                raise KeyError("Database configuration ('db') is missing in the config file.")
            
            connection = pymysql.connect(
                host=db_config['host'],
                user=db_config['user'],
                password=db_config['passwd'],
                database=db_config['db'],
                port=db_config['port'],
                cursorclass=pymysql.cursors.DictCursor
            )
            return connection
        except KeyError as e:
            raise KeyError(f"Missing database configuration key: {e}")
        except pymysql.MySQLError as e:
            raise ConnectionError(f"Failed to connect to the database: {e}")

class AuthService(BaseService):
    def register_user(self, form_data):
        try:
            if form_data['password'] != form_data['confirm_password']:
                return {'success': False, 'message': 'Passwords do not match'}
            
            existing_user = User.get_by_email(form_data['email'])
            if existing_user:
                return {'success': False, 'message': 'Email already registered'}
            user = User(
                username=form_data['fullname'],
                email=form_data['email'],
                password=form_data['password'],
                user_type=form_data['user_type']
            )
            user.save()
            return {'success': True}
        except pymysql.Error as e:
            return {'success': False, 'message': str(e)}

# Updated AuthServices to handle both user and admin logins
    def login_user(self, form_data):
        try:
            conn = self.get_db()
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT u.*, o.org_name 
                    FROM Users u 
                    LEFT JOIN Organizations o ON u.org_id = o.org_id 
                    WHERE u.email = %s AND u.deleted = 0
                """, (form_data['email'],))
                user = cursor.fetchone()
                
                if not user or User._hash_password(form_data['password']) != user['hashed_password']:
                    return {
                        'success': False,
                        'message': 'Invalid email or password'
                    }
                
                # Check user type - prevent admin login on user portal
                if form_data.get('required_type') == 'Admin':
                    if user['user_type'] != 'Admin':
                        return {
                            'success': False,
                            'message': 'Admin access required'
                        }
                else:  # Regular user login
                    if user['user_type'] == 'Admin':
                        return {
                            'success': False,
                            'message': 'Please use admin login portal'
                        }
                
                # Update last login
                cursor.execute("""
                    UPDATE Users 
                    SET last_login = NOW() 
                    WHERE user_id = %s
                """, (user['user_id'],))
                conn.commit()
                
                return {
                    'success': True,
                    'user_data': {
                        'user_id': user['user_id'],
                        'username': user['username'],
                        'email': user['email'],
                        'user_type': user['user_type'],
                        'org_name': user['org_name']
                    }
                }
                
        except pymysql.Error as e:
            print(f"Database error in login: {e}")
            return {
                'success': False,
                'message': 'Database error occurred'
            }
        finally:
            if conn:
                conn.close()


    def get_password_reset_requests(self):
        """Get all pending password reset requests"""
        try:
            conn = self.get_db()
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT pr.pass_id, pr.email, pr.status, pr.created_at,
                        u.user_id, u.username
                    FROM Password_requests pr
                    JOIN Users u ON pr.email = u.email
                    WHERE pr.status = 'pending'
                    ORDER BY pr.created_at DESC
                """)
                requests = cursor.fetchall()
                return requests
        except pymysql.Error as e:
            print(f"Error fetching password requests: {e}")
            return {'success': False, 'message': str(e)}
        finally:
            if conn:
                conn.close()

    def handle_password_request(self, request_id: int, action: str) -> dict:
        """Handle password reset request approval/rejection"""
        try:
            conn = self.get_db()
            with conn.cursor() as cursor:
                # Get request details
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
                    # Generate temporary password
                    temp_password = 'TempPass123!'  # In production, generate a secure random password
                    
                    # Update user's password
                    cursor.execute("""
                        UPDATE Users 
                        SET hashed_password = %s
                        WHERE user_id = %s
                    """, (self._hash_password(temp_password), request['user_id']))
                    
                    # Update request status
                    cursor.execute("""
                        UPDATE Password_requests 
                        SET status = 'approved', 
                            processed_at = NOW()
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
                        SET status = 'rejected',
                            processed_at = NOW()
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
                
        except pymysql.Error as e:
            print(f"Error handling password request: {e}")
            return {
                'success': False,
                'message': f'Database error: {str(e)}'
            }
        finally:
            if conn:
                conn.close()


    # def reset_password(self, form_data):
    #     try:
    #         conn = self.get_db()
    #         with conn.cursor() as cursor:
    #             cursor.execute("""
    #                 SELECT * FROM Users 
    #                 WHERE email = %s AND 
    #                 security_answer1 = %s AND 
    #                 security_answer2 = %s
    #             """, (form_data['email'], form_data['answer1'], form_data['answer2']))
                
    #             if cursor.fetchone():
    #                 cursor.execute("""
    #                     UPDATE Users 
    #                     SET hashed_password = %s 
    #                     WHERE email = %s
    #                 """, (User._hash_password(form_data['new_password']), form_data['email']))
    #                 conn.commit()
    #                 return {'success': True}
    #             return {'success': False, 'message': 'Invalid security answers'}
    #     except pymysql.Error as e:
    #         return {'success': False, 'message': str(e)}

# handle_logout method added to AuthService
    def handle_logout(self, user_id: int) -> bool:
        """Handle any cleanup needed on logout"""
        try:
            conn = self.get_db()
            with conn.cursor() as cursor:
                # Update last_logout timestamp
                cursor.execute("""
                    UPDATE Users 
                    SET last_logout = NOW()
                    WHERE user_id = %s
                """, (user_id,))
                conn.commit()
                return True
        except Exception as e:
            print(f"Error in handle_logout: {e}")
            return False
        finally:
            if conn:
                conn.close()

class UserService(BaseService):
    def get_profile_data(self, user_id):
        try:
            conn = self.get_db()
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT COUNT(*) as count
                    FROM Messages 
                    WHERE receiver_id = %s 
                    AND read_status = 0 
                    AND deleted = 0
                """, (user_id,))
                unread_count = cursor.fetchone()['count']
                cursor.execute("""
                    SELECT u.*, o.org_name 
                    FROM Users u
                    LEFT JOIN Organizations o ON u.org_id = o.org_id
                    WHERE u.user_id = %s
                """, (user_id,))
                user = cursor.fetchone()
                org_type = 'Educational' if user['user_type'] in ['Student', 'Professor'] else 'Company'
                cursor.execute("SELECT * FROM Organizations WHERE org_type = %s", (org_type,))
                organizations = cursor.fetchall()
                return {
                    'user': user,
                    'organizations': organizations,
                    'unread_count': unread_count
                }
        except pymysql.Error as e:
            return {'success': False, 'message': str(e)}

    def update_profile(self, user_id, form_data):
        try:
            conn = self.get_db()
            with conn.cursor() as cursor:
                update_query = "UPDATE Users SET username = %s, email = %s, org_id = %s"
                params = [form_data['username'], form_data['email'], form_data['org_id']]
                if form_data.get('new_password'):
                    update_query += ", hashed_password = %s"
                    params.append(User._hash_password(form_data['new_password']))
                update_query += " WHERE user_id = %s"
                params.append(user_id)
                cursor.execute(update_query, params)
                cursor.execute("SELECT org_name FROM Organizations WHERE org_id = %s", 
                             (form_data['org_id'],))
                org_result = cursor.fetchone()
                conn.commit()
                return {
                    'success': True,
                    'user_data': {
                        'username': form_data['username'],
                        'email': form_data['email'],
                        'org_name': org_result['org_name'] if org_result else None
                    }
                }
        except pymysql.Error as e:
            return {'success': False, 'message': str(e)}

    def delete_account(self, user_id):
        try:
            conn = self.get_db()
            with conn.cursor() as cursor:
                tables = ['Saved_Posts', 'Applications', 'Project_Members', 'Posts', 'Users']
                for table in tables:
                    cursor.execute(f"DELETE FROM {table} WHERE user_id = %s", (user_id,))
                conn.commit()
                return {'success': True, 'message': 'Account deleted successfully'}
        except pymysql.Error as e:
            return {'success': False, 'message': str(e)}


    def get_peers(self, user_id, filters):
        try:
            # Default values for pagination
            PER_PAGE_DEFAULT = 12
            PAGE_DEFAULT = 1

            conn = self.get_db()
            with conn.cursor() as cursor:
                # Get pagination parameters
                per_page = int(filters.get('per_page', PER_PAGE_DEFAULT))
                page = int(filters.get('page', PAGE_DEFAULT))

                # Base query for peers and organization join
                base_query = """
                    FROM Users u
                    LEFT JOIN Followers f ON u.user_id = f.followed_id AND f.follower_id = %s
                    LEFT JOIN Organizations o ON u.org_id = o.org_id
                    WHERE u.user_id != %s 
                    AND u.user_type != 'Admin'
                    AND u.deleted = 0
                """

                select_query = f"""
                    SELECT DISTINCT
                        u.user_id, 
                        u.username, 
                        u.user_type, 
                        u.org_name,
                        o.org_type,
                        o.org_logo,
                        CASE WHEN f.follower_id IS NOT NULL THEN 1 ELSE 0 END as is_following
                    {base_query}
                """

                count_query = f"SELECT COUNT(DISTINCT u.user_id) as total {base_query}"

                params = [user_id, user_id]
                count_params = [user_id, user_id]

                # Apply search filter
                if filters.get('search_query'):
                    search_clause = " AND (u.username LIKE %s OR COALESCE(u.org_name, '') LIKE %s)"
                    search_term = f"%{filters['search_query']}%"
                    select_query += search_clause
                    count_query += search_clause
                    params.extend([search_term, search_term])
                    count_params.extend([search_term, search_term])

                # Apply user type filter and corresponding org_type filter
                if filters.get('user_type'):
                    user_types = filters['user_type']
                    type_clause = " AND u.user_type IN ({})".format(','.join(['%s'] * len(user_types)))
                    select_query += type_clause
                    count_query += type_clause
                    params.extend(user_types)
                    count_params.extend(user_types)

                    # Combine org_type logic
                    educational_types = ['Student', 'Professor']
                    company_types = ['Company_recruiter']

                    if set(user_types) & set(educational_types) and 'Company_recruiter' in user_types:
                        org_type_clause = " AND (o.org_type = 'Educational' OR o.org_type = 'Company')"
                    elif set(user_types) == set(educational_types):
                        org_type_clause = " AND o.org_type = 'Educational'"
                    elif 'Company_recruiter' in user_types:
                        org_type_clause = " AND o.org_type = 'Company'"
                    else:
                        org_type_clause = ""

                    select_query += org_type_clause
                    count_query += org_type_clause

                # Apply organization filter
                if filters.get('org_id'):
                    org_clause = " AND u.org_id = %s"
                    select_query += org_clause
                    count_query += org_clause
                    params.append(filters['org_id'])
                    count_params.append(filters['org_id'])

                # Get total count for pagination
                cursor.execute(count_query, count_params)
                total_results = cursor.fetchone()['total']

                # Apply sorting
                if not filters.get('search_query') and not filters.get('user_type'):
                    select_query += " ORDER BY RAND()"
                else:
                    select_query += " ORDER BY u.username"

                # Apply pagination
                offset = (page - 1) * per_page
                select_query += " LIMIT %s OFFSET %s"
                params.extend([per_page, offset])

                # Execute final query
                cursor.execute(select_query, params)
                peers = cursor.fetchall()

                # Fetch organizations for filter options with logos
                cursor.execute("""
                    SELECT DISTINCT o.org_id, o.org_name, o.org_type, o.org_logo
                    FROM Organizations o
                    JOIN Users u ON u.org_id = o.org_id
                    WHERE u.deleted = 0 
                    ORDER BY o.org_name
                """)
                organizations = cursor.fetchall()

                return {
                    'success': True,
                    'peers': peers,
                    'organizations': organizations,
                    'total_results': total_results,
                    'pagination': {
                        'page': page,
                        'per_page': per_page,
                        'total': total_results,
                        'pages': (total_results + per_page - 1) // per_page
                    }
                }

        except Exception as e:
            print(f"Error in get_peers: {str(e)}")
            return {
                'success': False,
                'message': str(e),
                'peers': [],
                'organizations': [],
                'total_results': 0,
                'pagination': {'page': PAGE_DEFAULT, 'pages': 1, 'per_page': PER_PAGE_DEFAULT}
            }
        finally:
            if conn:
                conn.close()


    # def get_peers(self, user_id, filters):
    #     try:
    #         conn = self.get_db()
    #         with conn.cursor() as cursor:
    #             # Get pagination parameters
    #             per_page = int(filters.get('per_page', 12))
    #             page = int(filters.get('page', 1))

    #             # Base query with is_following status and organization join
    #             base_query = """
    #                 FROM Users u
    #                 LEFT JOIN Followers f ON u.user_id = f.followed_id AND f.follower_id = %s
    #                 LEFT JOIN Organizations o ON u.org_id = o.org_id
    #                 WHERE u.user_id != %s 
    #                 AND u.user_type != 'Admin'
    #                 AND u.deleted = 0
    #             """
                
    #             query = f"""
    #                 SELECT DISTINCT
    #                     u.user_id, 
    #                     u.username, 
    #                     u.user_type, 
    #                     u.org_name,
    #                     o.org_type,
    #                     CASE WHEN f.follower_id IS NOT NULL THEN 1 ELSE 0 END as is_following
    #                 {base_query}
    #             """
                
    #             count_query = f"SELECT COUNT(DISTINCT u.user_id) as total {base_query}"
                
    #             params = [user_id, user_id]
    #             count_params = [user_id, user_id]

    #             # Add search filter
    #             if filters.get('search_query'):
    #                 search_clause = " AND (u.username LIKE %s OR COALESCE(u.org_name, '') LIKE %s)"
    #                 query += search_clause
    #                 count_query += search_clause
    #                 search_term = f"%{filters['search_query']}%"
    #                 params.extend([search_term, search_term])
    #                 count_params.extend([search_term, search_term])

    #             # Add user type filter with corresponding org_type filter
    #             if filters.get('user_type'):
    #                 user_types = filters['user_type']
    #                 type_clause = " AND u.user_type IN ({})".format(','.join(['%s'] * len(user_types)))
    #                 query += type_clause
    #                 count_query += type_clause
    #                 params.extend(user_types)
    #                 count_params.extend(user_types)

    #                 # Handle combinations of user types
    #                 educational_types = ['Student', 'Professor']
    #                 company_types = ['Company_recruiter']

    #                 if set(user_types) & set(educational_types) and 'Company_recruiter' in user_types:
    #                     org_type_clause = " AND (o.org_type = 'Educational' OR o.org_type = 'Company')"
    #                 elif set(user_types) == set(educational_types):
    #                     org_type_clause = " AND o.org_type = 'Educational'"
    #                 elif 'Company_recruiter' in user_types:
    #                     org_type_clause = " AND o.org_type = 'Company'"
    #                 else:
    #                     org_type_clause = ""

    #                 query += org_type_clause
    #                 count_query += org_type_clause

    #             # Add organization filter
    #             if filters.get('org_id'):
    #                 org_clause = " AND u.org_id = %s"
    #                 query += org_clause
    #                 count_query += org_clause
    #                 params.append(filters['org_id'])
    #                 count_params.append(filters['org_id'])

    #             # Get total count
    #             cursor.execute(count_query, count_params)
    #             total_results = cursor.fetchone()['total']

    #             # Add sorting
    #             if not filters.get('search_query') and not filters.get('user_type'):
    #                 query += " ORDER BY RAND()"
    #             else:
    #                 query += " ORDER BY u.username"

    #             # Add pagination
    #             offset = (page - 1) * per_page
    #             query += " LIMIT %s OFFSET %s"
    #             params.extend([per_page, offset])

    #             # Execute final query
    #             cursor.execute(query, params)
    #             peers = cursor.fetchall()

    #             # Get organizations for filter
    #             cursor.execute("""
    #                 SELECT DISTINCT o.org_id, o.org_name, o.org_type
    #                 FROM Organizations o
    #                 JOIN Users u ON u.org_id = o.org_id
    #                 WHERE u.deleted = 0 
    #                 ORDER BY o.org_name
    #             """)
    #             organizations = cursor.fetchall()

    #             return {
    #                 'success': True,
    #                 'peers': peers,
    #                 'organizations': organizations,
    #                 'total_results': total_results,
    #                 'pagination': {
    #                     'page': page,
    #                     'per_page': per_page,
    #                     'total': total_results,
    #                     'pages': (total_results + per_page - 1) // per_page
    #                 }
    #             }

    #     except Exception as e:
    #         print(f"Error in get_peers: {str(e)}")
    #         return {
    #             'success': False,
    #             'message': str(e),
    #             'peers': [],
    #             'organizations': [],
    #             'total_results': 0,
    #             'pagination': {'page': 1, 'pages': 1, 'per_page': 12}
    #         }
    #     finally:
    #         if conn:
    #             conn.close()



    # def get_peers(self, user_id, filters):
    #     try:
    #         conn = self.get_db()
    #         with conn.cursor() as cursor:
    #             # Get pagination parameters
    #             per_page = int(filters.get('per_page', 12))
    #             page = int(filters.get('page', 1))

    #             # Base query with is_following status and organization join
    #             base_query = """
    #                 FROM Users u
    #                 LEFT JOIN Followers f ON u.user_id = f.followed_id AND f.follower_id = %s
    #                 LEFT JOIN Organizations o ON u.org_id = o.org_id
    #                 WHERE u.user_id != %s 
    #                 AND u.user_type != 'Admin'
    #                 AND u.deleted = 0
    #             """
                
    #             query = f"""
    #                 SELECT DISTINCT
    #                     u.user_id, 
    #                     u.username, 
    #                     u.user_type, 
    #                     u.org_name,
    #                     o.org_type,
    #                     CASE WHEN f.follower_id IS NOT NULL THEN 1 ELSE 0 END as is_following
    #                 {base_query}
    #             """
                
    #             count_query = f"SELECT COUNT(DISTINCT u.user_id) as total {base_query}"
                
    #             params = [user_id, user_id]
    #             count_params = [user_id, user_id]

    #             # Add search filter
    #             if filters.get('search_query'):
    #                 search_clause = " AND (u.username LIKE %s OR COALESCE(u.org_name, '') LIKE %s)"
    #                 query += search_clause
    #                 count_query += search_clause
    #                 search_term = f"%{filters['search_query']}%"
    #                 params.extend([search_term, search_term])
    #                 count_params.extend([search_term, search_term])

    #             # Add user type filter with corresponding org_type filter
    #             if filters.get('user_type'):
    #                 type_clause = " AND u.user_type IN ({})".format(','.join(['%s'] * len(filters['user_type'])))
    #                 query += type_clause
    #                 count_query += type_clause
    #                 params.extend(filters['user_type'])
    #                 count_params.extend(filters['user_type'])

    #                 # Add org_type filter based on user_type
    #                 educational_types = ['Student', 'Professor']
    #                 company_types = ['Company_recruiter']
    #                 user_types = filters['user_type']

    #                 org_type_conditions = []
    #                 if any(utype in educational_types for utype in user_types):
    #                     org_type_conditions.append("o.org_type = 'Educational'")
    #                 if any(utype in company_types for utype in user_types):
    #                     org_type_conditions.append("o.org_type = 'Company'")

    #                 if org_type_conditions:
    #                     org_type_clause = " AND (" + " OR ".join(org_type_conditions) + ")"
    #                     query += org_type_clause
    #                     count_query += org_type_clause

    #             # Add organization filter
    #             if filters.get('org_id'):
    #                 org_clause = " AND u.org_id = %s"
    #                 query += org_clause
    #                 count_query += org_clause
    #                 params.append(filters['org_id'])
    #                 count_params.append(filters['org_id'])

    #             # Get total count
    #             cursor.execute(count_query, count_params)
    #             total_results = cursor.fetchone()['total']

    #             # Add sorting
    #             if not filters.get('search_query') and not filters.get('user_type'):
    #                 query += " ORDER BY RAND()"
    #             else:
    #                 query += " ORDER BY u.username"

    #             # Add pagination
    #             offset = (page - 1) * per_page
    #             query += " LIMIT %s OFFSET %s"
    #             params.extend([per_page, offset])

    #             # Execute final query
    #             cursor.execute(query, params)
    #             peers = cursor.fetchall()

    #             # Get organizations for filter
    #             cursor.execute("""
    #                 SELECT DISTINCT o.org_id, o.org_name, o.org_type
    #                 FROM Organizations o
    #                 JOIN Users u ON u.org_id = o.org_id
    #                 WHERE u.deleted = 0 
    #                 ORDER BY o.org_name
    #             """)
    #             organizations = cursor.fetchall()

    #             return {
    #                 'success': True,
    #                 'peers': peers,
    #                 'organizations': organizations,
    #                 'total_results': total_results,
    #                 'pagination': {
    #                     'page': page,
    #                     'per_page': per_page,
    #                     'total': total_results,
    #                     'pages': (total_results + per_page - 1) // per_page
    #                 }
    #             }

    #     except Exception as e:
    #         print(f"Error in get_peers: {str(e)}")
    #         return {
    #             'success': False,
    #             'message': str(e),
    #             'peers': [],
    #             'organizations': [],
    #             'total_results': 0,
    #             'pagination': {'page': 1, 'pages': 1, 'per_page': 12}
    #         }
    #     finally:
    #         if conn:
    #             conn.close()


    # def get_peers(self, user_id, filters):
    #     try:
    #         conn = self.get_db()
    #         with conn.cursor() as cursor:
    #             # Get pagination parameters
    #             per_page = int(filters.get('per_page', 12))
    #             page = int(filters.get('page', 1))

    #             # Base query with is_following status and organization join
    #             base_query = """
    #                 FROM Users u
    #                 LEFT JOIN Followers f ON u.user_id = f.followed_id AND f.follower_id = %s
    #                 LEFT JOIN Organizations o ON u.org_id = o.org_id
    #                 WHERE u.user_id != %s 
    #                 AND u.user_type != 'Admin'
    #                 AND u.deleted = 0
    #             """
                
    #             query = f"""
    #                 SELECT DISTINCT
    #                     u.user_id, 
    #                     u.username, 
    #                     u.user_type, 
    #                     u.org_name,
    #                     o.org_type,
    #                     CASE WHEN f.follower_id IS NOT NULL THEN 1 ELSE 0 END as is_following
    #                 {base_query}
    #             """
                
    #             count_query = f"SELECT COUNT(DISTINCT u.user_id) as total {base_query}"
                
    #             params = [user_id, user_id]
    #             count_params = [user_id, user_id]

    #             # Add search filter
    #             if filters.get('search_query'):
    #                 search_clause = " AND (u.username LIKE %s OR COALESCE(u.org_name, '') LIKE %s)"
    #                 query += search_clause
    #                 count_query += search_clause
    #                 search_term = f"%{filters['search_query']}%"
    #                 params.extend([search_term, search_term])
    #                 count_params.extend([search_term, search_term])

    #             # Add user type filter with corresponding org_type filter
    #             if filters.get('user_type'):
    #                 type_clause = " AND u.user_type IN ({})".format(','.join(['%s'] * len(filters['user_type'])))
    #                 query += type_clause
    #                 count_query += type_clause
    #                 params.extend(filters['user_type'])
    #                 count_params.extend(filters['user_type'])

    #                 # Add org_type filter based on user_type
    #                 educational_types = ['Student', 'Professor']
    #                 company_types = ['Company_recruiter']
    #                 user_types = filters['user_type']

    #                 org_type_conditions = []
    #                 if any(utype in educational_types for utype in user_types):
    #                     org_type_conditions.append("o.org_type = 'Educational'")
    #                 if any(utype in company_types for utype in user_types):
    #                     org_type_conditions.append("o.org_type = 'Company'")

    #                 if org_type_conditions:
    #                     org_type_clause = " AND (" + " OR ".join(org_type_conditions) + ")"
    #                     query += org_type_clause
    #                     count_query += org_type_clause

    #             # Add organization filter
    #             if filters.get('org_id'):
    #                 org_clause = " AND u.org_id = %s"
    #                 query += org_clause
    #                 count_query += org_clause
    #                 params.append(filters['org_id'])
    #                 count_params.append(filters['org_id'])

    #             # Get total count
    #             cursor.execute(count_query, count_params)
    #             total_results = cursor.fetchone()['total']

    #             # Add sorting
    #             if filters.get('search_query'):
    #                 query += " ORDER BY u.username"
    #             else:
    #                 query += " ORDER BY RAND()"

    #             # Add pagination
    #             offset = (page - 1) * per_page
    #             query += " LIMIT %s OFFSET %s"
    #             params.extend([per_page, offset])

    #             # Execute final query
    #             cursor.execute(query, params)
    #             peers = cursor.fetchall()

    #             # Get organizations for filter
    #             cursor.execute("""
    #                 SELECT DISTINCT o.org_id, o.org_name, o.org_type
    #                 FROM Organizations o
    #                 JOIN Users u ON u.org_id = o.org_id
    #                 WHERE u.deleted = 0 
    #                 ORDER BY o.org_name
    #             """)
    #             organizations = cursor.fetchall()

    #             return {
    #                 'success': True,
    #                 'peers': peers,
    #                 'organizations': organizations,
    #                 'total_results': total_results,
    #                 'pagination': {
    #                     'page': page,
    #                     'per_page': per_page,
    #                     'total': total_results,
    #                     'pages': (total_results + per_page - 1) // per_page
    #                 }
    #             }

    #     except Exception as e:
    #         print(f"Error in get_peers: {str(e)}")
    #         return {
    #             'success': False,
    #             'message': str(e),
    #             'peers': [],
    #             'organizations': [],
    #             'total_results': 0,
    #             'pagination': {'page': 1, 'pages': 1, 'per_page': 12}
    #         }
    #     finally:
    #         if conn:
    #             conn.close()    

    # def get_peers(self, user_id, filters):
    #     try:
    #         conn = self.get_db()
    #         with conn.cursor() as cursor:
    #             # Get pagination parameters
    #             per_page = int(filters.get('per_page', 12))
    #             page = int(filters.get('page', 1))

    #             # Base query with is_following status
    #             base_query = """
    #                 FROM Users u
    #                 LEFT JOIN Followers f ON u.user_id = f.followed_id AND f.follower_id = %s
    #                 WHERE u.user_id != %s 
    #                 AND u.user_type != 'Admin'
    #                 AND u.deleted = 0
    #             """
                
    #             query = f"""
    #                 SELECT DISTINCT
    #                     u.user_id, 
    #                     u.username, 
    #                     u.user_type, 
    #                     u.org_name,
    #                     CASE WHEN f.follower_id IS NOT NULL THEN 1 ELSE 0 END as is_following
    #                 {base_query}
    #             """
                
    #             count_query = f"SELECT COUNT(DISTINCT u.user_id) as total {base_query}"
                
    #             params = [user_id, user_id]
    #             count_params = [user_id, user_id]

    #             # Add search filter
    #             if filters.get('search_query'):
    #                 search_clause = " AND (u.username LIKE %s OR COALESCE(u.org_name, '') LIKE %s)"
    #                 query += search_clause
    #                 count_query += search_clause
    #                 search_term = f"%{filters['search_query']}%"
    #                 params.extend([search_term, search_term])
    #                 count_params.extend([search_term, search_term])

    #             # Add user type filter
    #             if filters.get('user_type'):
    #                 type_clause = " AND u.user_type IN ({})".format(','.join(['%s'] * len(filters['user_type'])))
    #                 query += type_clause
    #                 count_query += type_clause
    #                 params.extend(filters['user_type'])
    #                 count_params.extend(filters['user_type'])

    #             # Add organization filter
    #             if filters.get('org_id'):
    #                 org_clause = " AND u.org_id = %s"
    #                 query += org_clause
    #                 count_query += org_clause
    #                 params.append(filters['org_id'])
    #                 count_params.append(filters['org_id'])

    #             # Get total count
    #             cursor.execute(count_query, count_params)
    #             total_results = cursor.fetchone()['total']

    #             # Add sorting
    #             if filters.get('search_query'):
    #                 query += " ORDER BY u.username"
    #             else:
    #                 # For initial display, show random users
    #                 query += " ORDER BY RAND()"

    #             # Add pagination
    #             offset = (page - 1) * per_page
    #             query += " LIMIT %s OFFSET %s"
    #             params.extend([per_page, offset])

    #             # Execute final query
    #             cursor.execute(query, params)
    #             peers = cursor.fetchall()

    #             # Get organizations for filter
    #             cursor.execute("""
    #                 SELECT DISTINCT o.org_id, o.org_name, o.org_type
    #                 FROM Organizations o
    #                 JOIN Users u ON u.org_id = o.org_id
    #                 WHERE u.deleted = 0 
    #                 ORDER BY o.org_name
    #             """)
    #             organizations = cursor.fetchall()

    #             return {
    #                 'success': True,
    #                 'peers': peers,
    #                 'organizations': organizations,
    #                 'total_results': total_results,
    #                 'pagination': {
    #                     'page': page,
    #                     'per_page': per_page,
    #                     'total': total_results,
    #                     'pages': (total_results + per_page - 1) // per_page
    #                 }
    #             }

    #     except Exception as e:
    #         print(f"Error in get_peers: {str(e)}")
    #         return {
    #             'success': False,
    #             'message': str(e),
    #             'peers': [],
    #             'organizations': [],
    #             'total_results': 0,
    #             'pagination': {'page': 1, 'pages': 1, 'per_page': 12}
    #         }
    #     finally:
    #         if conn:
    #             conn.close()

    def toggle_follow(self, follower_id, followed_id):
        try:
            conn = self.get_db()
            with conn.cursor() as cursor:
                # First check if the followed user exists and is not an admin
                cursor.execute("""
                    SELECT user_id FROM Users 
                    WHERE user_id = %s AND user_type != 'Admin'
                """, (followed_id,))
                if not cursor.fetchone():
                    return {'success': False, 'message': 'User not found'}
                # Check if already following
                cursor.execute("""
                    SELECT * FROM Followers 
                    WHERE follower_id = %s AND followed_id = %s
                """, (follower_id, followed_id))
                if cursor.fetchone():
                    # Unfollow
                    cursor.execute("""
                        DELETE FROM Followers 
                        WHERE follower_id = %s AND followed_id = %s
                    """, (follower_id, followed_id))
                    action = 'unfollowed'
                    message = 'Unfollowed successfully'
                else:
                    # Follow
                    cursor.execute("""
                        INSERT INTO Followers (follower_id, followed_id, followed_at)
                        VALUES (%s, %s, NOW())
                    """, (follower_id, followed_id))
                    action = 'followed'
                    message = 'Followed successfully'
                conn.commit()
                return {'success': True, 'message': message, 'action': action}       
        except pymysql.Error as e:
            print(f"Database error in toggle_follow: {e}")
            return {'success': False, 'message': 'Database error occurred'}
        finally:
            conn.close()

    
    # Add this method to your UserService class if you want search functionality
    def search_peers(self, user_id, query):
        try:
            conn = self.get_db()
            with conn.cursor() as cursor:
                search_term = f"%{query}%"
                cursor.execute("""
                    SELECT DISTINCT 
                        user_id, 
                        username,
                        user_type,
                        org_name
                    FROM Users
                    WHERE user_id != %s
                    AND (username LIKE %s OR org_name LIKE %s)
                    LIMIT 10
                """, (user_id, search_term, search_term))
                return cursor.fetchall()
        except pymysql.Error as e:
            print(f"Error in search_peers: {e}")
            return []
        finally:
            conn.close()


    def get_user_profile(self, username, current_user_id):
        try:
            conn = self.get_db()
            with conn.cursor() as cursor:
                # Get user details with following status
                cursor.execute("""
                    SELECT 
                        u.*,
                        o.org_name,
                        CASE WHEN f.follower_id IS NOT NULL THEN 1 ELSE 0 END as is_following
                    FROM Users u
                    LEFT JOIN Organizations o ON u.org_id = o.org_id
                    LEFT JOIN Followers f ON u.user_id = f.followed_id AND f.follower_id = %s
                    WHERE u.username = %s AND u.deleted = 0
                """, (current_user_id, username))
                
                user = cursor.fetchone()
                if not user:
                    return {'success': False, 'message': 'User not found'}

                # Get statistics
                cursor.execute("""
                    SELECT 
                        (SELECT COUNT(*) FROM Followers WHERE followed_id = %s) as followers_count,
                        (SELECT COUNT(*) FROM Followers WHERE follower_id = %s) as following_count,
                        (SELECT COUNT(*) FROM Posts WHERE user_id = %s AND deleted = 0) as posts_count
                    FROM dual
                """, (user['user_id'], user['user_id'], user['user_id']))
                
                stats = cursor.fetchone()

                return {
                    'success': True,
                    'user': user,
                    'stats': stats,
                    'is_following': bool(user['is_following'])
                }
        except Exception as e:
            print(f"Error in get_user_profile: {e}")
            return {'success': False, 'message': 'Error retrieving profile'}
        finally:
            if conn:
                conn.close()

class PostService(BaseService):
    def get_home_feed(self, user_id, args):
        """
        Get posts for home feed with optional filtering and sorting.
        Returns limited to 5 posts for home page.
        
        Args:
            user_id (int): Current user's ID
            args (dict): Query parameters for filtering and sorting
            
        Returns:
            tuple: (list of posts, unread message count)
        """
        conn = None
        try:
            conn = self.get_db()
            with conn.cursor() as cursor:
                # Get unread count
                cursor.execute("""
                    SELECT COUNT(*) as count
                    FROM Messages 
                    WHERE receiver_id = %s 
                    AND read_status = 0 
                    AND deleted = 0
                """, (user_id,))
                unread_count = cursor.fetchone()['count']

                # Get query parameters with defaults
                sort_order = args.get('sort', 'newer')
                posted_by = args.getlist('posted-by')
                fields = args.getlist('field')
                posted_time = args.get('posted-time', 'all')

                # Base query with JOIN optimizations
                query = """
                SELECT DISTINCT
                    p.post_id,
                    p.user_id,
                    p.title,
                    p.description,
                    p.post_type,
                    p.field_of_interest,
                    p.source_url,
                    p.post_created_at,
                    p.status,
                    u.username,
                    u.org_name,
                    o.org_logo,
                    CASE WHEN sp.post_id IS NOT NULL THEN 1 ELSE 0 END as is_saved
                FROM Posts p 
                INNER JOIN Users u ON p.user_id = u.user_id 
                LEFT JOIN Organizations o ON u.org_id = o.org_id 
                LEFT JOIN Saved_Posts sp ON p.post_id = sp.post_id AND sp.user_id = %s
                WHERE p.status = 'active' 
                AND u.deleted = 0
                """
                params = [user_id]

                # Add filters with parameter validation
                if posted_by:
                    valid_types = ['Student', 'Professor', 'Company']  # Valid user types
                    filtered_types = [t for t in posted_by if t in valid_types]
                    if filtered_types:
                        query += " AND u.user_type IN (%s)" % ','.join(['%s'] * len(filtered_types))
                        params.extend(filtered_types)

                if fields:
                    valid_fields = ['IT', 'Comp-Sci', 'Electronics', 'AI & ML', 'Data Science']
                    filtered_fields = [f for f in fields if f in valid_fields]
                    if filtered_fields:
                        query += " AND p.field_of_interest IN (%s)" % ','.join(['%s'] * len(filtered_fields))
                        params.extend(filtered_fields)

                if posted_time != 'all':
                    date_limits = {
                        'today': timedelta(days=1),
                        'week': timedelta(days=7),
                        'month': timedelta(days=30)
                    }
                    if posted_time in date_limits:
                        query += " AND p.post_created_at >= %s"
                        params.append(datetime.now() - date_limits[posted_time])

                # Add sorting with input validation
                query += " ORDER BY p.post_created_at"
                query += " DESC" if sort_order != 'older' else " ASC"

                # Add limit for home page
                query += " LIMIT 5"

                # Execute query with error handling
                try:
                    cursor.execute(query, params)
                    posts = cursor.fetchall()
                except pymysql.Error as e:
                    print(f"Query execution error: {e}")
                    print(f"Query was: {cursor._last_executed}")  # Debug the actual query
                    return [], unread_count

                # Format dates and ensure consistent output
                formatted_posts = []
                for post in posts:
                    try:
                        formatted_post = dict(post)  # Create a copy of the post
                        if formatted_post.get('post_created_at'):
                            formatted_post['formatted_date'] = formatted_post['post_created_at'].strftime('%Y-%m-%d %H:%M:%S')
                        
                        # Ensure all required fields exist
                        required_fields = ['post_id', 'title', 'description', 'post_type', 'username']
                        for field in required_fields:
                            if field not in formatted_post:
                                formatted_post[field] = None
                                
                        formatted_posts.append(formatted_post)
                    except Exception as e:
                        print(f"Error formatting post {post.get('post_id', 'unknown')}: {e}")
                        continue

                print(f"Successfully retrieved {len(formatted_posts)} posts with sort order: {sort_order}")
                return formatted_posts, unread_count

        except pymysql.Error as e:
            print(f"Database error in get_home_feed: {str(e)}")
            return [], 0
        except Exception as e:
            print(f"Unexpected error in get_home_feed: {str(e)}")
            return [], 0
        finally:
            if conn:
                try:
                    conn.close()
                except Exception as e:
                    print(f"Error closing database connection: {e}")

    def create_post(self, user_id, form_data):
        try:
            conn = self.get_db()
            with conn.cursor() as cursor:
                # Validate source URL if provided
                source_url = form_data.get('source_url', '').strip()
                if source_url and not source_url.startswith(('http://', 'https://')):
                    source_url = 'https://' + source_url

                cursor.execute("""
                    INSERT INTO Posts (
                        user_id, 
                        title, 
                        description, 
                        post_type, 
                        field_of_interest,
                        source_url, 
                        post_created_at, 
                        status
                    ) VALUES (%s, %s, %s, %s, %s, %s, NOW(), 'active')
                """, (
                    user_id,
                    form_data['title'].strip(),
                    form_data['description'].strip(),
                    form_data['post_type'],
                    form_data['field_of_interest'],
                    source_url
                ))
                conn.commit()
                return {'success': True}
        except Exception as e:
            print(f"Error creating post: {e}")
            return {'success': False, 'message': str(e)}
        finally:
            if conn:
                conn.close()

    def get_post(self, post_id):
        try:
            conn = self.get_db()
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT 
                        p.*, 
                        u.username, 
                        u.org_name, 
                        o.org_logo,
                        u.user_type as poster_type
                    FROM Posts p 
                    JOIN Users u ON p.user_id = u.user_id 
                    LEFT JOIN Organizations o ON u.org_id = o.org_id 
                    WHERE p.post_id = %s
                """, (post_id,))
                post = cursor.fetchone()
                
                if not post:
                    return {'success': False, 'message': 'Post not found'}

                # Format dates for display
                if post['post_created_at']:
                    post['post_created_at'] = post['post_created_at']
                
                return {'success': True, 'post': post}
        except pymysql.Error as e:
            print(f"Database error in get_post: {e}")
            return {'success': False, 'message': 'Error retrieving post'}
        finally:
            if conn:
                conn.close()

    def check_is_saved(self, user_id, post_id):
        """Check if a post is saved by the user"""
        try:
            conn = self.get_db()
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT COUNT(*) as count 
                    FROM Saved_Posts 
                    WHERE post_id = %s AND user_id = %s
                """, (post_id, user_id))
                result = cursor.fetchone()
                return bool(result['count']) if result else False
        except pymysql.Error as e:
            print(f"Error checking saved status: {e}")
            return False
        finally:
            if conn:
                conn.close()
                
    def handle_application(self, user_id, post_id):
        try:
            conn = self.get_db()
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT p.*, u.user_id as recruiter_id, u.username as recruiter_name,
                           p.title as post_title
                    FROM Posts p
                    JOIN Users u ON p.user_id = u.user_id
                    WHERE p.post_id = %s
                """, (post_id,))
                post = cursor.fetchone()
                if not post:
                    return {'success': False, 'message': 'Post not found'}, 404
                initial_message = f"Applied for: {post['post_title']}\n\nI am interested in this opportunity and would like to discuss further."
                cursor.execute("""
                    INSERT INTO Messages (sender_id, receiver_id, message_text, sent_at)
                    VALUES (%s, %s, %s, NOW())
                """, (user_id, post['recruiter_id'], initial_message))
                conn.commit()
                return {
                    'success': True,
                    'redirect_url': f"/chat/{post['recruiter_id']}"
                }
        except pymysql.Error as e:
            return {'success': False, 'message': str(e)}, 500

    def toggle_save(self, user_id, post_id):
        try:
            conn = self.get_db()
            with conn.cursor() as cursor:
                # Check if post exists
                cursor.execute("SELECT COUNT(*) as count FROM Posts WHERE post_id = %s", (post_id,))
                if cursor.fetchone()['count'] == 0:
                    return {'success': False, 'message': 'Post not found'}, 404
                # Check if already saved
                cursor.execute("""
                    SELECT saved_id FROM Saved_Posts 
                    WHERE post_id = %s AND user_id = %s
                """, (post_id, user_id))
                saved_post = cursor.fetchone()
                if saved_post:
                    # Remove from saved posts
                    cursor.execute("""
                        DELETE FROM Saved_Posts 
                        WHERE post_id = %s AND user_id = %s
                    """, (post_id, user_id))
                    action = 'unsaved'
                    message = 'Post unsaved'
                else:
                    # Save the post
                    try:
                        cursor.execute("""
                            INSERT INTO Saved_Posts (post_id, user_id, saved_at)
                            VALUES (%s, %s, %s)
                        """, (post_id, user_id, datetime.now()))
                        action = 'saved'
                        message = 'Post saved successfully'
                    except pymysql.err.IntegrityError:
                        return {'success': False, 'message': 'Post already saved'}, 400
                conn.commit()
                return {'success': True, 'message': message, 'action': action}
                
        except pymysql.Error as e:
            print(f"Error in toggle_save: {e}")
            return {'success': False, 'message': 'Database error occurred'}, 500
        finally:
            conn.close()
                        
    def get_saved_posts(self, user_id):
        try:
            conn = self.get_db()
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT 
                        p.*,
                        u.username,
                        u.org_name,
                        sp.saved_at,
                        CASE 
                            WHEN sp.post_id IS NOT NULL THEN 1 
                            ELSE 0 
                        END as is_saved
                    FROM Posts p
                    JOIN Saved_Posts sp ON p.post_id = sp.post_id
                    LEFT JOIN Users u ON p.user_id = u.user_id
                    WHERE sp.user_id = %s
                    ORDER BY sp.saved_at DESC
                """, (user_id,))
                saved_posts = cursor.fetchall()
                return saved_posts
        except pymysql.Error as e:
            print(f"Error retrieving saved posts: {e}")
            return []
        finally:
            conn.close()

    def get_is_saved(self, user_id, post_id):
        """Check if a post is saved by the user"""
        try:
            conn = self.get_db()
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT COUNT(*) as count 
                    FROM Saved_Posts 
                    WHERE post_id = %s AND user_id = %s
                """, (post_id, user_id))
                result = cursor.fetchone()
                return bool(result['count']) if result else False
        except pymysql.Error as e:
            print(f"Error checking saved status: {e}")
            return False
        finally:
            conn.close()

    def get_paginated_posts(self, user_id, page, per_page, args):
        """
        Get paginated posts with filtering, search, and interaction tracking.
        
        Args:
            user_id (int): Current user's ID
            page (int): Page number (1-based)
            per_page (int): Number of items per page
            args (dict): Query parameters for filtering, searching and sorting
            
        Returns:
            tuple: (list of posts, total number of posts)
        """
        conn = None
        try:
            conn = self.get_db()
            with conn.cursor() as cursor:
                # Get query parameters
                sort_order = args.get('sort', 'newer')
                posted_by = args.getlist('posted-by')
                search_query = args.get('search', '').strip()
                field = args.get('field')
                post_type = args.get('post_type')
                posted_time = args.get('posted-time', 'all')

                # Base query
                query = """
                SELECT DISTINCT
                    p.*, 
                    u.username, 
                    u.org_name, 
                    o.org_logo,
                    CASE WHEN sp.post_id IS NOT NULL THEN 1 ELSE 0 END as is_saved,
                    COALESCE(pa.view_count, 0) as view_count,
                    COALESCE(pa.apply_count, 0) as apply_count,
                    COALESCE(pa.save_count, 0) as save_count
                FROM Posts p 
                INNER JOIN Users u ON p.user_id = u.user_id 
                LEFT JOIN Organizations o ON u.org_id = o.org_id 
                LEFT JOIN Saved_Posts sp ON p.post_id = sp.post_id AND sp.user_id = %s
                LEFT JOIN Post_Analytics pa ON p.post_id = pa.post_id
                WHERE p.status = 'active' 
                AND p.deleted = 0
                AND u.deleted = 0
                """
                count_query = """
                SELECT COUNT(DISTINCT p.post_id) as total
                FROM Posts p 
                INNER JOIN Users u ON p.user_id = u.user_id 
                WHERE p.status = 'active' 
                AND p.deleted = 0
                AND u.deleted = 0
                """
                params = [user_id]
                count_params = []

                # Add search filter
                if search_query:
                    search_clause = """ AND (
                        p.title LIKE %s OR 
                        p.description LIKE %s OR 
                        p.field_of_interest LIKE %s OR
                        u.username LIKE %s OR
                        u.org_name LIKE %s
                    )"""
                    query += search_clause
                    count_query += search_clause
                    search_term = f"%{search_query}%"
                    params.extend([search_term] * 5)
                    count_params.extend([search_term] * 5)

                # Add field filter
                if field:
                    field_clause = " AND p.field_of_interest = %s"
                    query += field_clause
                    count_query += field_clause
                    params.append(field)
                    count_params.append(field)

                # Add post type filter
                if post_type:
                    type_clause = " AND p.post_type = %s"
                    query += type_clause
                    count_query += type_clause
                    params.append(post_type)
                    count_params.append(post_type)

                # Add user type filter
                if posted_by:
                    user_type_clause = " AND u.user_type IN (%s)" % ','.join(['%s'] * len(posted_by))
                    query += user_type_clause
                    count_query += user_type_clause
                    params.extend(posted_by)
                    count_params.extend(posted_by)

                # Add time filter
                if posted_time != 'all':
                    date_limits = {
                        'today': timedelta(days=1),
                        'week': timedelta(days=7),
                        'month': timedelta(days=30)
                    }
                    if posted_time in date_limits:
                        time_clause = " AND p.post_created_at >= %s"
                        query += time_clause
                        count_query += time_clause
                        params.append(datetime.now() - date_limits[posted_time])
                        count_params.append(datetime.now() - date_limits[posted_time])

                # Get total count first
                cursor.execute(count_query, count_params)
                total_posts = cursor.fetchone()['total']

                # Add sorting
                sort_options = {
                    'newer': "p.post_created_at DESC",
                    'older': "p.post_created_at ASC",
                    'most_viewed': "COALESCE(pa.view_count, 0) DESC, p.post_created_at DESC",
                    'most_applied': "COALESCE(pa.apply_count, 0) DESC, p.post_created_at DESC",
                    'most_saved': "COALESCE(pa.save_count, 0) DESC, p.post_created_at DESC"
                }
                query += f" ORDER BY {sort_options.get(sort_order, 'p.post_created_at DESC')}"

                # Add pagination
                offset = (page - 1) * per_page
                query += f" LIMIT {per_page} OFFSET {offset}"

                # Get posts
                cursor.execute(query, params)
                posts = cursor.fetchall()

                # Format dates and clean up data
                for post in posts:
                    if post.get('post_created_at'):
                        post['formatted_date'] = post['post_created_at'].strftime('%Y-%m-%d %H:%M:%S')
                    # Clean up analytics data
                    post['analytics'] = {
                        'views': post.pop('view_count', 0),
                        'applies': post.pop('apply_count', 0),
                        'saves': post.pop('save_count', 0)
                    }

                return posts, total_posts

        except pymysql.Error as e:
            print(f"Database error in get_paginated_posts: {e}")
            return [], 0
        except Exception as e:
            print(f"Unexpected error in get_paginated_posts: {e}")
            return [], 0
        finally:
            if conn:
                try:
                    conn.close()
                except Exception as e:
                    print(f"Error closing database connection: {e}")

    def track_interaction(self, user_id, post_id, interaction_type):
        """Track user interaction with a post (view, apply, or save)"""
        try:
            conn = self.get_db()
            with conn.cursor() as cursor:
                # Record in Post_Interactions table
                cursor.execute("""
                    INSERT INTO Post_Interactions 
                    (user_id, post_id, interaction_type, created_at)
                    VALUES (%s, %s, %s, NOW())
                """, (user_id, post_id, interaction_type))
                
                # Get field_of_interest for the post
                cursor.execute("""
                    SELECT field_of_interest FROM Posts 
                    WHERE post_id = %s
                """, (post_id,))
                post = cursor.fetchone()
                
                # Update or insert into Post_Analytics
                cursor.execute("""
                    INSERT INTO Post_Analytics 
                    (post_id, field_of_interest, view_count, apply_count, save_count, created_at)
                    VALUES (%s, %s, %s, %s, %s, NOW())
                    ON DUPLICATE KEY UPDATE
                    view_count = view_count + IF(%s = 'view', 1, 0),
                    apply_count = apply_count + IF(%s = 'apply', 1, 0),
                    save_count = save_count + IF(%s = 'save', 1, 0)
                """, (
                    post_id,
                    post['field_of_interest'],
                    1 if interaction_type == 'view' else 0,
                    1 if interaction_type == 'apply' else 0,
                    1 if interaction_type == 'save' else 0,
                    interaction_type,
                    interaction_type,
                    interaction_type
                ))
                
                conn.commit()
                return True
        except Exception as e:
            print(f"Error tracking interaction: {e}")
            return False
        finally:
            if conn:
                conn.close()
            
    # def track_post_interaction(self, post_id, interaction_type):
    #     """Track interaction with a post"""
    #     try:
    #         conn = self.get_db()
    #         with conn.cursor() as cursor:
    #             # Insert or update analytics
    #             cursor.execute("""
    #                 INSERT INTO Post_Analytics (post_id, view_count, apply_count, save_count)
    #                 VALUES (%s, %s, %s, %s)
    #                 ON DUPLICATE KEY UPDATE
    #                 view_count = view_count + %s,
    #                 apply_count = apply_count + %s,
    #                 save_count = save_count + %s
    #             """, (
    #                 post_id,
    #                 1 if interaction_type == 'view' else 0,
    #                 1 if interaction_type == 'apply' else 0,
    #                 1 if interaction_type == 'save' else 0,
    #                 1 if interaction_type == 'view' else 0,
    #                 1 if interaction_type == 'apply' else 0,
    #                 1 if interaction_type == 'save' else 0
    #             ))
    #             conn.commit()
    #     except Exception as e:
    #         print(f"Error tracking post interaction: {e}")
    #     finally:
    #         if conn:
    #             conn.close()

    def get_user_posts(self, user_id):
        try:
            conn = self.get_db()
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT 
                        p.*,
                        COALESCE(pa.view_count, 0) as views,
                        COALESCE(pa.apply_count, 0) as applies,
                        COALESCE(pa.save_count, 0) as saves
                    FROM Posts p
                    LEFT JOIN Post_Analytics pa ON p.post_id = pa.post_id
                    WHERE p.user_id = %s AND p.deleted = 0
                    ORDER BY p.post_created_at DESC
                """, (user_id,))
                posts = cursor.fetchall()
                
                # Format posts data
                formatted_posts = []
                for post in posts:
                    post_dict = dict(post)
                    post_dict['analytics'] = {
                        'views': post_dict.pop('views', 0),
                        'applies': post_dict.pop('applies', 0),
                        'saves': post_dict.pop('saves', 0)
                    }
                    formatted_posts.append(post_dict)

                return {
                    'success': True,
                    'posts': formatted_posts
                }
        except Exception as e:
            print(f"Error getting user posts: {e}")
            return {
                'success': False,
                'message': 'Error retrieving posts',
                'posts': []
            }
        finally:
            if conn:
                conn.close()
    # def get_user_posts(self, user_id):
    #     try:
    #         conn = self.get_db()
    #         with conn.cursor() as cursor:
    #             cursor.execute("""
    #                 SELECT p.*, u.username, u.org_name
    #                 FROM Posts p
    #                 JOIN Users u ON p.user_id = u.user_id
    #                 WHERE p.user_id = %s AND p.deleted = 0
    #                 ORDER BY p.post_created_at DESC
    #             """, (user_id,))
                
    #             posts = cursor.fetchall()
    #             return {'success': True, 'posts': posts}
    #     except Exception as e:
    #         print(f"Error in get_user_posts: {e}")
    #         return {'success': False, 'posts': []}
    #     finally:
    #         if conn:
    #             conn.close()

    def get_post_for_edit(self, post_id, user_id):
        try:
            conn = self.get_db()
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT * FROM Posts 
                    WHERE post_id = %s AND user_id = %s AND deleted = 0
                """, (post_id, user_id))
                post = cursor.fetchone()
                
                if not post:
                    return {
                        'success': False,
                        'message': 'Post not found or unauthorized'
                    }
                
                return {
                    'success': True,
                    'post': post
                }
        except Exception as e:
            print(f"Error getting post for edit: {e}")
            return {
                'success': False,
                'message': 'Error retrieving post'
            }
        finally:
            if conn:
                conn.close()


    def update_post(self, post_id, user_id, form_data):
        try:
            conn = self.get_db()
            with conn.cursor() as cursor:
                # Verify ownership
                cursor.execute("""
                    SELECT post_id FROM Posts 
                    WHERE post_id = %s AND user_id = %s AND deleted = 0
                """, (post_id, user_id))
                
                if not cursor.fetchone():
                    return {
                        'success': False,
                        'message': 'Post not found or unauthorized'
                    }
                
                # Update post
                cursor.execute("""
                    UPDATE Posts 
                    SET title = %s,
                        description = %s,
                        field_of_interest = %s,
                        source_url = %s
                    WHERE post_id = %s
                """, (
                    form_data['title'],
                    form_data['description'],
                    form_data['field_of_interest'],
                    form_data.get('source_url', ''),
                    post_id
                ))
                conn.commit()
                
                return {
                    'success': True,
                    'message': 'Post updated successfully'
                }
        except Exception as e:
            print(f"Error updating post: {e}")
            return {
                'success': False,
                'message': 'Error updating post'
            }
        finally:
            if conn:
                conn.close()

    def delete_post(self, post_id, user_id):
        try:
            conn = self.get_db()
            with conn.cursor() as cursor:
                # Verify ownership
                cursor.execute("""
                    SELECT post_id FROM Posts 
                    WHERE post_id = %s AND user_id = %s AND deleted = 0
                """, (post_id, user_id))
                
                if not cursor.fetchone():
                    return {
                        'success': False,
                        'message': 'Post not found or unauthorized'
                    }
                
                # Soft delete the post
                cursor.execute("""
                    UPDATE Posts 
                    SET deleted = 1
                    WHERE post_id = %s
                """, (post_id,))
                conn.commit()
                
                return {
                    'success': True,
                    'message': 'Post deleted successfully'
                }
        except Exception as e:
            print(f"Error deleting post: {e}")
            return {
                'success': False,
                'message': 'Error deleting post'
            }
        finally:
            if conn:
                conn.close()

    def toggle_post_status(self, post_id, user_id, new_status):
        try:
            conn = self.get_db()
            with conn.cursor() as cursor:
                # Verify ownership
                cursor.execute("""
                    SELECT post_id FROM Posts 
                    WHERE post_id = %s AND user_id = %s AND deleted = 0
                """, (post_id, user_id))
                
                if not cursor.fetchone():
                    return {
                        'success': False,
                        'message': 'Post not found or unauthorized'
                    }
                
                # Update status
                cursor.execute("""
                    UPDATE Posts 
                    SET status = %s
                    WHERE post_id = %s
                """, (new_status, post_id))
                conn.commit()
                
                return {
                    'success': True,
                    'message': 'Post status updated successfully'
                }
        except Exception as e:
            print(f"Error updating post status: {e}")
            return {
                'success': False,
                'message': 'Error updating post status'
            }
        finally:
            if conn:
                conn.close()

    def track_interaction(self, user_id, post_id, interaction_type):
        try:
            conn = self.get_db()
            with conn.cursor() as cursor:
                # Record interaction
                cursor.execute("""
                    INSERT INTO Post_Interactions 
                    (user_id, post_id, interaction_type) 
                    VALUES (%s, %s, %s)
                """, (user_id, post_id, interaction_type))
                
                # Get field_of_interest for the post
                cursor.execute("""
                    SELECT field_of_interest FROM Posts 
                    WHERE post_id = %s
                """, (post_id,))
                post = cursor.fetchone()
                
                # Update or insert analytics
                cursor.execute("""
                    INSERT INTO Post_Analytics 
                    (post_id, field_of_interest, view_count, apply_count, save_count)
                    VALUES (%s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                    view_count = view_count + IF(%s = 'view', 1, 0),
                    apply_count = apply_count + IF(%s = 'apply', 1, 0),
                    save_count = save_count + IF(%s = 'save', 1, 0)
                """, (
                    post_id, 
                    post['field_of_interest'],
                    1 if interaction_type == 'view' else 0,
                    1 if interaction_type == 'apply' else 0,
                    1 if interaction_type == 'save' else 0,
                    interaction_type,
                    interaction_type,
                    interaction_type
                ))
                
                conn.commit()
                return True
        except Exception as e:
            print(f"Error tracking interaction: {e}")
            return False
        finally:
            if conn:
                conn.close()

    def get_admin_analytics(self):
        try:
            conn = self.get_db()
            with conn.cursor() as cursor:
                analytics = {}
                
                # Most viewed posts
                cursor.execute("""
                    SELECT p.*, pa.view_count, u.username
                    FROM Posts p
                    JOIN Post_Analytics pa ON p.post_id = pa.post_id
                    JOIN Users u ON p.user_id = u.user_id
                    WHERE p.deleted = 0
                    ORDER BY pa.view_count DESC
                    LIMIT 10
                """)
                analytics['most_viewed'] = cursor.fetchall()
                
                # Most applied posts
                cursor.execute("""
                    SELECT p.*, pa.apply_count, u.username
                    FROM Posts p
                    JOIN Post_Analytics pa ON p.post_id = pa.post_id
                    JOIN Users u ON p.user_id = u.user_id
                    WHERE p.deleted = 0
                    ORDER BY pa.apply_count DESC
                    LIMIT 10
                """)
                analytics['most_applied'] = cursor.fetchall()
                
                # Most saved posts
                cursor.execute("""
                    SELECT p.*, pa.save_count, u.username
                    FROM Posts p
                    JOIN Post_Analytics pa ON p.post_id = pa.post_id
                    JOIN Users u ON p.user_id = u.user_id
                    WHERE p.deleted = 0
                    ORDER BY pa.save_count DESC
                    LIMIT 10
                """)
                analytics['most_saved'] = cursor.fetchall()
                
                # Field analytics
                cursor.execute("""
                    SELECT 
                        field_of_interest,
                        SUM(view_count) as total_views,
                        SUM(apply_count) as total_applies,
                        SUM(save_count) as total_saves,
                        COUNT(DISTINCT post_id) as post_count
                    FROM Post_Analytics
                    GROUP BY field_of_interest
                    ORDER BY total_views DESC
                """)
                analytics['field_analytics'] = cursor.fetchall()
                
                # Recent interactions
                cursor.execute("""
                    SELECT 
                        pi.*, 
                        u.username,
                        p.title as post_title
                    FROM Post_Interactions pi
                    JOIN Users u ON pi.user_id = u.user_id
                    JOIN Posts p ON pi.post_id = p.post_id
                    ORDER BY pi.created_at DESC
                    LIMIT 50
                """)
                analytics['recent_interactions'] = cursor.fetchall()
                
                return analytics
        except Exception as e:
            print(f"Error getting analytics: {e}")
            return None
        finally:
            if conn:
                conn.close()






class MessageService(BaseService):
    def get_conversations(self, user_id):
        """Gets list of conversations for a user"""
        try:
            conn = self.get_db()
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT COUNT(*) as count
                    FROM Messages 
                    WHERE receiver_id = %s 
                    AND read_status = 0 
                    AND deleted = 0
                """, (user_id,))
                total_unread = cursor.fetchone()['count']

                cursor.execute("""
                    SELECT DISTINCT 
                        u.user_id,
                        u.username,
                        u.org_name,
                        (SELECT message_text 
                         FROM Messages 
                         WHERE ((sender_id = u.user_id AND receiver_id = %s)
                            OR (sender_id = %s AND receiver_id = u.user_id))
                            AND deleted = 0
                         ORDER BY sent_at DESC LIMIT 1) as last_message,
                        (SELECT sent_at 
                         FROM Messages 
                         WHERE ((sender_id = u.user_id AND receiver_id = %s)
                            OR (sender_id = %s AND receiver_id = u.user_id))
                            AND deleted = 0
                         ORDER BY sent_at DESC LIMIT 1) as last_message_time,
                        (SELECT COUNT(*) 
                         FROM Messages 
                         WHERE sender_id = u.user_id 
                            AND receiver_id = %s 
                            AND read_status = 0
                            AND deleted = 0) as unread_count
                    FROM Users u
                    JOIN Messages m ON (u.user_id = m.sender_id OR u.user_id = m.receiver_id)
                    WHERE (m.sender_id = %s OR m.receiver_id = %s)
                        AND u.user_id != %s
                        AND u.deleted = 0 
                        AND m.deleted = 0
                    GROUP BY u.user_id
                    HAVING last_message IS NOT NULL
                    ORDER BY last_message_time DESC
                """, (user_id,) * 8)
                conversations = cursor.fetchall()
                return {
                    'conversations': conversations,
                    'unread_count': total_unread
                }
        except pymysql.Error as e:
            print(f"Error in get_conversations: {e}")
            return {'success': False, 'message': str(e)}
        finally:
            if conn:
                conn.close()

    def get_chat_data_by_username(self, user_id, username):
        """Gets chat history with a specific user"""
        try:
            conn = self.get_db()
            with conn.cursor() as cursor:
                # Get chat user details
                cursor.execute("""
                    SELECT user_id, username, org_name 
                    FROM Users 
                    WHERE username = %s AND deleted = 0
                """, (username,))
                other_user = cursor.fetchone()
                if not other_user:
                    #return {'success': False, 'message': 'User not found'}
                    return {'success': True, 'message': 'Message Sent'}
                
                other_user_id = other_user['user_id']

                # Get messages
                cursor.execute("""
                    SELECT m.*, u.username as sender_name
                    FROM Messages m
                    JOIN Users u ON m.sender_id = u.user_id
                    WHERE ((sender_id = %s AND receiver_id = %s)
                    OR (sender_id = %s AND receiver_id = %s))
                    AND m.deleted = 0 
                    AND u.deleted = 0
                    ORDER BY sent_at
                """, (user_id, other_user_id, other_user_id, user_id))
                messages = cursor.fetchall()
                
                # Mark messages as read
                cursor.execute("""
                    UPDATE Messages 
                    SET read_status = 1
                    WHERE sender_id = %s 
                    AND receiver_id = %s 
                    AND deleted = 0
                """, (other_user_id, user_id))
                
                conn.commit()
                
                # Get updated unread count
                cursor.execute("""
                    SELECT COUNT(*) as count
                    FROM Messages 
                    WHERE receiver_id = %s 
                    AND read_status = 0 
                    AND deleted = 0
                """, (user_id,))
                unread_count = cursor.fetchone()['count']
                
                return {
                    'success': True,
                    'messages': messages,
                    'chat_user': other_user,
                    'unread_count': unread_count
                }
        except pymysql.Error as e:
            print(f"Database error in get_chat_data: {e}")
            return {'success': False, 'message': str(e)}
        finally:
            if conn:
                conn.close()


    def send_message_by_username(self, sender_id, data):
        if not data.get('message') or not data.get('receiver_username'):
            return {'success': False, 'message': 'Invalid message data'}, 400
        try:
            conn = self.get_db()
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT user_id
                    FROM Users
                    WHERE username = %s AND deleted = 0
                """, (data['receiver_username'],))
                
                receiver = cursor.fetchone()
                if not receiver:
                    return {'success': False, 'message': 'Recipient not found'}, 404

                cursor.execute("""
                    INSERT INTO Messages 
                    (sender_id, receiver_id, message_text, sent_at, read_status, deleted)
                    VALUES (%s, %s, %s, NOW(), 0, 0)
                """, (sender_id, receiver['user_id'], data['message']))
                
                message_id = cursor.lastrowid
                
                cursor.execute("""
                    SELECT m.*, u.username as sender_name 
                    FROM Messages m
                    JOIN Users u ON m.sender_id = u.user_id
                    WHERE m.message_id = %s
                """, (message_id,))
                message = cursor.fetchone()
                message['sent_at'] = message['sent_at'].strftime('%Y-%m-%d %H:%M:%S')
                
                conn.commit()
                return {'success': True, 'data': message}
                
        except pymysql.Error as e:
            print(f"Database error: {e}")
            return {'success': False, 'message': str(e)}, 500
        finally:
            if conn:
                conn.close()


    def get_actual_unread_count(self, user_id):
        """Gets accurate unread message count"""
        try:
            conn = self.get_db()
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT COUNT(*) as count
                    FROM Messages m
                    JOIN Users u ON m.sender_id = u.user_id
                    WHERE m.receiver_id = %s 
                    AND m.read_status = 0 
                    AND m.deleted = 0
                    AND u.deleted = 0
                """, (user_id,))
                result = cursor.fetchone()
                return result['count'] if result else 0
        except pymysql.Error as e:
            print(f"Error getting unread count: {e}")
            return 0
        finally:
            if conn:
                conn.close()

    def mark_messages_as_read(self, user_id, other_user_id=None):
        """Marks messages as read"""
        try:
            conn = self.get_db()
            with conn.cursor() as cursor:
                query = """
                    UPDATE Messages 
                    SET read_status = 1
                    WHERE receiver_id = %s 
                    AND read_status = 0
                    AND deleted = 0
                """
                params = [user_id]
                
                if other_user_id:
                    query += " AND sender_id = %s"
                    params.append(other_user_id)
                    
                cursor.execute(query, params)
                conn.commit()
                return True
        except pymysql.Error as e:
            print(f"Error marking messages as read: {e}")
            return False
        finally:
            if conn:
                conn.close()

    # Add this method to MessageService class
    def get_new_messages(self, user_id, username, since=None):
        try:
            conn = self.get_db()
            with conn.cursor() as cursor:
                # Get other user's ID
                cursor.execute("""
                    SELECT user_id
                    FROM Users
                    WHERE username = %s AND deleted = 0
                """, (username,))
                other_user = cursor.fetchone()
                
                if not other_user:
                    return {'success': False, 'messages': []}
                    
                query = """
                    SELECT m.*, u.username as sender_name
                    FROM Messages m
                    JOIN Users u ON m.sender_id = u.user_id
                    WHERE ((m.sender_id = %s AND m.receiver_id = %s)
                        OR (m.sender_id = %s AND m.receiver_id = %s))
                    AND m.deleted = 0
                """
                params = [user_id, other_user['user_id'], other_user['user_id'], user_id]

                if since:
                    query += " AND m.sent_at > %s"
                    params.append(since)

                query += " ORDER BY m.sent_at"
                cursor.execute(query, params)
                messages = cursor.fetchall()

                # Format datetime for JSON
                for message in messages:
                    message['sent_at'] = message['sent_at'].strftime('%Y-%m-%d %H:%M:%S')

                return {
                    'success': True,
                    'messages': messages
                }

        except pymysql.Error as e:
            print(f"Error getting new messages: {e}")
            return {'success': False, 'messages': []}
        finally:
            if conn:
                conn.close()
