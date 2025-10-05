# src/services/admin_service.py
from dao.user_dao import UserDAO
from dao.question_dao import QuestionDAO
from dao.attempt_dao import AttemptDAO

user_dao = UserDAO()
question_dao = QuestionDAO()
attempt_dao = AttemptDAO()  # Fixed variable name

class AdminService:
    def get_students(self):
        return user_dao.get_students()

    def add_question(self, question_obj):
        return question_dao.create(question_obj)

    def modify_question(self, question_id, fields):
        return question_dao.update(question_id, fields)

    def delete_question(self, question_id):
        return question_dao.delete(question_id)

    def quiz_status(self, subject_id):
        return attempt_dao.get_active_status(subject_id)

    def get_all_students_with_stats(self):
        try:
            # Get all students from database
            students = user_dao.get_students()
            print(f"📊 Found {len(students)} students in database")
            
            students_with_stats = []
            
            for student in students:
                # Get attempts for this student
                attempts = attempt_dao.get_user_attempts(student.get('user_id'))
                
                # Calculate stats
                quizzes_taken = len(attempts)
                total_score = sum(attempt.get('score', 0) for attempt in attempts)
                avg_score = total_score / quizzes_taken if quizzes_taken > 0 else 0
                
                # Determine performance
                performance = self._get_performance_level(avg_score)
                
                students_with_stats.append({
                    'user_id': student.get('user_id'),
                    'name': student.get('username') or student.get('name', 'Unknown'),
                    'email': student.get('email'),
                    'quizzes_taken': quizzes_taken,
                    'avg_score': f"{avg_score:.1f}%",
                    'performance': performance,
                    'joined': student.get('created_at', '')[:10] if student.get('created_at') else 'Unknown'
                })
            
            return True, students_with_stats
            
        except Exception as e:
            print(f"❌ Error getting students with stats: {e}")
            import traceback
            traceback.print_exc()
            return False, str(e)
    
    def _get_performance_level(self, score):
        if score >= 90:
            return 'Excellent'
        elif score >= 80:
            return 'Good'
        elif score >= 70:
            return 'Average'
        else:
            return 'Poor'