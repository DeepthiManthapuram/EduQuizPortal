# frontend/app.py
import streamlit as st
import os
import sys
from dotenv import load_dotenv
import time
import pandas as pd
from datetime import datetime

# Add backend to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.join(current_dir, '..', 'src')
sys.path.insert(0, backend_dir)

# Load environment variables
env_path = os.path.join(current_dir, '..', '.env')
if os.path.exists(env_path):
    load_dotenv(env_path)
    print("✅ Environment variables loaded")
else:
    st.error("❌ .env file not found!")

# Import backend services
try:
    from services.auth_service import AuthService
    from services.student_service import StudentService
    from services.admin_service import AdminService
    from dao.question_dao import QuestionDAO
    from dao.attempt_dao import AttemptDAO
    from dao.user_dao import UserDAO
    from dao.supabase_client import client
    print("✅ Backend services imported successfully")
except ImportError as e:
    st.error(f"❌ Backend import error: {e}")

# Page configuration
st.set_page_config(
    page_title="eduQuizPortal",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern styling
def load_css():
    st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: bold;
    }
    .card {
        background: white;
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        border-left: 5px solid #667eea;
        margin-bottom: 1rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
    }
    .quiz-card {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #28a745;
        margin: 1rem 0;
    }
    .question-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        border: 1px solid #e0e0e0;
        margin: 1rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .stButton>button {
        border-radius: 10px;
        height: 3rem;
        font-weight: bold;
        border: none;
    }
    .primary-button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
    }
    .secondary-button {
        background: #6c757d !important;
        color: white !important;
    }
    .success-button {
        background: #28a745 !important;
        color: white !important;
    }
    .danger-button {
        background: #dc3545 !important;
        color: white !important;
    }
    </style>
    """, unsafe_allow_html=True)

def initialize_session_state():
    """Initialize all session state variables"""
    defaults = {
        'user': None,
        'authenticated': False,
        'current_page': 'Login',
        'quiz_started': False,
        'current_questions': [],
        'current_answers': {},
        'quiz_subject_id': None,
        'quiz_start_time': None,
        'admin_current_tab': 'Student Management',
        'quiz_submitted': False
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

def login_section():
    """Login section with modern UI"""
    st.markdown('<div class="main-header">🎓 eduQuizPortal</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        with st.container():
            st.markdown("### Welcome Back! 👋")
            st.markdown("*Continue your learning journey*")
            
            with st.form("login_form"):
                username = st.text_input(
                    "👤 Username or Email", 
                    placeholder="Enter your username or email"
                )
                password = st.text_input(
                    "🔒 Password", 
                    type="password", 
                    placeholder="Enter your password"
                )
                
                col1, col2 = st.columns(2)
                with col1:
                    login_btn = st.form_submit_button(
                        "🚀 Login", 
                        use_container_width=True
                    )
                with col2:
                    register_btn = st.form_submit_button(
                        "📝 Register", 
                        use_container_width=True
                    )
                
                if login_btn:
                    if username and password:
                        with st.spinner("Logging in..."):
                            try:
                                auth_service = AuthService()
                                success, result = auth_service.login(username, password)
                                
                                if success:
                                    st.session_state.user = result
                                    st.session_state.authenticated = True
                                    st.session_state.current_page = "Dashboard"
                                    st.success("✅ Login successful!")
                                    time.sleep(1)
                                    st.rerun()
                                else:
                                    st.error(f"❌ {result}")
                            except Exception as e:
                                st.error(f"🚨 Login error: {str(e)}")
                    else:
                        st.error("Please fill in all fields")
                
                if register_btn:
                    st.session_state.current_page = "Register"
                    st.rerun()

def register_section():
    """Registration section"""
    st.markdown('<div class="main-header">🎓 Create Account</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        with st.container():
            st.markdown("### Join Our Learning Community 🌟")
            
            with st.form("register_form"):
                username = st.text_input("👤 Username", placeholder="Choose a username")
                email = st.text_input("📧 Email", placeholder="Enter your email")
                password = st.text_input("🔒 Password", type="password", placeholder="Create a password")
                confirm_password = st.text_input("🔒 Confirm Password", type="password", placeholder="Confirm your password")
                role = st.selectbox("🎯 Role", ["student", "admin"])
                
                col1, col2 = st.columns(2)
                with col1:
                    register_btn = st.form_submit_button("🌟 Create Account", use_container_width=True)
                with col2:
                    back_btn = st.form_submit_button("⬅️ Back to Login", use_container_width=True)
                
                if register_btn:
                    if not all([username, email, password, confirm_password]):
                        st.error("❌ Please fill in all fields")
                    elif password != confirm_password:
                        st.error("❌ Passwords do not match")
                    else:
                        with st.spinner("Creating account..."):
                            try:
                                auth_service = AuthService()
                                success, result = auth_service.register(username, email, password, role)
                                
                                if success:
                                    st.success("✅ Account created successfully! Please login.")
                                    time.sleep(2)
                                    st.session_state.current_page = "Login"
                                    st.rerun()
                                else:
                                    st.error(f"❌ {result}")
                            except Exception as e:
                                st.error(f"🚨 Registration error: {str(e)}")
                
                if back_btn:
                    st.session_state.current_page = "Login"
                    st.rerun()

def dashboard_section():
    """Main dashboard section - Different for students vs admins"""
    st.markdown(f'<div class="main-header">🎓 Welcome, {st.session_state.user["username"]}!</div>', unsafe_allow_html=True)
    
    if st.session_state.user["role"] == "student":
        student_dashboard()
    else:
        admin_dashboard()

def student_dashboard():
    """Student dashboard with learning features"""
    # User info and quick stats
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <h3>👤 Profile</h3>
            <p><strong>Role:</strong> Student</p>
            <p><strong>Email:</strong> {st.session_state.user["email"]}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        # Get user attempts count
        try:
            attempt_dao = AttemptDAO()
            attempts = attempt_dao.get_user_attempts(st.session_state.user["user_id"])
            attempts_count = len(attempts)
            
            st.markdown(f"""
            <div class="metric-card">
                <h3>📊 Quizzes Taken</h3>
                <h1 style="font-size: 3rem; margin: 0;">{attempts_count}</h1>
            </div>
            """, unsafe_allow_html=True)
        except:
            st.markdown("""
            <div class="metric-card">
                <h3>📊 Quizzes Taken</h3>
                <h1 style="font-size: 3rem; margin: 0;">0</h1>
            </div>
            """, unsafe_allow_html=True)
    
    with col3:
        # Calculate average score
        try:
            attempt_dao = AttemptDAO()
            attempts = attempt_dao.get_user_attempts(st.session_state.user["user_id"])
            if attempts:
                avg_score = sum((a['correct_answers'] / a['total_questions'] * 100) for a in attempts) / len(attempts)
            else:
                avg_score = 0
                
            st.markdown(f"""
            <div class="metric-card">
                <h3>🎯 Average Score</h3>
                <h1 style="font-size: 3rem; margin: 0;">{avg_score:.1f}%</h1>
            </div>
            """, unsafe_allow_html=True)
        except:
            st.markdown("""
            <div class="metric-card">
                <h3>🎯 Average Score</h3>
                <h1 style="font-size: 3rem; margin: 0;">0%</h1>
            </div>
            """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="metric-card">
            <h3>🚀 Quick Actions</h3>
            <p>Start learning now!</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Student navigation
    st.markdown("---")
    st.markdown("## 🚀 Quick Navigation")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📝 Take Quiz", use_container_width=True, type="primary"):
            st.session_state.current_page = "Take Quiz"
            st.rerun()
    
    with col2:
        if st.button("📊 My Results", use_container_width=True):
            st.session_state.current_page = "My Results"
            st.rerun()
    
    with col3:
        if st.button("🏆 Leaderboard", use_container_width=True):
            st.session_state.current_page = "Leaderboard"
            st.rerun()

def admin_dashboard():
    """Admin dashboard with management features"""
    # Admin metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        try:
            admin_service = AdminService()
            students = admin_service.get_students()
            st.metric("👥 Total Students", len(students))
        except:
            st.metric("👥 Total Students", 0)
    
    with col2:
        try:
            question_dao = QuestionDAO()
            total_questions = question_dao.get_total_questions_count()
            st.metric("❓ Total Questions", total_questions)
        except:
            st.metric("❓ Total Questions", 0)
    
    with col3:
        try:
            attempt_dao = AttemptDAO()
            attempts_res = client.table("attempts").select("attempt_id", count="exact").execute()
            total_attempts = attempts_res.count if hasattr(attempts_res, 'count') else len(attempts_res.data)
            st.metric("📊 Total Attempts", total_attempts)
        except:
            st.metric("📊 Total Attempts", 0)
    
    with col4:
        try:
            subjects_res = client.table("subjects").select("subject_id", count="exact").execute()
            total_subjects = subjects_res.count if hasattr(subjects_res, 'count') else len(subjects_res.data)
            st.metric("📚 Total Subjects", total_subjects)
        except:
            st.metric("📚 Total Subjects", "N/A")
    
    # Admin management tabs
    st.markdown("---")
    
    # Tabs for different management sections
    tab1, tab2, tab3 = st.tabs([
        "👥 Student Management", 
        "❓ Question Management", 
        "📈 Analytics & Leaderboard"
    ])
    
    # Set the current tab
    if 'admin_current_tab' not in st.session_state:
        st.session_state.admin_current_tab = "Student Management"
    
    with tab1:
        student_management_section()
    
    with tab2:
        question_management_section()
    
    with tab3:
        analytics_leaderboard_section()

def student_management_section():
    """Student management section for admins"""
    st.markdown("### 👥 Student Management")
    
    try:
        admin_service = AdminService()
        
        # Display all students
        st.markdown("#### All Students")
        students = admin_service.get_students()
        
        if not students:
            st.info("No students found.")
            return
        
        # Display in table format
        student_data = []
        for student in students:
            student_data.append({
                'ID': student['user_id'],
                'Username': student['username'],
                'Email': student['email'],
                'Role': student['role'],
                'Joined': student.get('created_at', 'N/A')[:10] if student.get('created_at') else 'N/A'
            })
        
        if student_data:
            st.dataframe(student_data, use_container_width=True)
        else:
            st.info("No students found.")
            
        # Student statistics
        st.markdown("---")
        st.markdown("#### 📊 Student Performance")
        success, students_with_stats = admin_service.get_all_students_with_stats()
        
        if success and students_with_stats:
            for student in students_with_stats:
                with st.container():
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.write(f"**{student['name']}**")
                        st.write(student['email'])
                    
                    with col2:
                        st.write(f"**Quizzes:** {student['quizzes_taken']}")
                    
                    with col3:
                        st.write(f"**Avg Score:** {student['avg_score']}")
                    
                    with col4:
                        performance = student['performance']
                        if performance == 'Excellent':
                            st.success(f"**Performance:** {performance}")
                        elif performance == 'Good':
                            st.info(f"**Performance:** {performance}")
                        elif performance == 'Average':
                            st.warning(f"**Performance:** {performance}")
                        else:
                            st.error(f"**Performance:** {performance}")
                    
                    st.markdown("---")
        else:
            st.info("No student statistics available.")
                
    except Exception as e:
        st.error(f"❌ Error loading students: {str(e)}")

def question_management_section():
    """Question management section for admins"""
    st.markdown("### ❓ Question Management")
    
    # Tabs for different operations
    qtab1, qtab2, qtab3 = st.tabs(["➕ Add Question", "✏️ Modify Question", "🗑️ Delete Question"])
    
    with qtab1:
        add_question_section()
    
    with qtab2:
        modify_question_section()
    
    with qtab3:
        delete_question_section()

def add_question_section():
    """Add question section"""
    st.markdown("#### ➕ Add New Question")
    
    try:
        # Show available subjects
        subjects = client.table("subjects").select("*").execute().data
        if not subjects:
            st.error("❌ No subjects available. Please create subjects first.")
            return
        
        # Subject selection
        subject_options = {f"{s['subject_id']}. {s['name']}": s['subject_id'] for s in subjects}
        selected_subject = st.selectbox("Select Subject:", list(subject_options.keys()))
        subject_id = subject_options[selected_subject]
        
        with st.form("add_question_form"):
            question_text = st.text_area("Question Text:", placeholder="Enter the question text")
            
            col1, col2 = st.columns(2)
            with col1:
                option_a = st.text_input("Option A:", placeholder="Enter option A")
                option_b = st.text_input("Option B:", placeholder="Enter option B")
            with col2:
                option_c = st.text_input("Option C (optional):", placeholder="Enter option C")
                option_d = st.text_input("Option D (optional):", placeholder="Enter option D")
            
            correct_option = st.selectbox("Correct Option:", ["A", "B", "C", "D"])
            
            col1, col2 = st.columns(2)
            with col1:
                add_btn = st.form_submit_button("✅ Add Question", type="primary", use_container_width=True)
            with col2:
                clear_btn = st.form_submit_button("🔄 Clear", use_container_width=True)
            
            if add_btn:
                if not all([question_text, option_a, option_b, correct_option]):
                    st.error("❌ Question text, options A, B, and correct option are required!")
                else:
                    with st.spinner("Adding question..."):
                        question_dao = QuestionDAO()
                        
                        question_data = {
                            'subject_id': subject_id,
                            'question_text': question_text,
                            'option_a': option_a,
                            'option_b': option_b,
                            'option_c': option_c,
                            'option_d': option_d,
                            'correct_option': correct_option,
                            'created_by': st.session_state.user['user_id']
                        }
                        
                        result = question_dao.create(question_data)
                        if result:
                            st.success("✅ Question added successfully!")
                        else:
                            st.error("❌ Failed to add question.")
            
            if clear_btn:
                st.rerun()
                
    except Exception as e:
        st.error(f"❌ Error adding question: {str(e)}")

def modify_question_section():
    """Modify question section"""
    st.markdown("#### ✏️ Modify Existing Question")
    
    try:
        # Get all questions for reference
        questions_res = client.table("questions").select("question_id, question_text, subject_id").execute()
        questions = questions_res.data if questions_res.data else []
        
        if not questions:
            st.info("No questions available to modify.")
            return
        
        # Question selection
        question_options = {f"Q{q['question_id']}: {q['question_text'][:50]}...": q['question_id'] for q in questions}
        selected_question_label = st.selectbox("Select Question to Modify:", list(question_options.keys()))
        question_id = question_options[selected_question_label]
        
        # Get current question data
        current_question_res = client.table("questions").select("*").eq("question_id", question_id).execute()
        if not current_question_res.data:
            st.error("Question not found!")
            return
        
        current_question = current_question_res.data[0]
        
        with st.form("modify_question_form"):
            st.markdown("**Current Question Details:**")
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Question:** {current_question['question_text']}")
                st.write(f"**Option A:** {current_question['option_a']}")
                st.write(f"**Option B:** {current_question['option_b']}")
            with col2:
                st.write(f"**Option C:** {current_question.get('option_c', 'N/A')}")
                st.write(f"**Option D:** {current_question.get('option_d', 'N/A')}")
                st.write(f"**Correct:** {current_question['correct_option']}")
            
            st.markdown("---")
            st.markdown("**Modify Field:**")
            
            field = st.selectbox(
                "Field to change:",
                ["question_text", "option_a", "option_b", "option_c", "option_d", "correct_option"]
            )
            
            new_value = st.text_input("New value:", placeholder=f"Enter new value for {field}")
            
            if field == 'correct_option' and new_value:
                new_value = new_value.upper()
                if new_value not in ['A', 'B', 'C', 'D']:
                    st.error("❌ Correct option must be A, B, C, or D")
            
            col1, col2 = st.columns(2)
            with col1:
                update_btn = st.form_submit_button("✅ Update Question", type="primary", use_container_width=True)
            with col2:
                cancel_btn = st.form_submit_button("❌ Cancel", use_container_width=True)
            
            if update_btn:
                if not new_value:
                    st.error("❌ Please enter a new value")
                else:
                    with st.spinner("Updating question..."):
                        question_dao = QuestionDAO()
                        result = question_dao.update(question_id, {field: new_value})
                        if result:
                            st.success("✅ Question updated successfully!")
                        else:
                            st.error("❌ Failed to update question. Check if question ID exists.")
            
            if cancel_btn:
                st.rerun()
                
    except Exception as e:
        st.error(f"❌ Error modifying question: {str(e)}")

def delete_question_section():
    """Delete question section"""
    st.markdown("#### 🗑️ Delete Question")
    
    try:
        # Get all questions for reference
        questions_res = client.table("questions").select("question_id, question_text, subject_id").execute()
        questions = questions_res.data if questions_res.data else []
        
        if not questions:
            st.info("No questions available to delete.")
            return
        
        # Question selection
        question_options = {f"Q{q['question_id']}: {q['question_text'][:50]}...": q['question_id'] for q in questions}
        selected_question_label = st.selectbox("Select Question to Delete:", list(question_options.keys()))
        question_id = question_options[selected_question_label]
        
        # Get question details for confirmation
        question_res = client.table("questions").select("*").eq("question_id", question_id).execute()
        if question_res.data:
            question = question_res.data[0]
            
            st.warning("### ⚠️ Confirm Deletion")
            st.markdown(f"""
            **Question:** {question['question_text']}
            """)
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("✅ Confirm Delete", type="primary", use_container_width=True):
                    with st.spinner("Deleting question..."):
                        question_dao = QuestionDAO()
                        result = question_dao.delete(question_id)
                        
                        if result:
                            st.success("✅ Question deleted successfully!")
                            time.sleep(2)
                            st.rerun()
                        else:
                            st.error("❌ Failed to delete question. Check if question ID exists.")
            
            with col2:
                if st.button("❌ Cancel", use_container_width=True):
                    st.info("Deletion cancelled.")
                    st.rerun()
        else:
            st.error("Question not found!")
                
    except Exception as e:
        st.error(f"❌ Error deleting question: {str(e)}")

def analytics_leaderboard_section():
    """Analytics and leaderboard section for admins"""
    st.markdown("### 📈 System Analytics & Leaderboard")
    
    try:
        admin_service = AdminService()
        
        # Overall statistics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            students = admin_service.get_students()
            st.metric("Total Students", len(students))
        
        with col2:
            question_dao = QuestionDAO()
            total_questions = question_dao.get_total_questions_count()
            st.metric("Total Questions", total_questions)
        
        with col3:
            attempts_res = client.table("attempts").select("attempt_id", count="exact").execute()
            total_attempts = attempts_res.count if hasattr(attempts_res, 'count') else len(attempts_res.data)
            st.metric("Total Quiz Attempts", total_attempts)
        
        with col4:
            subjects_res = client.table("subjects").select("subject_id", count="exact").execute()
            total_subjects = subjects_res.count if hasattr(subjects_res, 'count') else len(subjects_res.data)
            st.metric("Total Subjects", total_subjects)
        
        # Student performance overview
        st.markdown("---")
        st.markdown("### 🎯 Student Performance Overview")
        
        success, students_with_stats = admin_service.get_all_students_with_stats()
        
        if success and students_with_stats:
            # Performance distribution
            performance_counts = {}
            for student in students_with_stats:
                performance = student['performance']
                performance_counts[performance] = performance_counts.get(performance, 0) + 1
            
            col1, col2, col3, col4 = st.columns(4)
            performances = ['Excellent', 'Good', 'Average', 'Poor']
            
            for i, perf in enumerate(performances):
                with [col1, col2, col3, col4][i]:
                    count = performance_counts.get(perf, 0)
                    st.metric(f"{perf} Performance", count)
            
            # Detailed student performance
            st.markdown("#### 📊 Detailed Student Performance")
            for student in students_with_stats:
                with st.container():
                    col1, col2, col3, col4, col5 = st.columns([2, 1, 1, 1, 1])
                    
                    with col1:
                        st.write(f"**{student['name']}**")
                        st.write(student['email'])
                    
                    with col2:
                        st.metric("Quizzes", student['quizzes_taken'])
                    
                    with col3:
                        st.write(f"Avg: {student['avg_score']}")
                    
                    with col4:
                        performance = student['performance']
                        if performance == 'Excellent':
                            st.success(performance)
                        elif performance == 'Good':
                            st.info(performance)
                        elif performance == 'Average':
                            st.warning(performance)
                        else:
                            st.error(performance)
                    
                    with col5:
                        st.write(f"Joined: {student['joined']}")
                    
                    st.markdown("---")
        else:
            st.info("No student performance data available.")
            
        # Leaderboard
        st.markdown("---")
        st.markdown("### 🏆 Leaderboard - Top Performers")
        
        res = client.table("attempts").select(
            "user_id, score, correct_answers, total_questions, users(username), subjects(name)"
        ).order("score", desc=True).limit(10).execute()
        
        leaderboard_data = res.data or []
        
        if leaderboard_data:
            for i, entry in enumerate(leaderboard_data, 1):
                username = entry.get("users", {}).get("username", "Unknown")
                subject_name = entry.get("subjects", {}).get("name", "Unknown Subject")
                score = entry.get('score', 0)
                correct = entry.get('correct_answers', 0)
                total = entry.get('total_questions', 0)
                
                # Medal emojis for top 3
                medal = ""
                if i == 1: medal = "🥇"
                elif i == 2: medal = "🥈"
                elif i == 3: medal = "🥉"
                
                with st.container():
                    col1, col2, col3, col4, col5 = st.columns([1, 3, 3, 2, 2])
                    
                    with col1:
                        st.markdown(f"**{medal} #{i}**")
                    with col2:
                        st.markdown(f"**{username}**")
                    with col3:
                        st.markdown(f"*{subject_name}*")
                    with col4:
                        st.markdown(f"**{score:.1f}%**")
                    with col5:
                        st.markdown(f"({correct}/{total})")
                    
                    st.markdown("---")
        else:
            st.info("No leaderboard data available.")
                
    except Exception as e:
        st.error(f"❌ Error loading analytics: {str(e)}")

def take_quiz_section():
    """Take quiz section - ONLY for students"""
    if st.session_state.user["role"] != "student":
        st.error("❌ This feature is only available for students.")
        if st.button("⬅️ Back to Dashboard"):
            st.session_state.current_page = "Dashboard"
            st.rerun()
        return
    
    st.markdown('<div class="main-header">📝 Take Quiz</div>', unsafe_allow_html=True)
    
    # Initialize student_service at the beginning of the function
    student_service = StudentService()
    
    # Check if quiz was just submitted
    if st.session_state.get('quiz_submitted', False):
        # Show results and back button
        st.success("🎉 Quiz Submitted Successfully!")
        
        # Reset the submitted flag
        st.session_state.quiz_submitted = False
        
        if st.button("🏠 Back to Dashboard"):
            st.session_state.current_page = "Dashboard"
            st.rerun()
        return
    
    if not st.session_state.quiz_started:
        # Subject selection
        subjects = student_service.list_subjects()
        
        if not subjects:
            st.warning("❌ No subjects available at the moment.")
            if st.button("⬅️ Back to Dashboard"):
                st.session_state.current_page = "Dashboard"
                st.rerun()
            return
        
        st.markdown("### Choose a Subject")
        
        # Create subject options
        subject_options = {f"{s['subject_id']}. {s['name']}": s for s in subjects}
        selected_subject_label = st.selectbox("Select Subject:", list(subject_options.keys()))
        selected_subject = subject_options[selected_subject_label]
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🎯 Start Quiz", type="primary", use_container_width=True):
                subject_id = selected_subject['subject_id']
                success, questions = student_service.start_quiz(st.session_state.user, subject_id)
                
                if success and questions:
                    st.session_state.quiz_started = True
                    st.session_state.current_questions = questions
                    st.session_state.quiz_subject_id = subject_id
                    st.session_state.quiz_start_time = time.time()
                    st.session_state.current_answers = {}
                    st.success(f"✅ Started quiz for {selected_subject['name']}!")
                    st.rerun()
                else:
                    st.error("❌ Failed to start quiz. Please try again.")
        
        with col2:
            if st.button("⬅️ Back to Dashboard", use_container_width=True):
                st.session_state.current_page = "Dashboard"
                st.rerun()
    
    else:
        # Quiz in progress
        questions = st.session_state.current_questions
        
        # Get current subject name for display
        subjects = student_service.list_subjects()
        current_subject = next((s for s in subjects 
                              if s['subject_id'] == st.session_state.quiz_subject_id), None)
        
        st.markdown(f"### 📝 Quiz: {current_subject['name'] if current_subject else 'Unknown Subject'}")
        st.markdown(f"**Total Questions:** {len(questions)}")
        st.markdown("---")
        
        # Display questions
        with st.form("quiz_form"):
            for i, question in enumerate(questions, 1):
                with st.container():
                    st.markdown(f"**Q{i}: {question['question_text']}**")
                    
                    # Display options
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**A.** {question['option_a']}")
                        st.write(f"**B.** {question['option_b']}")
                    with col2:
                        if question.get('option_c'):
                            st.write(f"**C.** {question['option_c']}")
                        if question.get('option_d'):
                            st.write(f"**D.** {question['option_d']}")
                    
                    # Answer input
                    options = ['A', 'B']
                    if question.get('option_c'):
                        options.append('C')
                    if question.get('option_d'):
                        options.append('D')
                    
                    answer = st.radio(
                        f"Select your answer for Q{i}:",
                        options,
                        key=f"q_{question['question_id']}",
                        index=None,
                        horizontal=True
                    )
                    
                    if answer:
                        st.session_state.current_answers[question['question_id']] = answer
                    
                    st.markdown("---")
            
            col1, col2, col3 = st.columns([1, 1, 1])
            with col2:
                submit_btn = st.form_submit_button("✅ Submit Quiz", type="primary", use_container_width=True)
            
            if submit_btn:
                if len(st.session_state.current_answers) == len(questions):
                    with st.spinner("Submitting your answers..."):
                        # Calculate score
                        correct_answers = 0
                        for question in questions:
                            user_answer = st.session_state.current_answers.get(question['question_id'])
                            if user_answer and user_answer.upper() == question['correct_option'].upper():
                                correct_answers += 1
                        
                        total_questions = len(questions)
                        score_percentage = (correct_answers / total_questions) * 100
                        
                        # Save attempt
                        student_service = StudentService()
                        attempt = student_service.submit_attempt(
                            st.session_state.user["user_id"],
                            st.session_state.quiz_subject_id,
                            total_questions,
                            correct_answers
                        )
                        
                        # Show results
                        st.markdown(f"""
                        <div class="quiz-card">
                            <h3>📊 Quiz Results</h3>
                            <p><strong>Total Questions:</strong> {total_questions}</p>
                            <p><strong>Correct Answers:</strong> {correct_answers}</p>
                            <p><strong>Score:</strong> {score_percentage:.2f}% ({correct_answers}/{total_questions})</p>
                            <p><strong>Time Taken:</strong> {(time.time() - st.session_state.quiz_start_time):.1f} seconds</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        if attempt:
                            st.success("✅ Results saved successfully!")
                        else:
                            st.warning("⚠️ Results could not be saved.")
                        
                        # Reset quiz state and set submitted flag
                        st.session_state.quiz_started = False
                        st.session_state.current_questions = []
                        st.session_state.current_answers = {}
                        st.session_state.quiz_subject_id = None
                        st.session_state.quiz_submitted = True
                        
                        # Rerun to show the results page
                        st.rerun()
                else:
                    st.warning("⚠️ Please answer all questions before submitting.")

