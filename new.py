import pickle
import re

import joblib
import numpy as np
import streamlit as st
import pandas as pd
import plotly.express as px
from cassandra.auth import PlainTextAuthProvider
from cassandra.cluster import Cluster
from serpapi import GoogleSearch
import random
from Background import BackgroundCSSGenerator
st.set_page_config(
    page_title="Teacher Performance Tracker",
    page_icon="📊",  # You can replace this with an emoji or a URL to an image
    layout="wide"
)
img1_path = r"giphy.gif"
img2_path = r"giphy.gif"
background_generator = BackgroundCSSGenerator(img1_path, img2_path)
page_bg_img = background_generator.generate_background_css()
st.markdown(page_bg_img, unsafe_allow_html=True)
# Dummy user credentials
USER_CREDENTIALS = {
    "Management": {"username": "admin", "password": "admin123"},
    "Teacher": {"username": "teacher", "password": "teacher123"},
    "Student": {"username": "student", "password": "student123"}
}

# Initialize session state variables
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_role" not in st.session_state:
    st.session_state.user_role = None

# Path to secure connect bundle
cloud_config = {
    'secure_connect_bundle': 'secure-connect-college-data.zip'  # Update with your path
}



CLIENT_ID = st.secrets["CLIENT_ID"]
CLIENT_SECRET = st.secrets["CLIENT_SECRET"]




# Authentication provider
auth_provider = PlainTextAuthProvider(CLIENT_ID, CLIENT_SECRET)
cluster = Cluster(cloud=cloud_config, auth_provider=auth_provider)
session = cluster.connect()
session.set_keyspace('college_data')

ASTRA_TABLE = "teachers_copy"
model = joblib.load("teacher_performance_model.pkl")
le = joblib.load("label_encoder.pkl")

def get_faculty_data(name):
    result = session.execute(f"SELECT attendance, citations_count, hod_sentiment_score, publications, student_ratings, photo_url, position, department,hod_feedback FROM {ASTRA_TABLE} WHERE name=%s", (name,))
    return result.one()

def get_departments():
    result = session.execute(f"SELECT department FROM {ASTRA_TABLE}")
    departments = set(row.department for row in result if row.department)
    return list(departments)

# Logout function
def logout():
    st.session_state.logged_in = False
    st.session_state.user_role = None
    st.rerun()

def fetch_research_data(name):
    API_KEY = st.secrets["API_KEY"]

    params = {
        "engine": "google_scholar_profiles",
        "mauthors": name,
        "api_key": API_KEY
    }

    search = GoogleSearch(params)
    results = search.get_dict()
    profiles = results.get("profiles", [])

    if not profiles:
        return None, None

    profile = profiles[0]
    profile_link = profile['link']

    # Extract Author ID
    match = re.search(r"user=([\w-]+)", profile_link)
    if not match:
        return None, None

    author_id = match.group(1)
    publication_params = {
        "engine": "google_scholar_author",
        "author_id": author_id,
        "api_key": API_KEY
    }

    pub_search = GoogleSearch(publication_params)
    pub_results = pub_search.get_dict()
    articles = pub_results.get("articles", [])

    research_papers = []
    for article in articles[:5]:  # Fetch top 5 papers
        research_papers.append({
            "Title": article.get("title", "N/A"),
            "Year": article.get("year", "N/A"),
            "Journal": article.get("publication", "N/A"),
            "Citations": article.get("cited_by", {}).get("value", "N/A"),
            "Link": article.get("link", "N/A")
        })

    return profile_link, research_papers


def mangement_side_tab1():
    st.title("Faculty Performance Prediction")
    st.markdown("""
                        <hr style="border: 1px solid #dee2e6; margin: 20px 0;">
                        
                    """, unsafe_allow_html=True)    
    st.sidebar.header("Filters")

    # Sidebar Select box for departments

                        

                    

