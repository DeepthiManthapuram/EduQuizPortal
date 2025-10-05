# src/cli/main.py
import sys
import os

# Add the src directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.dirname(current_dir)  # This goes to src/
sys.path.insert(0, src_dir)

try:
    from services.auth_service import AuthService
    from services.student_service import StudentService
    from services.admin_service import AdminService
    from dao.attempt_dao import AttemptDAO
    from dao.question_dao import QuestionDAO
    from dao.supabase_client import client
    
    print("✅ All imports successful")
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)

auth = AuthService()
student_svc = StudentService()
admin_svc = AdminService()

def main_menu():
    while True:
        print("\n" + "="*50)
        print("           eduQuizPortal - Main Menu")
        print("="*50)
        print("1. Login")
        print("2. Register")
        print("3. Exit")
        print("-"*50)
        
        choice = input("Choose option (1-3): ").strip()
        
        if choice == "1":
            login_flow()
        elif choice == "2":
            register_flow()
        elif choice == "3":
            print("\nThank you for using eduQuizPortal! Goodbye! 👋")
            sys.exit(0)
        else:
            print("❌ Invalid choice. Please enter 1, 2, or 3.")

def register_flow():
    print("\n" + "="*50)
    print("               User Registration")
    print("="*50)
    
    username = input("Username: ").strip()
    email = input("Email: ").strip()
    password = input("Password: ").strip()
    role = input("Role (student/admin): ").strip().lower()
    
    if not username or not email or not password:
        print("❌ All fields are required!")
        return
        
    if role not in ['student', 'admin']:
        print("❌ Role must be 'student' or 'admin'")
        return
    
    ok, res = auth.register(username, email, password, role)
    if ok:
        print("✅ Registration successful! You can now login.")
    else:
        print(f"❌ Registration failed: {res}")

def login_flow():
    print("\n" + "="*50)
    print("                  User Login")
    print("="*50)
    
    iden = input("Username or Email: ").strip()
    password = input("Password: ").strip()
    
    if not iden or not password:
        print("❌ Both username/email and password are required!")
        return
    
    ok, res = auth.login(iden, password)
    if not ok:
        print(f"❌ Login failed: {res}")
        return
        
    user = res
    print(f"\n🎉 Welcome {user['username']} ({user['role'].title()})!")
    
    if user["role"] == "student":
        student_menu(user)
    else:
        admin_menu(user)

def student_menu(user):
    while True:
        print("\n" + "="*50)
        print(f"       Student Dashboard - Welcome {user['username']}")
        print("="*50)
        print("1. Take Quiz")
        print("2. View My Attempts & Scores")
        print("3. View Leaderboard")
        print("4. Logout")
        print("-"*50)
        
        choice = input("Choose option (1-4): ").strip()
        
        if choice == "1":
            take_quiz_flow(user)
        elif choice == "2":
            view_attempts(user)
        elif choice == "3":
            show_leaderboard()
        elif choice == "4":
            print("👋 Logging out...")
            break
        else:
            print("❌ Invalid choice. Please enter 1-4.")

def take_quiz_flow(user):
    print("\n" + "="*50)
    print("               Available Subjects")
    print("="*50)
    
    subjects = student_svc.list_subjects()
    if not subjects:
        print("❌ No subjects available at the moment.")
        return
    
    for s in subjects:
        print(f"{s['subject_id']}. {s['name']}")
    print("-"*50)
    
    try:
        subj_id = int(input("Choose subject ID: ").strip())
    except ValueError:
        print("❌ Please enter a valid subject ID (number).")
        return
    
    # Check if subject exists
    subject_exists = any(s['subject_id'] == subj_id for s in subjects)
    if not subject_exists:
        print("❌ Invalid subject ID.")
        return
    
    ok, qs = student_svc.start_quiz(user, subj_id)
    if not ok:
        print(f"❌ {qs}")
        return
        
    if not qs:
        print("❌ No questions available for this subject.")
        return
    
    total = len(qs)
    correct = 0
    
    print(f"\n📝 Starting quiz with {total} questions...")
    print("="*50)
    
    for i, q in enumerate(qs, 1):
        print(f"\nQ{i}: {q['question_text']}")
        print(f"A. {q['option_a']}")
        print(f"B. {q['option_b']}")
        if q.get('option_c'):
            print(f"C. {q['option_c']}")
        if q.get('option_d'):
            print(f"D. {q['option_d']}")
        
        while True:
            ans = input("Your answer (A/B/C/D): ").strip().upper()
            if ans in ['A', 'B', 'C', 'D']:
                break
            print("❌ Please enter A, B, C, or D")
        
        if ans == q["correct_option"].upper():
            print("✅ Correct!")
            correct += 1
        else:
            print(f"❌ Wrong! Correct answer: {q['correct_option'].upper()}")
    
    # Submit attempt
    attempt = student_svc.submit_attempt(user["user_id"], subj_id, total, correct)
    
    print("\n" + "="*50)
    print("                 Quiz Results")
    print("="*50)
    print(f"Total Questions: {total}")
    print(f"Correct Answers: {correct}")
    print(f"Score: {(correct/total)*100:.2f}% ({correct}/{total})")
    
    if attempt:
        print("✅ Results saved successfully!")
    else:
        print("⚠️  Results could not be saved.")