def view_attempts_section():
    """View attempts section - ONLY for students"""
    if st.session_state.user["role"] != "student":
        st.error("❌ This feature is only available for students.")
        if st.button("⬅️ Back to Dashboard"):
            st.session_state.current_page = "Dashboard"
            st.rerun()
        return
    
    st.markdown('<div class="main-header">📊 My Results</div>', unsafe_allow_html=True)
    
    try:
        attempt_dao = AttemptDAO()
        attempts = attempt_dao.get_user_attempts(st.session_state.user["user_id"])
        
        if not attempts:
            st.info("📝 You haven't taken any quizzes yet. Start your first quiz!")
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button("📝 Take First Quiz", use_container_width=True):
                    st.session_state.current_page = "Take Quiz"
                    st.rerun()
            return
        
        # Display attempts
        st.markdown("### My Quiz Attempts")
        st.markdown("---")
        
        for i, attempt in enumerate(attempts, 1):
            score_percent = (attempt['correct_answers'] / attempt['total_questions']) * 100
            
            # Get subject name
            try:
                subject_res = client.table("subjects").select("name").eq("subject_id", attempt['subject_id']).execute()
                subject_name = subject_res.data[0]['name'] if subject_res.data else f"Subject {attempt['subject_id']}"
            except:
                subject_name = f"Subject {attempt['subject_id']}"
            
            with st.container():
                col1, col2, col3, col4 = st.columns([2, 2, 2, 3])
                
                with col1:
                    st.write(f"**{subject_name}**")
                with col2:
                    st.write(f"Score: {score_percent:.1f}%")
                with col3:
                    st.write(f"Correct: {attempt['correct_answers']}/{attempt['total_questions']}")
                with col4:
                    attempt_date = attempt.get('started_at', 'N/A')
                    if attempt_date != 'N/A':
                        try:
                            if 'T' in attempt_date:
                                date_part = attempt_date.split('T')[0]
                                attempt_date = date_part
                        except:
                            pass
                    st.write(f"Date: {attempt_date}")
                
                st.markdown("---")
        
        # Show statistics
        st.markdown("### 📈 Performance Statistics")
        col1, col2, col3, col4 = st.columns(4)
        
        total_quizzes = len(attempts)
        avg_score = sum((a['correct_answers'] / a['total_questions'] * 100) for a in attempts) / total_quizzes
        best_score = max((a['correct_answers'] / a['total_questions'] * 100) for a in attempts)
        total_correct = sum(a['correct_answers'] for a in attempts)
        total_questions = sum(a['total_questions'] for a in attempts)
        
        with col1:
            st.metric("Total Quizzes", total_quizzes)
        with col2:
            st.metric("Average Score", f"{avg_score:.1f}%")
        with col3:
            st.metric("Best Score", f"{best_score:.1f}%")
        with col4:
            st.metric("Total Correct", f"{total_correct}/{total_questions}")
            
    except Exception as e:
        st.error(f"❌ Error loading results: {str(e)}")
    
    st.markdown("---")
    if st.button("⬅️ Back to Dashboard", use_container_width=True):
        st.session_state.current_page = "Dashboard"
        st.rerun()

