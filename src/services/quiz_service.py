from src.dao.question_dao import QuestionDAO


question_dao = QuestionDAO()


class QuizService:
    def get_quiz(self, subject_id: int):
        questions = question_dao.get_by_subject(subject_id)
        if not questions:
            return False, "No questions available for this subject"

        # Ensure we only expose safe fields and normalize shape
        sanitized = []
        for q in questions:
            sanitized.append(
                {
                    "question_id": q.get("question_id"),
                    "subject_id": q.get("subject_id"),
                    "question_text": q.get("question_text"),
                    "option_a": q.get("option_a"),
                    "option_b": q.get("option_b"),
                    "option_c": q.get("option_c"),
                    "option_d": q.get("option_d"),
                    "correct_option": q.get("correct_option"),
                }
            )

        return True, sanitized