def mangement_side_tab1():
                    
                    if faculty:
                        col1, col2,col3 = st.columns(3)  # Adjust width ratio to ensure proper alignment

                        with col1:
                            st.image(faculty.photo_url, caption=f"**{selected_teacher}**", width=250)  # Adjust width for uniformity

                        with col2:
                            
                            st.markdown(f"""
                                    <div style="
                                        background: linear-gradient(135deg, #ffffff, #f8f9fa);
                                        border-radius: 12px;
                                        padding: 20px;
                                        box-shadow: 0px 5px 10px rgba(0, 0, 0, 0.1);
                                        font-family: Arial, sans-serif;
                                        text-align: left;
                                        width: 100%;
                                    ">
                                        <h3 style="color: #0d6efd; margin-bottom: 10px;">{selected_teacher}</h3>
                                        <p style="color: #495057; margin: 5px 0;"><strong>🎓 Position:</strong> {faculty.position}</p>
                                        <p style="color: #495057; margin: 5px 0;"><strong>🏛️ Department:</strong> {faculty.department}</p>
                                        <p style="color: #495057; margin: 5px 0;"><strong>📜 <a href="{profile_link}" target="_blank" style="color: #0d6efd; text-decoration: none;">Google Scholar Profile</a></strong></p>
                                    </div>
                                """, unsafe_allow_html=True)

                            
                        with col3:
                            st.markdown(f"""
                                <div style="
                                    background: linear-gradient(135deg, #e9ecef, #ffffff);
                                    border-radius: 12px;
                                    padding: 20px;
                                    box-shadow: 0px 5px 10px rgba(0, 0, 0, 0.1);
                                    font-family: Arial, sans-serif;
                                    text-align: left;
                                    width: 100%;
                                    margin-top: 15px;
                                ">
                                    <h3 style="color: #198754; font-size: 22px; font-weight: bold; text-align: center;">📊 Faculty Metrics</h3>
                                    <p style="color: #155724; font-size: 18px; margin: 12px 0;">
                                        <strong>✅ Attendance:</strong> {faculty.attendance}%
                                    </p>
                                    <p style="color: #155724; font-size: 18px; margin: 12px 0;">
                                        <strong>📄 Citations:</strong> {faculty.citations_count}
                                    </p>
                                    <p style="color: #155724; font-size: 18px; margin: 12px 0;">
                                        <strong>👨‍🏫 HOD Sentiment:</strong> {faculty.hod_sentiment_score:.2f}
                                    </p>
                                    <p style="color: #155724; font-size: 18px; margin: 12px 0;">
                                        <strong>📚 Publications:</strong> {faculty.publications}
                                    </p>
                                    <p style="color: #155724; font-size: 18px; margin: 12px 0;">
                                        <strong>⭐ Student Ratings:</strong> {faculty.student_ratings:.2f}
                                    </p>
                                </div>
                            """, unsafe_allow_html=True)
                            





                        # Performance Prediction
                        features = np.array([
                            faculty.attendance,
                            faculty.citations_count,
                            faculty.hod_sentiment_score,
                            faculty.publications,
                            faculty.student_ratings
                        ]).reshape(1, -1)

                        prediction = model.predict(features).flatten()
                        predicted_performance = le.inverse_transform(prediction)

                        st.markdown("""
                            <hr style="border: 1px solid #dee2e6; margin: 20px 0;">
                            <h3 style='text-align: center; color: #856404;'>🔮 Predicted Performance</h3>
                        """, unsafe_allow_html=True)

                        st.markdown(f"""
                            <div style="
                                background: #fff3cd;
                                border-radius: 12px;
                                padding: 20px;
                                text-align: center;
                                box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.1);
                                font-family: Arial, sans-serif;
                            ">
                                <h2 style="color: #d39e00;">{predicted_performance[0]}</h2>
                            </div>
                        """, unsafe_allow_html=True)

                    else:
                        st.warning("Faculty data not found. Try another name.")

                    
                    st.markdown("""
                            <hr style="border: 1px solid #dee2e6; margin: 20px 0;">
                            
                        """, unsafe_allow_html=True)
                    if research_papers:
                        with st.expander("Research Papers"):
                                # Create a table for research papers
                            st.table(research_papers)
                    else:
                        st.write("No research data found.")


