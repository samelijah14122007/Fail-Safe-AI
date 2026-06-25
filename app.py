import pickle

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from components import (
    divider,
    load_css,
    metric_tile,
    page_header,
    persona_banner,
    risk_gauge,
    risk_pill,
    section_label,
)

# ============================================================
# PAGE CONFIG  (must run before any other st.* call)
# ============================================================
st.set_page_config(
    page_title="FailSafe AI",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)
load_css("style.css")

# ============================================================
# MODEL  (unchanged logic: G1, G2, absences, studytime, failures -> Risk)
# ============================================================
with open("model.pkl", "rb") as f:
    model = pickle.load(f)

FEATURE_COLUMNS = ["G1", "G2", "absences", "studytime", "failures"]


def predict_risk(g1, g2, absences, studytime, failures):
    """Same inference contract as the original app: returns (label, confidence_pct)."""
    row = pd.DataFrame(
        [[g1, g2, absences, studytime, failures]], columns=FEATURE_COLUMNS
    )
    label = model.predict(row)[0]
    proba = model.predict_proba(row)[0]
    confidence = round(max(proba) * 100)
    return label, confidence


def compute_risk_score(attendance, marks, assignments, study_hours, gpa):
    """Same weighted formula as the original app, clamped to a 0-100 display range
    (the original app only clamped the progress bar, not the raw risk number)."""
    risk = (
        (100 - attendance) * 0.30
        + (100 - marks) * 0.30
        + (100 - assignments) * 0.20
        + (30 - study_hours) * 0.10
        + (10 - gpa) * 4
    )
    return max(0, min(100, round(risk)))


# ============================================================
# SIDEBAR — IDENTITY RAIL
# ============================================================
with st.sidebar:
    st.markdown(
        '<div class="fs-eyebrow">STUDENT SUCCESS INTELLIGENCE</div>'
        '<div class="fs-h1" style="font-size:1.6rem;">🎓 FailSafe AI</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="fs-sub" style="font-size:0.85rem;">'
        "Turn academic signals into early warnings and clear next steps."
        "</div>",
        unsafe_allow_html=True,
    )
    divider()

    role_choice = st.radio(
        "Sign in as",
        ["👨‍🎓 Student", "👩‍🏫 Faculty"],
        label_visibility="visible",
    )

    divider()
    st.markdown(
        '<div class="fs-section-label">SYSTEM</div>'
        '<div style="color:#94A3B8; font-size:0.78rem; line-height:1.6;">'
        "Model: Random Forest Classifier<br>"
        "Inputs: G1 · G2 · Absences · Study Time · Failures<br>"
        "Outputs: Low / Medium / High risk band"
        "</div>",
        unsafe_allow_html=True,
    )

st.session_state.setdefault("analyzed", False)

# ============================================================
# FACULTY DASHBOARD
# ============================================================
if role_choice == "👩‍🏫 Faculty":
    page_header(
        "FACULTY CONSOLE",
        "Faculty Dashboard",
        "Screen a student in seconds using attendance and internal marks.",
    )
    divider()

    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown('<div class="fs-card">', unsafe_allow_html=True)
        section_label("FACULTY")
        teacher_name = st.text_input("Faculty name", key="teacher_name")
        st.markdown("</div>", unsafe_allow_html=True)
    with col_b:
        st.markdown('<div class="fs-card">', unsafe_allow_html=True)
        section_label("STUDENT")
        student_name_f = st.text_input("Student name", key="student_name_faculty")
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="fs-card">', unsafe_allow_html=True)
    section_label("QUICK SCREEN")
    c1, c2 = st.columns(2)
    with c1:
        attendance_f = st.slider("Attendance (%)", 0, 100, 75, key="faculty_attendance")
    with c2:
        marks_f = st.slider("Marks (%)", 0, 100, 60, key="faculty_marks")

    analyze_faculty = st.button("Analyze student", key="faculty_btn")
    st.markdown("</div>", unsafe_allow_html=True)

    if analyze_faculty:
        name_display = student_name_f or "This student"
        if attendance_f >= 85 and marks_f >= 75:
            level, title, desc = (
                "low",
                "On track",
                f"{name_display} is performing well — attendance and marks are both healthy.",
            )
        elif attendance_f >= 60 and marks_f >= 50:
            level, title, desc = (
                "medium",
                "Needs mentoring",
                f"{name_display} is borderline. Light-touch mentoring now can prevent slippage.",
            )
        else:
            level, title, desc = (
                "high",
                "Needs intervention",
                f"{name_display} requires immediate academic intervention.",
            )

        st.markdown(persona_banner(level, title, desc), unsafe_allow_html=True)

