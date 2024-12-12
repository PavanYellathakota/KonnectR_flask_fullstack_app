# user.py
import pymysql
import hashlib
from typing import Optional, Dict, Any, List
import yaml
from datetime import datetime
from baseObject import BaseObject

class User(BaseObject):
    def __init__(self, username: str, email: str, password: str, user_type: str,
                 org_name: Optional[str] = None, org_id: Optional[int] = None):
        """Initialize User object"""
        super().__init__()
        self.username = username
        self.email = email
        self.hashed_password = self._hash_password(password) if password else None
        self.user_type = user_type
        self.org_name = org_name or "Not Set"
        self.org_id = org_id
        self.user_id = None

    @staticmethod
    def _hash_password(password: str) -> str:
        """Hash password using MD5"""
        return hashlib.md5(password.encode()).hexdigest()

    @staticmethod
    def get_db_connection():
        """Get database connection using config"""
        with open('config.yaml', 'r') as file:
            config = yaml.safe_load(file)
        return pymysql.connect(
            host=config['db']['host'],
            user=config['db']['user'],
            password=config['db']['passwd'],
            database=config['db']['db'],
            port=config['db']['port'],
            cursorclass=pymysql.cursors.DictCursor
        )

    def validate(self) -> tuple[bool, str]:
        """Validate user data before saving"""
        if not self.username or len(self.username) < 3:
            return False, "Username must be at least 3 characters long"
        
        if not self.email or '@' not in self.email:
            return False, "Invalid email address"
            
        valid_user_types = ['Student', 'Professor', 'Professional', 'Company_recruiter', 'Admin']
        if self.user_type not in valid_user_types:
            return False, f"Invalid user type. Must be one of {valid_user_types}"
            
        return True, ""

    def save(self) -> Optional[int]:
        """Save user to database"""
        # Validate before saving
        is_valid, error_message = self.validate()
        if not is_valid:
            raise ValueError(error_message)

        self.before_save()
        conn = self.get_db_connection()
        try:
            with conn.cursor() as cursor:
                if self.user_id:
                    # Update existing user
                    query = """
                        UPDATE Users 
                        SET username = %s, email = %s, user_type = %s, 
                            org_name = %s, org_id = %s, updated_at = %s
                        WHERE user_id = %s
                    """
                    values = (self.username, self.email, self.user_type,
                            self.org_name, self.org_id, self.updated_at, self.user_id)
                else:
                    # Insert new user
                    query = """
                        INSERT INTO Users (username, email, hashed_password, created_at, 
                                        user_type, org_name, org_id)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """
                    values = (self.username, self.email, self.hashed_password,
                            self.created_at, self.user_type, self.org_name, self.org_id)
                
                cursor.execute(query, values)
                conn.commit()
                
                if not self.user_id:
                    self.user_id = cursor.lastrowid
                
                self.after_save()
                return self.user_id
        except pymysql.Error as e:
            print(f"Database error in save: {e}")
            return None
        finally:
            conn.close()

    @staticmethod
    def get_by_email(email: str) -> Optional['User']:
        """Find user by email"""
        conn = User.get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM Users WHERE email = %s", (email,))
                user_data = cursor.fetchone()
                
                if user_data:
                    user = User(
                        username=user_data['username'],
                        email=user_data['email'],
                        password='',  # Password is already hashed in DB
                        user_type=user_data['user_type'],
                        org_name=user_data['org_name'],
                        org_id=user_data['org_id']
                    )
                    user.user_id = user_data['user_id']
                    user.hashed_password = user_data['hashed_password']
                    user.created_at = user_data['created_at']
                    return user
                return None
        finally:
            conn.close()

    @staticmethod
    def get_by_id(user_id: int) -> Optional['User']:
        """Find user by ID"""
        conn = User.get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT * FROM Users 
                    WHERE user_id = %s AND deleted = 0
                """, (user_id,))
                user_data = cursor.fetchone()
                
                if user_data:
                    user = User(
                        username=user_data['username'],
                        email=user_data['email'],
                        password='',
                        user_type=user_data['user_type'],
                        org_name=user_data['org_name'],
                        org_id=user_data['org_id']
                    )
                    user.user_id = user_data['user_id']
                    user.hashed_password = user_data['hashed_password']
                    user.created_at = user_data['created_at']
                    return user
                return None
        finally:
            conn.close()

    def verify_password(self, password: str) -> bool:
        """Verify password"""
        return self.hashed_password == self._hash_password(password)

    def delete(self) -> bool:
        """Soft delete user"""
        self.before_delete()
        conn = self.get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    UPDATE Users 
                    SET deleted = 1, updated_at = %s 
                    WHERE user_id = %s
                """, (datetime.now(), self.user_id))
                conn.commit()
                self.deleted = True
                self.after_delete()
                return True
        except pymysql.Error as e:
            print(f"Database error in delete: {e}")
            return False
        finally:
            conn.close()

    @staticmethod
    def get_all(include_deleted: bool = False) -> List['User']:
        """Get all users"""
        conn = User.get_db_connection()
        try:
            with conn.cursor() as cursor:
                query = "SELECT * FROM Users"
                if not include_deleted:
                    query += " WHERE deleted = 0"
                cursor.execute(query)
                users = []
                for user_data in cursor.fetchall():
                    user = User(
                        username=user_data['username'],
                        email=user_data['email'],
                        password='',
                        user_type=user_data['user_type'],
                        org_name=user_data['org_name'],
                        org_id=user_data['org_id']
                    )
                    user.user_id = user_data['user_id']
                    user.created_at = user_data['created_at']
                    user.deleted = user_data['deleted']
                    users.append(user)
                return users
        finally:
            conn.close()