def mangnagement_side_tab2():
    st.write("\n================================")
    
    if faculty:
        # Data for bar chart
        metrics = {
            "Publications": faculty.publications,
            "Attendance (%)": faculty.attendance,
            "Student Rating": faculty.student_ratings,
            "Citation Count": faculty.citations_count,
            "HOD Sentiment Score": faculty.hod_sentiment_score,
            "HOD Feedback Data": faculty.hod_feedback
        }

        df = pd.DataFrame(list(metrics.items()), columns=["Metric", "Value"])

        col1, col2 = st.columns(2)

        # Bar Chart
        with col1:
            fig_bar = px.bar(df, x="Metric", y="Value", 
                            color="Metric", 
                            title=f"📊 Performance Metrics for {selected_teacher}",
                            text="Value", 
                            color_discrete_sequence=px.colors.qualitative.Safe)

            fig_bar.update_traces(textposition="outside")
            fig_bar.update_layout(yaxis_title="Score", xaxis_title="Metrics", height=450)
            st.plotly_chart(fig_bar, use_container_width=True)
            st.subheader("📝 HOD Feedback")
            st.info(faculty.hod_feedback)  # Highlight feedback in a text box

        # Star Rating
        with col2:
            import plotly.graph_objects as go

            student_rating = faculty.student_ratings
            fig_star = go.Figure()

            for i in range(5):  
                fig_star.add_trace(go.Scatter(
                    x=[i + 1], y=[1],
                    marker=dict(
                        size=50,
                        symbol="star",
                        color="gold" if i < student_rating else "lightgray"
                    ),
                    mode="markers"
                ))

            fig_star.update_layout(
                title="⭐ Student Rating",
                xaxis=dict(showticklabels=False, showgrid=False, fixedrange=True),
                yaxis=dict(showticklabels=False, showgrid=False, range=[0, 2], fixedrange=True),
                height=150,  # Increased height
                margin=dict(l=20, r=20, t=40, b=20)
            )

            st.plotly_chart(fig_star, use_container_width=True)


        

            fig_pub_vs_cite = go.Figure()

            # Bar for Publications
            fig_pub_vs_cite.add_trace(go.Bar(
                x=["Publications"],
                y=[faculty.publications],
                name="Publications",
                marker_color="royalblue"
            ))

            # Bar for Citations
            fig_pub_vs_cite.add_trace(go.Bar(
                x=["Citations"],
                y=[faculty.citations_count],
                name="Citations",
                marker_color="orange"
            ))

            # Layout adjustments
            fig_pub_vs_cite.update_layout(
                title="📚 Publications vs Citations",
                barmode="group",  # Grouped bars for better comparison
                yaxis_title="Count",
                xaxis_title="Metric",
                height=400,
                margin=dict(l=20, r=20, t=40, b=20)
            )

            # Display in Streamlit
            st.plotly_chart(fig_pub_vs_cite, use_container_width=True)


def tabs(faculty, research_papers, profile_link,selected_teacher):
    tab1, tab2 = st.tabs(["Faculty Performance Prediction", "Metrics Dashboard"])
    print(type(tab1))  # This should print <class 'streamlit.delta_generator.DeltaGenerator'>

    with tab1:
        mangement_side_tab1()
    with tab2:
        mangnagement_side_tab2()




# Role-based access


# Login Page
if not st.session_state.logged_in:
    st.title("Login Page")
    role = st.selectbox("Select Role", ["Student", "Management", "Teacher"])
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if username == USER_CREDENTIALS[role]["username"] and password == USER_CREDENTIALS[role]["password"]:
            st.session_state.logged_in = True
            st.session_state.user_role = role
            st.success(f"Logged in as {role}")
            st.rerun()
        else:
            st.error("Invalid username or password. Try again.")