def leaderboard_section():
    """Leaderboard section - Available for both"""
    st.markdown('<div class="main-header">🏆 Leaderboard</div>', unsafe_allow_html=True)
    
    try:
        # Get top attempts
        res = client.table("attempts").select(
            "user_id, score, correct_answers, total_questions, users(username), subjects(name)"
        ).order("score", desc=True).limit(10).execute()
        
        leaderboard_data = res.data or []
        
        if not leaderboard_data:
            st.info("📊 No quiz attempts yet. Be the first to appear on the leaderboard!")
            return
        
        # Display leaderboard
        st.markdown("### Top Performers 🏅")
        st.markdown("---")
        
        for i, entry in enumerate(leaderboard_data, 1):
            username = entry.get("users", {}).get("username", "Unknown")
            subject_name = entry.get("subjects", {}).get("name", "Unknown Subject")
            score = entry.get('score', 0)
            correct = entry.get('correct_answers', 0)
            total = entry.get('total_questions', 0)
            
            # Medal emojis for top 3
            medal = ""
            if i == 1: medal = "🥇"
            elif i == 2: medal = "🥈"
            elif i == 3: medal = "🥉"
            
            with st.container():
                col1, col2, col3, col4, col5 = st.columns([1, 3, 3, 2, 2])
                
                with col1:
                    st.markdown(f"**{medal} #{i}**")
                with col2:
                    st.markdown(f"**{username}**")
                with col3:
                    st.markdown(f"*{subject_name}*")
                with col4:
                    st.markdown(f"**{score:.1f}%**")
                with col5:
                    st.markdown(f"({correct}/{total})")
                
                st.markdown("---")
                
    except Exception as e:
        st.error(f"❌ Error loading leaderboard: {str(e)}")
    
    if st.button("⬅️ Back to Dashboard", use_container_width=True):
        st.session_state.current_page = "Dashboard"
        st.rerun()

