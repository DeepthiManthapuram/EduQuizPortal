from .supabase_client import client

class UserDAO:
    def get_by_username(self, username):
        res = client.table("users").select("*").eq("username", username).execute()
        return res.data[0] if res.data else None

    def get_by_email(self, email):
        res = client.table("users").select("*").eq("email", email).execute()
        return res.data[0] if res.data else None

    def create(self, username, email, password, role):
        res = client.table("users").insert({
            "username": username, "email": email, "password": password, "role": role
        }).execute()
        return res.data[0] if res.data else None

    def get_students(self):
        try:
            res = client.table("users").select("*").eq("role", "student").execute()
            print(f"✅ Found {len(res.data)} students in database")
            return res.data or []
        except Exception as e:
            print(f"❌ Error getting students: {e}")
            return []

    # ADD THIS METHOD TO GET STUDENT COUNT
    def get_student_count(self):
        try:
            res = client.table("users").select("user_id", count="exact").eq("role", "student").execute()
            count = res.count if hasattr(res, 'count') else len(res.data) if res.data else 0
            print(f"✅ Total students count: {count}")
            return count
        except Exception as e:
            print(f"❌ Error getting student count: {e}")
            return 0