def view_attempts(user):
    adao = AttemptDAO()
    attempts = adao.get_user_attempts(user["user_id"])
    
    print("\n" + "="*50)
    print("              My Quiz Attempts")
    print("="*50)
    
    if not attempts:
        print("No quiz attempts yet. Take a quiz to see your results here!")
        return
    
    for i, attempt in enumerate(attempts, 1):
        score_percent = (attempt['correct_answers'] / attempt['total_questions']) * 100
        print(f"{i}. Subject {attempt['subject_id']} - "
              f"Score: {score_percent:.1f}% ({attempt['correct_answers']}/{attempt['total_questions']}) - "
              f"Date: {attempt.get('started_at', 'N/A')}")

def show_leaderboard():
    try:
        res = client.table("attempts").select(
            "user_id, score, correct_answers, total_questions, users(username), subjects(name)"
        ).order("score", desc=True).limit(10).execute()
        
        rows = res.data or []
        
        print("\n" + "="*50)
        print("               Leaderboard - Top Scores")
        print("="*50)
        
        if not rows:
            print("No quiz attempts yet. Be the first to take a quiz!")
            return
        
        for i, row in enumerate(rows, 1):
            username = row.get("users", {}).get("username", "Unknown")
            subject_name = row.get("subjects", {}).get("name", "Unknown Subject")
            score = row.get('score', 0)
            correct = row.get('correct_answers', 0)
            total = row.get('total_questions', 0)
            
            print(f"{i}. {username} - {subject_name} - {score:.1f}% ({correct}/{total})")
            
    except Exception as e:
        print(f"❌ Error loading leaderboard: {e}")

def admin_menu(user):
    while True:
        print("\n" + "="*50)
        print(f"        Admin Dashboard - Welcome {user['username']}")
        print("="*50)
        print("1. View All Students")
        print("2. Manage Questions")
        print("3. Check Quiz Status")
        print("4. View Leaderboard")
        print("5. Student Statistics")
        print("6. Logout")
        print("-"*50)
        
        choice = input("Choose option (1-6): ").strip()
        
        if choice == "1":
            view_all_students()
        elif choice == "2":
            edit_questions_flow(user)
        elif choice == "3":
            check_quiz_status()
        elif choice == "4":
            show_leaderboard()
        elif choice == "5":
            show_student_stats()
        elif choice == "6":
            print("👋 Logging out...")
            break
        else:
            print("❌ Invalid choice. Please enter 1-6.")

def view_all_students():
    students = admin_svc.get_students()
    
    print("\n" + "="*50)
    print("               All Students")
    print("="*50)
    
    if not students:
        print("No students found.")
        return
    
    for i, student in enumerate(students, 1):
        print(f"{i}. ID: {student['user_id']} | "
              f"Username: {student['username']} | "
              f"Email: {student['email']} | "
              f"Joined: {student.get('created_at', 'N/A')}")

def check_quiz_status():
    try:
        subjects = client.table("subjects").select("*").execute().data
        if not subjects:
            print("❌ No subjects found.")
            return
        
        print("\n" + "="*50)
        print("              Quiz Status by Subject")
        print("="*50)
        
        for subject in subjects:
            subject_id = subject['subject_id']
            active = admin_svc.quiz_status(subject_id)
            status = "🟢 ACTIVE" if active else "🔴 INACTIVE"
            print(f"Subject {subject_id}: {subject['name']} - {status}")
            
    except Exception as e:
        print(f"❌ Error checking quiz status: {e}")