def sidebar():
    """Sidebar navigation"""
    with st.sidebar:
        st.markdown("## 🎓 eduQuizPortal")
        st.markdown("---")
        
        if st.session_state.authenticated:
            st.markdown(f"**Welcome, {st.session_state.user['username']}!**")
            st.markdown(f"*Role: {st.session_state.user['role'].title()}*")
            st.markdown("---")
            
            # Navigation - Same for both but different features available
            pages = ["Dashboard", "Leaderboard"]
            
            if st.session_state.user["role"] == "student":
                pages.extend(["Take Quiz", "My Results"])
            
            for page in pages:
                if st.button(f"📊 {page}" if page == "Dashboard" else f"🏆 {page}" if page == "Leaderboard" else f"📝 {page}" if page == "Take Quiz" else f"📈 {page}", use_container_width=True, key=f"nav_{page}"):
                    st.session_state.current_page = page
                    st.rerun()
            
            st.markdown("---")
            
            if st.button("🚪 Logout", use_container_width=True):
                st.session_state.authenticated = False
                st.session_state.user = None
                st.session_state.current_page = "Login"
                st.session_state.quiz_started = False
                st.session_state.current_questions = []
                st.session_state.current_answers = {}
                st.session_state.quiz_submitted = False
                st.rerun()
        else:
            st.markdown("### Get Started")
            st.markdown("Login to access all features and start your learning journey!")

def main():
    """Main application"""
    load_css()
    initialize_session_state()
    sidebar()
    
    # Route to current page
    pages = {
        "Login": login_section,
        "Register": register_section, 
        "Dashboard": dashboard_section,
        "Take Quiz": take_quiz_section,
        "My Results": view_attempts_section,
        "Leaderboard": leaderboard_section
    }
    
    current_page = st.session_state.current_page
    if current_page in pages:
        pages[current_page]()
    else:
        st.session_state.current_page = "Login"
        st.rerun()

if __name__ == "__main__":
    main()