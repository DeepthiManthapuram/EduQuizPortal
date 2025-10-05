# src/services/auth_service.py
from dao.user_dao import UserDAO

user_dao = UserDAO()

class AuthService:
    def register(self, username, email, password, role):
        try:
            # Input validation
            if not username or not email or not password:
                return False, "All fields are required"
            
            if role not in ['student', 'admin']:
                return False, "Role must be 'student' or 'admin'"
            
            # Check if username exists
            if user_dao.get_by_username(username):
                return False, "Username already exists"
            
            # Check if email exists
            if user_dao.get_by_email(email):
                return False, "Email already exists"
            
            # Create user
            user = user_dao.create(username, email, password, role)
            
            if user:
                return True, {
                    "user_id": user.get("user_id"),
                    "username": user.get("username"),
                    "email": user.get("email"),
                    "role": user.get("role")
                }
            else:
                return False, "Failed to create user"
                
        except Exception as e:
            print(f"🚨 Registration error: {e}")
            return False, f"Registration failed: {str(e)}"

    def login(self, username_or_email, password):
        try:
            if not username_or_email or not password:
                return False, "Username/email and password are required"
            
            # Try username first, then email
            user = user_dao.get_by_username(username_or_email)
            if not user:
                user = user_dao.get_by_email(username_or_email)
            
            if not user:
                return False, "User not found"
            
            # Simple password check (in real app, use hashing)
            if user.get("password") != password:
                return False, "Incorrect password"
            
            # Return user data without password
            user_data = {
                "user_id": user.get("user_id"),
                "username": user.get("username"),
                "email": user.get("email"),
                "role": user.get("role")
            }
            return True, user_data
            
        except Exception as e:
            print(f"🚨 Login error: {e}")
            return False, f"Login failed: {str(e)}"