def show_student_stats():
    ok, students_with_stats = admin_svc.get_all_students_with_stats()
    
    if not ok:
        print(f"❌ Error: {students_with_stats}")
        return
    
    print("\n" + "="*50)
    print("           Student Performance Statistics")
    print("="*50)
    
    if not students_with_stats:
        print("No student data available.")
        return
    
    for student in students_with_stats:
        print(f"👤 {student['name']} ({student['email']})")
        print(f"   📊 Quizzes Taken: {student['quizzes_taken']}")
        print(f"   🎯 Average Score: {student['avg_score']}")
        print(f"   📈 Performance: {student['performance']}")
        print(f"   📅 Joined: {student['joined']}")
        print("-" * 30)

def edit_questions_flow(user):
    while True:
        print("\n" + "="*50)
        print("             Question Management")
        print("="*50)
        print("1. Add New Question")
        print("2. Modify Existing Question")
        print("3. Delete Question")
        print("4. Back to Admin Menu")
        print("-"*50)
        
        ch = input("Choose option (1-4): ").strip()
        
        if ch == "1":
            add_question_flow(user)
        elif ch == "2":
            modify_question_flow()
        elif ch == "3":
            delete_question_flow()
        elif ch == "4":
            break
        else:
            print("❌ Invalid choice. Please enter 1-4.")

def add_question_flow(user):
    print("\n" + "="*50)
    print("              Add New Question")
    print("="*50)
    
    try:
        # Show available subjects
        subjects = client.table("subjects").select("*").execute().data
        if not subjects:
            print("❌ No subjects available. Please create subjects first.")
            return
        
        for s in subjects:
            print(f"{s['subject_id']}. {s['name']}")
        print("-"*50)
        
        sid = int(input("Subject ID: ").strip())
        qtext = input("Question Text: ").strip()
        a = input("Option A: ").strip()
        b = input("Option B: ").strip()
        c = input("Option C: ").strip()
        d = input("Option D: ").strip()
        
        while True:
            corr = input("Correct Option (A/B/C/D): ").strip().upper()
            if corr in ['A', 'B', 'C', 'D']:
                break
            print("❌ Please enter A, B, C, or D")
        
        # Create question using QuestionDAO directly
        from dao.question_dao import QuestionDAO
        qdao = QuestionDAO()
        
        question_data = {
            'subject_id': sid,
            'question_text': qtext,
            'option_a': a,
            'option_b': b,
            'option_c': c,
            'option_d': d,
            'correct_option': corr,
            'created_by': user['user_id']
        }
        
        result = qdao.create(question_data)
        if result:
            print("✅ Question added successfully!")
        else:
            print("❌ Failed to add question.")
            
    except ValueError:
        print("❌ Please enter valid numbers for subject ID.")
    except Exception as e:
        print(f"❌ Error adding question: {e}")

def modify_question_flow():
    print("\n" + "="*50)
    print("             Modify Question")
    print("="*50)
    
    try:
        qid = int(input("Question ID to modify: ").strip())
        field = input("Field to change (question_text/option_a/option_b/option_c/option_d/correct_option): ").strip()
        val = input("New value: ").strip()
        
        if field == 'correct_option':
            val = val.upper()
            if val not in ['A', 'B', 'C', 'D']:
                print("❌ Correct option must be A, B, C, or D")
                return
        
        from dao.question_dao import QuestionDAO
        qdao = QuestionDAO()
        result = qdao.update(qid, {field: val})
        
        if result:
            print("✅ Question updated successfully!")
        else:
            print("❌ Failed to update question. Check if question ID exists.")
            
    except ValueError:
        print("❌ Please enter a valid question ID (number).")
    except Exception as e:
        print(f"❌ Error updating question: {e}")

def delete_question_flow():
    print("\n" + "="*50)
    print("              Delete Question")
    print("="*50)
    
    try:
        qid = int(input("Question ID to delete: ").strip())
        
        # Confirm deletion
        confirm = input("Are you sure you want to delete this question? (y/N): ").strip().lower()
        if confirm != 'y':
            print("❌ Deletion cancelled.")
            return
        
        from dao.question_dao import QuestionDAO
        qdao = QuestionDAO()
        result = qdao.delete(qid)
        
        if result:
            print("✅ Question deleted successfully!")
        else:
            print("❌ Failed to delete question. Check if question ID exists.")
            
    except ValueError:
        print("❌ Please enter a valid question ID (number).")
    except Exception as e:
        print(f"❌ Error deleting question: {e}")

if __name__ == "__main__":
    print("🚀 Starting eduQuizPortal...")
    
    # Test database connection
    try:
        # Simple test query
        test = client.table('users').select('count', count='exact').execute()
        print("✅ Database connection successful!")
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        print("💡 Please check your internet connection and .env file")
        sys.exit(1)
    
    main_menu()