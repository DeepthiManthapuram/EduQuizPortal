from .supabase_client import client

class AttemptDAO:
    def create_attempt(self, user_id, subject_id, total_questions, correct_answers, score):
        res = client.table("attempts").insert({
            "user_id": user_id,
            "subject_id": subject_id,
            "total_questions": total_questions,
            "correct_answers": correct_answers,
            "score": score
        }).execute()
        return res.data[0] if res.data else None

    def get_user_attempts(self, user_id):
        res = client.table("attempts").select("*").eq("user_id", user_id).execute()
        return res.data or []

    def get_active_status(self, subject_id):
        # If any attempt with finished_at is null, consider active
        res = client.table("attempts").select("*").eq("subject_id", subject_id).is_("finished_at", None).execute()
        return bool(res.data)