else:
    st.sidebar.button("Logout", on_click=logout)

    if st.session_state.user_role == "Management":
        st.title("Management Dashboard")
        departments = get_departments()
        selected_department = st.sidebar.selectbox("Select Department", departments)



        if selected_department:
            
                result = session.execute(f"""
                    SELECT name FROM {ASTRA_TABLE} WHERE department=%s ALLOW FILTERING
                """, (selected_department,))
                teacher_names = [row.name for row in result]

                selected_teacher = st.sidebar.selectbox("Select Teacher", teacher_names)

                if selected_teacher:
                    
                        faculty = get_faculty_data(selected_teacher)
                        profile_link, research_papers = fetch_research_data(selected_teacher)
                        tabs(faculty, research_papers, profile_link,selected_teacher)

    elif st.session_state.user_role == "Teacher":
        
        departments = get_departments()
        selected_department = st.sidebar.selectbox("Select Department", departments)



        if selected_department:
                teacher_courses = {
    "teacher_1": ["Data Structures", "Machine Learning"],
    "teacher_2": ["DBMS", "Operating Systems"]
}

                student_courses = {
        "student_1": ["Data Structures", "DBMS"],
        "student_2": ["Machine Learning", "Operating Systems"]
    }

                professors = ["Dr. Smith", "Dr. Johnson", "Prof. Lee", "Dr. Patel"]
                students = ["Alice", "Bob", "Charlie", "David"]
            
                result = session.execute(f"""
                    SELECT name FROM {ASTRA_TABLE} WHERE department=%s ALLOW FILTERING
                """, (selected_department,))
                teacher_names = [row.name for row in result]

                selected_teacher = st.sidebar.selectbox("Select Teacher", teacher_names)

                if selected_teacher:
                    
                        faculty = get_faculty_data(selected_teacher)
                        profile_link, research_papers = fetch_research_data(selected_teacher)
                        st.title("📚 Teacher Dashboard")
                        st.write(f"Welcome, {selected_teacher} ! Manage your courses and student performance here.")

                        # Display Assigned Courses
                        teacher_id = "teacher_1"
                        assigned_courses = teacher_courses.get(teacher_id, [])

                        if assigned_courses:
                            st.subheader("📖 Your Assigned Courses")
                            for course in assigned_courses:
                                st.write(f"- {course}")

                            # View Student Performance
                            st.subheader("📊 Student Performance")
                            selected_course = st.selectbox("Select Course", assigned_courses)
                            if selected_course:
                                student_data = pd.DataFrame({
                                    "Student Name": students,
                                    "Attendance (%)": [random.randint(60, 100) for _ in students],
                                    "Performance Score": [random.randint(50, 100) for _ in students]
                                })
                                st.dataframe(student_data)

                            # Provide Feedback on Students
                            st.subheader("📝 Provide Feedback")
                            selected_student = st.selectbox("Select Student", students)
                            feedback = st.text_area(f"Feedback for {selected_student}")

                            if st.button("Submit Feedback"):
                                st.success(f"Feedback for {selected_student} submitted successfully!")
                                st.toast(f"Feedback for {selected_student} submitted successfully!")

    elif st.session_state.user_role == "Student":

        teacher_courses = {
    "teacher_1": ["Data Structures", "Machine Learning"],
    "teacher_2": ["DBMS", "Operating Systems"]
}

        student_courses = {
    "student_1": ["Data Structures", "DBMS"],
    "student_2": ["Machine Learning", "Operating Systems"]
}

        professors = ["Dr. Smith", "Dr. Johnson", "Prof. Lee", "Dr. Patel"]
        students = ["Alice", "Bob", "Charlie", "David"]
        departments = get_departments()
        selected_department = st.sidebar.selectbox("Select Department", departments)



        if selected_department:
            
                result = session.execute(f"""
                    SELECT name FROM {ASTRA_TABLE} WHERE department=%s ALLOW FILTERING
                """, (selected_department,))
                teacher_names = [row.name for row in result]

                selected_teacher = st.sidebar.selectbox("Select Teacher", teacher_names)

                if selected_teacher:
                    
                        faculty = get_faculty_data(selected_teacher)
                        profile_link, research_papers = fetch_research_data(selected_teacher)
                        st.title("🎓 Student Dashboard")
                        st.write("Welcome, Student! Manage your courses and rate teachers here.")

                        # Display Enrolled Courses
                        student_id = "student_1"
                        enrolled_courses = student_courses.get(student_id, [])

                        if enrolled_courses:
                            st.subheader("📖 Your Enrolled Courses")
                            for course in enrolled_courses:
                                st.write(f"- {course}")

                            # Rate Professors
                            st.subheader("⭐ Rate Your Professors")
                            
                            rating = st.slider(f"Rate {selected_teacher} (Out of 5)", 1, 5, 3)

                            if st.button("Submit Feedback"):
                                st.success(f"Your feedback for {selected_teacher} has been submitted!")
                                st.toast(f"Your feedback for {selected_teacher} has been submitted!")
                                st.balloons()

                            st.subheader("enter teacher feedback")
                            st.text_input(f"enter feedback for {selected_teacher}")
                            if st.button("Submit Rating"):
                                st.success(f"Your rating for {selected_teacher} has been submitted!")
                                st.toast(f"Your rating for {selected_teacher} has been submitted!")
                                st.balloons()
