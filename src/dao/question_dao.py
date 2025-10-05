from .supabase_client import client

class QuestionDAO:
    def get_by_subject(self, subject_id):
        try:
            res = client.table("questions").select("*").eq("subject_id", subject_id).execute()
            return res.data or []
        except Exception as e:
            print(f"❌ Error getting questions by subject: {e}")
            return []

    def create(self, question_data):
        try:
            print(f"🔍 QuestionDAO: Inserting question: {question_data}")
            res = client.table("questions").insert({
                "subject_id": question_data['subject_id'],
                "question_text": question_data['question_text'],
                "option_a": question_data['option_a'],
                "option_b": question_data['option_b'],
                "option_c": question_data['option_c'],
                "option_d": question_data['option_d'],
                "correct_option": question_data['correct_option'],
                "created_by": question_data['created_by']
            }).execute()
            print(f"✅ QuestionDAO: Insert result: {res.data}")
            return res.data[0] if res.data else None
        except Exception as e:
            print(f"❌ Error creating question: {e}")
            return None

    def update(self, question_id, fields):
        try:
            # Try common primary key names
            res = client.table("questions").update(fields).eq("question_id", question_id).execute()
            if not res.data:
                res = client.table("questions").update(fields).eq("id", question_id).execute()
            return res.data[0] if res.data else None
        except Exception as e:
            print(f"❌ Error updating question: {e}")
            return None

    def delete(self, question_id):
        try:
            print(f"🔍 QuestionDAO: Attempting to delete question with ID: {question_id}")
            
            # First try with question_id
            res = client.table("questions").delete().eq("question_id", question_id).execute()
            print(f"🔍 Delete attempt with question_id: {res}")
            
            if res.data and len(res.data) > 0:
                print(f"✅ QuestionDAO: Deleted using question_id")
                return res
            
            # If not found, try with id
            res = client.table("questions").delete().eq("id", question_id).execute()
            print(f"🔍 Delete attempt with id: {res}")
            
            if res.data and len(res.data) > 0:
                print(f"✅ QuestionDAO: Deleted using id")
                return res
            
            print("❌ QuestionDAO: Question not found with either question_id or id")
            return None
            
        except Exception as e:
            print(f"❌ Error deleting question: {e}")
            # Print the full error details
            if hasattr(e, 'message'):
                print(f"❌ Error message: {e.message}")
            if hasattr(e, 'code'):
                print(f"❌ Error code: {e.code}")
            if hasattr(e, 'details'):
                print(f"❌ Error details: {e.details}")
            return None

    # ADD THIS METHOD TO GET TOTAL QUESTIONS COUNT
    def get_total_questions_count(self):
        try:
            res = client.table("questions").select("question_id", count="exact").execute()
            count = res.count if hasattr(res, 'count') else len(res.data) if res.data else 0
            print(f"✅ Total questions count: {count}")
            return count
        except Exception as e:
            print(f"❌ Error getting total questions count: {e}")
            return 0