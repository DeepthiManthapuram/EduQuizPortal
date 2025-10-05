# src/services/student_service.py
from dao.question_dao import QuestionDAO
from dao.attempt_dao import AttemptDAO
from dao.supabase_client import client

class StudentService:
    def __init__(self):
        self.qdao = QuestionDAO()
        self.adao = AttemptDAO()

    def list_subjects(self):
        try:
            res = client.table("subjects").select("*").execute()
            print(f"✅ Found {len(res.data)} subjects")
            return res.data or []
        except Exception as e:
            print(f"❌ Error listing subjects: {e}")
            return []

    def start_quiz(self, user, subject_id):
        try:
            questions = self.qdao.get_by_subject(subject_id)
            if not questions:
                return False, "No questions available for this subject"
            
            return True, questions
        except Exception as e:
            print(f"❌ Error starting quiz: {e}")
            return False, f"Error starting quiz: {str(e)}"

    def submit_attempt(self, user_id, subject_id, total_questions, correct_answers):
        try:
            score = (correct_answers / total_questions) * 100 if total_questions > 0 else 0
            
            attempt = self.adao.create_attempt(
                user_id=user_id,
                subject_id=subject_id,
                total_questions=total_questions,
                correct_answers=correct_answers,
                score=score
            )
            
            return attempt
        except Exception as e:
            print(f"❌ Error submitting attempt: {e}")
            return None