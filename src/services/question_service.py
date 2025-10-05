# src/services/question_service.py
from dao.question_dao import QuestionDAO

question_dao = QuestionDAO()

class QuestionService:
    def create_question(self, question_data):
        try:
            # Validate required fields
            required_fields = ['subject_id', 'question_text', 'option_a', 'option_b', 
                               'option_c', 'option_d', 'correct_option', 'created_by']
            for field in required_fields:
                if not question_data.get(field):
                    return False, f"Missing required field: {field}"
            
            # Save question in DB
            question = question_dao.create(question_data)
            if question:
                return True, question
            return False, "Failed to create question"
        except Exception as e:
            import traceback
            traceback.print_exc()
            return False, str(e)

    def get_questions_by_subject(self, subject_id):
        try:
            print(f"🔍 QuestionService: Getting questions for subject {subject_id}")
            questions = question_dao.get_by_subject(subject_id)
            print(f"✅ QuestionService: Found {len(questions)} questions")
            return True, questions
        except Exception as e:
            print(f"🚨 QuestionService Error: {e}")
            return False, str(e)
    
    def update_question(self, question_id, update_data):
        try:
            print(f"🔍 QuestionService: Updating question {question_id} with data: {update_data}")
            
            # Validate that we have fields to update
            if not update_data:
                return False, "No update data provided"
            
            # Update the question using QuestionDAO
            updated_question = question_dao.update(question_id, update_data)
            
            if updated_question:
                print(f"✅ QuestionService: Question updated successfully: {updated_question}")
                return True, updated_question
            else:
                print("❌ QuestionService: Failed to update question")
                return False, "Failed to update question"
                
        except Exception as e:
            print(f"🚨 QuestionService Update Error: {e}")
            import traceback
            traceback.print_exc()
            return False, f"Internal server error: {str(e)}"

    # MAKE SURE THIS DELETE METHOD IS PRESENT
    def delete_question(self, question_id):
        try:
            print(f"🔍 QuestionService: Deleting question {question_id}")
            
            # Delete the question using QuestionDAO
            result = question_dao.delete(question_id)
            
            if result:
                print(f"✅ QuestionService: Question deleted successfully: {result}")
                return True, "Question deleted successfully"
            else:
                print("❌ QuestionService: Failed to delete question - DAO returned None")
                return False, "Failed to delete question"
                
        except Exception as e:
            print(f"🚨 QuestionService Delete Error: {e}")
            import traceback
            traceback.print_exc()
            return False, f"Internal server error: {str(e)}"