# ============================================================
# STUDENT DASHBOARD
# ============================================================
else:
    page_header(
        "PERSONAL DASHBOARD",
        "Student Dashboard",
        "Enter your numbers once — get a risk read, a recovery plan, and a roadmap.",
    )
    divider()

    student_name = st.text_input("👤 Your name", key="student_name")

    col_left, col_right = st.columns(2, gap="large")

    with col_left:
        st.markdown('<div class="fs-card">', unsafe_allow_html=True)
        section_label("AI PREDICTION INPUTS")
        g1 = st.slider("First internal mark — G1", 0, 20, 10)
        g2 = st.slider("Second internal mark — G2", 0, 20, 10)
        absences = st.slider("Absences", 0, 100, 5)
        studytime = st.slider("Study time (1=low … 4=high)", 1, 4, 2)
        failures = st.slider("Previous failures", 0, 4, 0)
        st.markdown("</div>", unsafe_allow_html=True)

    with col_right:
        st.markdown('<div class="fs-card">', unsafe_allow_html=True)
        section_label("STUDENT DETAILS")
        attendance = st.slider("Attendance (%)", 0, 100, 75)
        marks = st.slider("Internal marks (%)", 0, 100, 60)
        assignments = st.slider("Assignment completion (%)", 0, 100, 70)
        study_hours = st.slider("Study hours per week", 0, 30, 10)
        gpa = st.slider("Previous GPA", 0.0, 10.0, 7.0)
        st.markdown("</div>", unsafe_allow_html=True)

    divider()
    analyze_clicked = st.button("🔍 Analyze student")
    if analyze_clicked:
        st.session_state["analyzed"] = True

    # --------------------------------------------------------
    # RESULTS (persist across reruns once analyzed)
    # --------------------------------------------------------
    if st.session_state["analyzed"]:
        greeting_name = student_name or "there"
        st.success(f"👋 Hi {greeting_name}, here's your read.")

        prediction, confidence = predict_risk(g1, g2, absences, studytime, failures)
        risk = compute_risk_score(attendance, marks, assignments, study_hours, gpa)
        health_score = max(0, 100 - risk)

        level_map = {0: "low", 1: "medium", 2: "high"}
        pred_level = level_map.get(prediction, "medium")

        # ---- Top row: AI verdict + gauge ----
        st.markdown('<div class="fs-card">', unsafe_allow_html=True)
        section_label("AI RISK PREDICTION")
        gcol1, gcol2 = st.columns([1, 1.4])
        with gcol1:
            st.markdown(
                f'<div class="fs-gauge-wrap">{risk_gauge(risk)}'
                f'<div class="fs-gauge-caption">CONFIDENCE {confidence}%</div></div>',
                unsafe_allow_html=True,
            )
        with gcol2:
            st.markdown(risk_pill(pred_level), unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown(
                f"""
                <div class="fs-metric-grid">
                    {metric_tile("Risk Score", f"{risk}%", "accent" if risk >= 60 else "")}
                    {metric_tile("Academic Health", f"{health_score}/100", "good" if health_score >= 60 else "")}
                    {metric_tile("Model Confidence", f"{confidence}%")}
                </div>
                """,
                unsafe_allow_html=True,
            )
        st.markdown("</div>", unsafe_allow_html=True)

        # ---- Persona ----
        if risk < 30:
            persona_html = persona_banner(
                "low", "Consistent Performer",
                "Your numbers are steady. Keep the current routine going.",
            )
        elif risk < 60:
            persona_html = persona_banner(
                "medium", "Recoverable Learner",
                "A few targeted changes now will move you back into safe territory.",
            )
        else:
            persona_html = persona_banner(
                "high", "At-Risk Learner",
                "Multiple factors are pulling your score down — act on the recovery plan below.",
            )
        st.markdown(persona_html, unsafe_allow_html=True)

        divider()

        # ---- Failure DNA ----
        st.markdown('<div class="fs-card">', unsafe_allow_html=True)
        section_label("ACADEMIC INSIGHT BREAKDOWN")

        attendance_issue = max(0, 100 - attendance)
        marks_issue = max(0, 100 - marks)
        assignment_issue = max(0, 100 - assignments)
        study_issue = max(0, 30 - study_hours)
        total = attendance_issue + marks_issue + assignment_issue + study_issue or 1

        breakdown_col, chart_col = st.columns([1, 1.2])
        with breakdown_col:
            for label_txt, val in [
                ("Attendance issues", attendance_issue),
                ("Marks issues", marks_issue),
                ("Assignment issues", assignment_issue),
                ("Study habit issues", study_issue),
            ]:
                pct = round(val / total * 100)
                st.markdown(
                    f"""
                    <div style="margin-bottom:0.7rem;">
                      <div style="display:flex; justify-content:space-between; font-size:0.85rem; color:#E7ECF5;">
                        <span>{label_txt}</span><span style="color:#F5A524; font-family:'JetBrains Mono', monospace;">{pct}%</span>
                      </div>
                      <div style="background:#0F1729; border-radius:6px; height:8px; margin-top:4px;">
                        <div style="background:#F5A524; width:{pct}%; height:8px; border-radius:6px;"></div>
                      </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

        with chart_col:
            df_breakdown = pd.DataFrame(
                {
                    "Factor": ["Attendance", "Marks", "Assignments", "Study Hours"],
                    "Impact": [attendance_issue, marks_issue, assignment_issue, study_issue],
                }
            )
            fig = px.pie(
                df_breakdown,
                values="Impact",
                names="Factor",
                hole=0.55,
                color_discrete_sequence=["#F5A524", "#FB7185", "#2DD4BF", "#60A5FA"],
            )
            fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font_color="#E7ECF5",
                legend=dict(orientation="h", y=-0.15),
                margin=dict(t=10, b=10, l=10, r=10),
                height=300,
            )
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        st.markdown("</div>", unsafe_allow_html=True)

        divider()

        # ---- Timeline + Recovery plan ----
        tcol, rcol = st.columns(2, gap="large")
        with tcol:
            st.markdown('<div class="fs-card">', unsafe_allow_html=True)
            section_label("PREDICTED FAILURE TIMELINE")
            timeline_items = [
                ("WK 01", "Minor academic warning"),
                ("WK 04", "Performance decline"),
                ("WK 08", "Internal marks reduction"),
                ("WK 12", "High risk of backlog"),
            ]
            tl_html = '<div class="fs-timeline">'
            for week, text in timeline_items:
                tl_html += (
                    f'<div class="fs-tl-item">'
                    f'<span class="fs-tl-week">{week}</span>'
                    f'<span class="fs-tl-text">{text}</span></div>'
                )
            tl_html += "</div>"
            st.markdown(tl_html, unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

        with rcol:
            st.markdown('<div class="fs-card">', unsafe_allow_html=True)
            section_label("RECOVERY PLAN")
            recs = []
            if attendance < 75:
                recs.append("Increase attendance above 80%")
            if marks < 60:
                recs.append("Focus on weak subjects")
            if assignments < 80:
                recs.append("Complete assignments on time")
            if study_hours < 10:
                recs.append("Increase weekly study hours")
            if gpa < 7:
                recs.append("Attend mentoring sessions")

            if recs:
                check_html = "".join(
                    f'<div class="fs-check"><span class="fs-check-mark">✓</span><span>{r}</span></div>'
                    for r in recs
                )
                st.markdown(check_html, unsafe_allow_html=True)
            else:
                st.markdown(
                    '<div style="color:#94A3B8; font-size:0.9rem;">No flags raised — current routine is on track.</div>',
                    unsafe_allow_html=True,
                )
            st.markdown("</div>", unsafe_allow_html=True)

        divider()

        # ---- What-if simulator ----
        st.markdown('<div class="fs-card">', unsafe_allow_html=True)
        section_label("WHAT-IF SIMULATOR")
        st.caption("Projected effect of +15% attendance and +15% marks, all else equal.")

        future_attendance = min(attendance + 15, 100)
        future_marks = min(marks + 15, 100)
        future_risk = compute_risk_score(future_attendance, future_marks, assignments, study_hours, gpa)
        improvement = risk - future_risk

        wcol1, wcol2, wcol3 = st.columns(3)
        with wcol1:
            st.markdown(metric_tile("Current Risk", f"{risk}%"), unsafe_allow_html=True)
        with wcol2:
            st.markdown(metric_tile("Improved Risk", f"{future_risk}%", "good"), unsafe_allow_html=True)
        with wcol3:
            st.markdown(metric_tile("Potential Drop", f"{improvement}%", "accent"), unsafe_allow_html=True)

        fig2 = go.Figure(
            go.Bar(
                x=["Current", "Improved"],
                y=[risk, future_risk],
                marker_color=["#FB7185" if risk >= 60 else "#F5A524", "#2DD4BF"],
                width=[0.45, 0.45],
                text=[f"{risk}%", f"{future_risk}%"],
                textposition="outside",
            )
        )
        fig2.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_color="#E7ECF5",
            yaxis=dict(range=[0, 100], gridcolor="#233047"),
            margin=dict(t=20, b=10, l=10, r=10),
            height=260,
            showlegend=False,
        )
        st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False})
        st.markdown("</div>", unsafe_allow_html=True)

    # --------------------------------------------------------
    # RESUME BOOSTER
    # --------------------------------------------------------
    divider()
    st.markdown('<div class="fs-card">', unsafe_allow_html=True)
    section_label("RESUME BOOSTER")
    resume_score = 70
    rb_col1, rb_col2 = st.columns([1, 2])
    with rb_col1:
        st.markdown(metric_tile("Resume Strength", f"{resume_score}/100", "accent"), unsafe_allow_html=True)
    with rb_col2:
        st.markdown(
            "".join(
                f'<div class="fs-check"><span class="fs-check-mark">✓</span><span>{item}</span></div>'
                for item in [
                    "Complete at least one internship",
                    "Build and publish projects on GitHub",
                    "Earn an industry certification",
                    "Participate in hackathons",
                ]
            ),
            unsafe_allow_html=True,
        )
    st.markdown("</div>", unsafe_allow_html=True)

    # --------------------------------------------------------
    # SEMESTER INTELLIGENCE
    # --------------------------------------------------------
    divider()
    st.markdown('<div class="fs-card">', unsafe_allow_html=True)
    section_label("SEMESTER INTELLIGENCE ENGINE")

    year = st.selectbox("Current year", ["1st Year", "2nd Year", "3rd Year", "4th Year"])

    year_focus = {
        "1st Year": ["Python Fundamentals", "C Programming", "Problem Solving", "Git & GitHub"],
        "2nd Year": ["Data Structures & Algorithms", "SQL", "Python for Data Science", "Machine Learning Basics"],
        "3rd Year": ["Deep Learning", "NLP", "Computer Vision", "MLOps"],
        "4th Year": ["System Design", "Advanced AI", "Research Projects", "Placement Preparation"],
    }
    project_ideas = [
        "Resume Analyzer",
        "Student Performance Predictor",
        "AI Interview Coach",
        "Attendance Intelligence System",
    ]

    fcol, pcol = st.columns(2, gap="large")
    with fcol:
        st.markdown('<div class="fs-section-label">FOCUS THIS YEAR</div>', unsafe_allow_html=True)
        st.markdown(
            "".join(
                f'<div class="fs-check"><span class="fs-check-mark">✓</span><span>{item}</span></div>'
                for item in year_focus[year]
            ),
            unsafe_allow_html=True,
        )
    with pcol:
        st.markdown('<div class="fs-section-label">SUGGESTED PROJECT IDEAS</div>', unsafe_allow_html=True)
        st.markdown(
            "".join(
                f'<div class="fs-check"><span class="fs-check-mark">🚀</span><span>{item}</span></div>'
                for item in project_ideas
            ),
            unsafe_allow_html=True,
        )
    st.markdown("</div>", unsafe_allow_html=True)

    # --------------------------------------------------------
    # CAREER GUIDANCE HUB
    # --------------------------------------------------------
    divider()
    st.markdown('<div class="fs-card">', unsafe_allow_html=True)
    section_label("CAREER GUIDANCE HUB (OPTIONAL)")

    with st.expander("📚 Explore skills, courses & career roadmap by department"):
        department = st.selectbox(
            "Select your department",
            [
                "AI & Data Science",
                "Computer Science Engineering",
                "Information Technology",
                "Electronics & Communication Engineering",
                "VLSI Design",
                "Mechanical Engineering",
                "Civil Engineering",
            ],
        )

        roadmaps = {
            "AI & Data Science": {
                "skills": ["Python", "SQL", "Data Structures & Algorithms", "Machine Learning", "Deep Learning", "Git & GitHub"],
                "courses": ["Machine Learning", "Data Analytics", "Generative AI", "Prompt Engineering"],
                "projects": ["Student Performance Predictor", "AI Resume Analyzer", "Fake News Detector"],
                "careers": ["AI Engineer", "Data Scientist", "ML Engineer"],
            },
            "Computer Science Engineering": {
                "skills": ["C++", "Java", "DSA", "DBMS", "Operating Systems"],
                "courses": [],
                "projects": ["Library Management System", "Full Stack Web App", "Online Code Compiler"],
                "careers": [],
            },
            "Information Technology": {
                "skills": ["HTML/CSS", "JavaScript", "React", "SQL", "Cloud Basics"],
                "courses": [],
                "projects": [],
                "careers": [],
            },
            "Electronics & Communication Engineering": {
                "skills": ["Embedded C", "Arduino", "IoT", "PCB Design"],
                "courses": [],
                "projects": [],
                "careers": [],
            },
            "VLSI Design": {
                "skills": ["Verilog", "VHDL", "FPGA", "Digital IC Design"],
                "courses": [],
                "projects": [],
                "careers": [],
            },
            "Mechanical Engineering": {
                "skills": ["AutoCAD", "SolidWorks", "Thermodynamics", "Manufacturing Processes"],
                "courses": [],
                "projects": [],
                "careers": [],
            },
            "Civil Engineering": {
                "skills": ["AutoCAD", "STAAD Pro", "Structural Analysis", "Project Management"],
                "courses": [],
                "projects": [],
                "careers": [],
            },
        }

        data = roadmaps[department]

        def render_group(title, items):
            if not items:
                return ""
            rows = "".join(
                f'<div class="fs-check"><span class="fs-check-mark">✓</span><span>{i}</span></div>'
                for i in items
            )
            return f'<div class="fs-section-label">{title}</div>{rows}'

        group_cols = st.columns(2)
        groups = [
            ("SKILLS TO LEARN", data["skills"]),
            ("RECOMMENDED COURSES", data["courses"]),
            ("PROJECT IDEAS", data["projects"]),
            ("CAREER PATHS", data["careers"]),
        ]
        for i, (title, items) in enumerate(groups):
            if not items:
                continue
            with group_cols[i % 2]:
                st.markdown(render_group(title, items), unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

# ============================================================
# FOOTER
# ============================================================
st.markdown(
    '<div class="fs-footer">FAILSAFE AI · STUDENT SUCCESS INTELLIGENCE PLATFORM</div>',
    unsafe_allow_html=True,
)
