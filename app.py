import sqlite3
from pathlib import Path
import pandas as pd
import streamlit as st

APP_DIR = Path(__file__).parent
DB_PATH = APP_DIR / "classact.db"

st.set_page_config(
    page_title="ClassAct | Student Grade Manager",
    page_icon="🎓",
    layout="wide",
   
)


def connect():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db():
    with connect() as conn:
        conn.executescript("""
        CREATE TABLE IF NOT EXISTS students (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            section TEXT NOT NULL DEFAULT ''
        );
        CREATE TABLE IF NOT EXISTS subjects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
        );
        CREATE TABLE IF NOT EXISTS grade_scheme (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            min REAL NOT NULL,
            max REAL NOT NULL
        );
        CREATE TABLE IF NOT EXISTS grades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT NOT NULL,
            subject TEXT NOT NULL,
            assessment TEXT NOT NULL DEFAULT 'Assessment',
            score REAL NOT NULL CHECK(score >= 0 AND score <= 100),
            FOREIGN KEY(student_id) REFERENCES students(id) ON DELETE CASCADE
        );
        """)
        
        count = conn.execute("SELECT COUNT(*) FROM students").fetchone()[0]
        if count == 0:
            conn.executemany("INSERT INTO students(id,name,section) VALUES(?,?,?)", [
                ("MMCM-2026-001", "Angela Reyes", "BSIT 2A"),
                ("MMCM-2026-002", "Joshua Santos", "BSIT 2A"),
                ("MMCM-2026-003", "Mikaela Cruz", "BSIT 2A"),
                ("MMCM-2026-004", "Daniel Garcia", "BSIT 2B"),
            ])
            conn.executemany("INSERT INTO subjects(name) VALUES(?)", [
                ("Programming",), ("Database Systems",), ("Web Development",), ("Systems Analysis",)
            ])
            conn.executemany("INSERT INTO grade_scheme(name,min,max) VALUES(?,?,?)", [
                ("1.0",96.01,100), ("1.25",91.51,96.00), ("1.5",87.01,91.50),
                ("1.75",82.51,87.00), ("2.0",78.01,82.50), ("2.25",73.51,78.00),
                ("2.5",69.01,73.50), ("2.75",64.515,69.00), ("3.0",60,64.514),
                ("IP",0,59.999), ("INC",101,200), ("5",201,300), ("3.0*",301,400), ("ABS",401,500)
            ])
            conn.executemany("INSERT INTO grades(student_id,subject,assessment,score) VALUES(?,?,?,?)", [
                ("MMCM-2026-001","Programming","Quiz 1",94),
                ("MMCM-2026-001","Database Systems","Midterm Exam",88),
                ("MMCM-2026-002","Programming","Quiz 1",82),
                ("MMCM-2026-002","Web Development","Project 1",91),
                ("MMCM-2026-003","Database Systems","Midterm Exam",96),
                ("MMCM-2026-003","Systems Analysis","Case Study",89),
                ("MMCM-2026-004","Programming","Quiz 1",58),
                ("MMCM-2026-004","Web Development","Project 1",67),
            ])

def query_df(sql, params=()):
    with connect() as conn:
        return pd.read_sql_query(sql, conn, params=params)

def execute(sql, params=()):
    with connect() as conn:
        conn.execute(sql, params)
        conn.commit()

def grade_for(score):
    bands = query_df("SELECT name,min,max FROM grade_scheme ORDER BY min DESC")
    found = bands[(bands["min"] <= score) & (bands["max"] >= score)]
    return str(found.iloc[0]["name"]) if not found.empty else "—"

def student_average(student_id):
    row = query_df("SELECT AVG(score) AS avg FROM grades WHERE student_id=?", (student_id,))
    return None if pd.isna(row.iloc[0]["avg"]) else float(row.iloc[0]["avg"])

def get_students():
    return query_df("""
        SELECT s.id, s.name, s.section, AVG(g.score) AS average, COUNT(g.id) AS entries
        FROM students s LEFT JOIN grades g ON g.student_id=s.id
        GROUP BY s.id ORDER BY s.name
    """)

def get_grades():
    df = query_df("""SELECT g.id, s.name AS student, g.student_id, s.section, g.subject,
                     g.assessment, g.score
                     FROM grades g JOIN students s ON s.id=g.student_id ORDER BY g.id DESC""")
    if not df.empty:
        df["Grade"] = df["score"].apply(grade_for)
        df["score"] = df["score"].map(lambda x: f"{x:.2f}%")
    return df

init_db()


st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
html, body, [class*="css"] { font-family: Inter, sans-serif; }
.stApp { background: #f6f7fc; }
section[data-testid="stSidebar"] { background: #fff; border-right: 1px solid #ececf3; }
.brand {display:flex;align-items:center;gap:11px;padding:5px 0 20px;border-bottom:1px solid #ececf3;margin-bottom:20px}
.brand-icon {background:linear-gradient(135deg,#a18af2,#7155d2);color:#fff;border-radius:11px;width:42px;height:42px;display:flex;align-items:center;justify-content:center;font-size:23px;font-weight:800}
.brand-title {font-size:22px;font-weight:800;color:#292b36;letter-spacing:-.5px}
.brand-sub {font-size:11px;color:#858ba1}
.page-title {font-size:27px;font-weight:750;letter-spacing:-.7px;color:#292b36;margin:0}
.page-sub {color:#858ba1;font-size:13px;margin-top:3px;margin-bottom:22px}
.metric-card {background:#fff;border:1px solid #ebebf3;border-radius:13px;padding:18px 20px;box-shadow:0 2px 6px #25254b08;min-height:118px}
.metric-label {font-size:13px;color:#777d91;margin-bottom:8px}
.metric-value {font-size:29px;font-weight:800;color:#292b36;letter-spacing:-.7px}
.metric-note {font-size:11px;color:#2da878;margin-top:4px}
.panel {background:#fff;border:1px solid #ebebf3;border-radius:13px;padding:20px;box-shadow:0 2px 6px #25254b08;margin-bottom:16px}
.panel-title {font-weight:700;font-size:16px;margin-bottom:3px;color:#292b36}
.panel-sub {font-size:12px;color:#858ba1;margin-bottom:15px}
div.stButton > button[kind="primary"] {background:#8267df;border-color:#8267df}
div.stButton > button {border-radius:9px}
div[data-testid="stDataFrame"] {border:1px solid #ececf3;border-radius:9px;overflow:hidden}
div[data-testid="stMetric"] {background:#fff;border:1px solid #ebebf3;padding:14px;border-radius:12px}
hr {border-color:#ececf3}
</style>
""", unsafe_allow_html=True)


with st.sidebar:
    st.markdown('<div class="brand"><div class="brand-icon">C</div><div><div class="brand-title">ClassAct</div><div class="brand-sub">Student Grade Manager</div></div></div>', unsafe_allow_html=True)
    page = st.radio("MAIN MENU", ["Dashboard", "Students", "Gradebook", "Subjects", "Reports"], label_visibility="visible")
    st.divider()
    st.caption("ClassAct - Grading System")



st.markdown(f'<div class="page-title">{page}</div>', unsafe_allow_html=True)
subtitles = {
    "Dashboard"
    "Students"
    "Gradebook"
    "Subjects"
    "Reports"
}


if page == "Dashboard":
    students_df = get_students()
    grades_df = query_df("SELECT * FROM grades")
    subjects_df = query_df("SELECT name FROM subjects ORDER BY name")
    avgs = students_df["average"].dropna()
    class_avg = float(avgs.mean()) if len(avgs) else 0
    passing = int((avgs >= 60).sum()) if len(avgs) else 0
    cols = st.columns(4)
    metrics = [
        ("Total Students", f"{len(students_df):,}", "Current class roster"),
        ("Subjects", f"{len(subjects_df):,}", "Active subjects"),
        ("Class Average", f"{class_avg:.1f}%" if len(avgs) else "—", "Average of student averages"),
        ("Passing Students", f"{passing:,}", "Passing mark: 60%"),
    ]
    for col, (label, value, note) in zip(cols, metrics):
        with col:
            st.markdown(f'<div class="metric-card"><div class="metric-label">{label}</div><div class="metric-value">{value}</div><div class="metric-note">{note}</div></div>', unsafe_allow_html=True)
    st.write("")
    left, right = st.columns([1.35, 1])
    with left:
        st.markdown('<div class="panel-title">Class Performance</div><div class="panel-sub">Average percentage by subject</div>', unsafe_allow_html=True)
        perf = query_df("SELECT subject, AVG(score) AS Average FROM grades GROUP BY subject ORDER BY subject")
        if not perf.empty:
            st.bar_chart(perf.set_index("subject"), y="Average", color="#8267df")
        else:
            st.info("Enter grades to see subject performance.")
    with right:
        st.markdown('<div class="panel-title">Grade Distribution</div><div class="panel-sub">Students grouped by overall average</div>', unsafe_allow_html=True)
        if not students_df.empty:
            valid = students_df.dropna(subset=["average"])
            bands = [
                ("Excellent · 90–100%", valid[(valid.average >= 90) & (valid.average <= 100)]),
                ("Good · 80–89.99%", valid[(valid.average >= 80) & (valid.average < 90)]),
                ("Satisfactory · 60–79.99%", valid[(valid.average >= 60) & (valid.average < 80)]),
                ("Needs support · below 60%", valid[valid.average < 60]),
            ]
            for label, group in bands:
                st.write(f"**{label}** · {len(group)}")
                st.progress(len(group) / max(len(students_df), 1))
    a, b = st.columns([1.25, 1])
    with a:
        st.markdown('<div class="panel-title">Recently Updated Grades</div><div class="panel-sub">Latest saved entries</div>', unsafe_allow_html=True)
        recent = get_grades().head(6)
        if recent.empty:
            st.info("No grades yet.")
        else:
            st.dataframe(recent[["student", "subject", "assessment", "score", "Grade"]], width='stretch', hide_index=True)
    with b:
        st.markdown('<div class="panel-title">Top Academic Progress</div><div class="panel-sub">Highest overall averages</div>', unsafe_allow_html=True)
        top = students_df.dropna(subset=["average"]).sort_values("average", ascending=False).head(5)
        if top.empty:
            st.info("Add grades to view top students.")
        else:
            for _, row in top.iterrows():
                st.write(f"**{row['name']}** · {row['average']:.2f}%")
                st.progress(min(float(row["average"]) / 100, 1.0))


elif page == "Students":
    with st.expander("＋ Add a student", expanded=False):
        with st.form("add_student", clear_on_submit=True):
            c1, c2 = st.columns(2)
            sid = c1.text_input("Student ID", placeholder="Enter Student ID")
            name = c2.text_input("Full name", placeholder="Enter Full Name")
            section = st.text_input("Section / Program", placeholder="Enter Section or Program")
            if st.form_submit_button("Save Student", type="primary"):
                if not sid.strip() or not name.strip():
                    st.error("Student ID and full name are required.")
                else:
                    try:
                        execute("INSERT INTO students(id,name,section) VALUES(?,?,?)", (sid.strip(), name.strip(), section.strip()))
                        st.success("Student saved to database.")
                        st.rerun()
                    except sqlite3.IntegrityError:
                        st.error("That student ID already exists.")
    sdf = get_students()
    q = st.text_input("Search students", placeholder="Search name, ID, or section")
    if q:
        sdf = sdf[sdf.astype(str).apply(lambda col: col.str.contains(q, case=False, na=False)).any(axis=1)]
    if not sdf.empty:
        view = sdf.copy()
        view["Overall Average"] = view["average"].apply(lambda x: f"{x:.2f}%" if pd.notna(x) else "—")
        view["Standing"] = view["average"].apply(lambda x: "No grades" if pd.isna(x) else ("Passing" if x >= 60 else "Needs support"))
        st.dataframe(view[["id","name","section","Overall Average","Standing","entries"]].rename(columns={"id":"Student ID","name":"Student","section":"Section","entries":"Grade Entries"}), width='stretch', hide_index=True)
        st.markdown("#### Edit or delete a student")
        options = {f"{r['name']} ({r['id']})": r["id"] for _, r in sdf.iterrows()}
        selected = st.selectbox("Select student", list(options))
        sid = options[selected]
        current = query_df("SELECT * FROM students WHERE id=?", (sid,)).iloc[0]
        with st.form("edit_student"):
            new_name = st.text_input("Name", value=current["name"])
            new_section = st.text_input("Section", value=current["section"])
            c1, c2 = st.columns(2)
            save_student = c1.form_submit_button("Update Student", type="primary")
            delete_student = c2.form_submit_button("Delete Student")
            if save_student:
                if not new_name.strip():
                    st.error("Name cannot be empty.")
                else:
                    execute("UPDATE students SET name=?,section=? WHERE id=?", (new_name.strip(), new_section.strip(), sid))
                    st.success("Student updated.")
                    st.rerun()
            if delete_student:
                execute("DELETE FROM grades WHERE student_id=?", (sid,))
                execute("DELETE FROM students WHERE id=?", (sid,))
                st.warning("Student and associated grades deleted.")
                st.rerun()
    else:
        st.info("No students match your search.")


elif page == "Gradebook":
    students_df = query_df("SELECT id,name FROM students ORDER BY name")
    subjects_df = query_df("SELECT name FROM subjects ORDER BY name")
    if students_df.empty or subjects_df.empty:
        st.warning("Add at least one student and one subject before entering grades.")
    else:
        with st.expander("＋ Enter a grade", expanded=True):
            with st.form("add_grade", clear_on_submit=True):
                c1, c2 = st.columns(2)
                student_map = {f"{r['name']} ({r['id']})": r["id"] for _, r in students_df.iterrows()}
                chosen_student = c1.selectbox("Student", list(student_map))
                chosen_subject = c2.selectbox("Subject", subjects_df["name"].tolist())
                assessment = st.text_input("Assessment name", placeholder="Quiz 1, Midterm Exam, Project")
                score = st.number_input("Score (%)", min_value=0.0, max_value=100.0, value=85.0, step=0.25)
                st.caption(f"Calculated grade: **{grade_for(score)}**")
                if st.form_submit_button("Save Grade", type="primary"):
                    execute("INSERT INTO grades(student_id,subject,assessment,score) VALUES(?,?,?,?)",
                            (student_map[chosen_student], chosen_subject, assessment.strip() or "Assessment", score))
                    st.success("Grade saved to SQLite database.")
                    st.rerun()
    gdf = get_grades()
    st.markdown("#### Grade entries")
    search = st.text_input("Filter grade entries", placeholder="Student, subject, or assessment")
    if search and not gdf.empty:
        mask = gdf.astype(str).apply(lambda col: col.str.contains(search, case=False, na=False)).any(axis=1)
        gdf = gdf[mask]
    if not gdf.empty:
        st.dataframe(gdf[["id","student","student_id","subject","assessment","score","Grade"]].rename(columns={"id":"Entry ID","student":"Student","student_id":"Student ID","subject":"Subject","assessment":"Assessment","score":"Score"}), width='stretch', hide_index=True)
        ids = gdf["id"].astype(int).tolist()
        entry_id = st.selectbox("Select entry to edit or delete", ids)
        record = query_df("SELECT * FROM grades WHERE id=?", (entry_id,)).iloc[0]
        with st.form("edit_grade"):
            c1, c2 = st.columns(2)
            edit_assessment = c1.text_input("Assessment", value=record["assessment"])
            edit_score = c2.number_input("Score (%)", min_value=0.0, max_value=100.0, value=float(record["score"]), step=0.25)
            c1, c2 = st.columns(2)
            update_grade = c1.form_submit_button("Update Grade", type="primary")
            remove_grade = c2.form_submit_button("Delete Grade")
            if update_grade:
                execute("UPDATE grades SET assessment=?,score=? WHERE id=?", (edit_assessment.strip() or "Assessment", edit_score, int(entry_id)))
                st.success("Grade updated.")
                st.rerun()
            if remove_grade:
                execute("DELETE FROM grades WHERE id=?", (int(entry_id),))
                st.warning("Grade entry deleted.")
                st.rerun()
    else:
        st.info("No grade entries found.")


elif page == "Subjects":
    with st.expander("＋ Add subject"):
        with st.form("add_subject", clear_on_submit=True):
            subject_name = st.text_input("Subject name", placeholder="e.g. Mathematics")
            if st.form_submit_button("Save Subject", type="primary"):
                if not subject_name.strip():
                    st.error("Subject name is required.")
                else:
                    try:
                        execute("INSERT INTO subjects(name) VALUES(?)", (subject_name.strip(),))
                        st.success("Subject saved.")
                        st.rerun()
                    except sqlite3.IntegrityError:
                        st.error("That subject already exists.")
    subjects_df = query_df("""SELECT s.name, COUNT(g.id) AS entries, AVG(g.score) AS average
                              FROM subjects s LEFT JOIN grades g ON g.subject=s.name GROUP BY s.id ORDER BY s.name""")
    if not subjects_df.empty:
        for _, row in subjects_df.iterrows():
            c1, c2, c3 = st.columns([3, 2, 1])
            c1.write(f"**{row['name']}**")
            c2.caption(f"{row['entries']} grade entries" + (f" · avg {row['average']:.1f}%" if pd.notna(row["average"]) else ""))
            if c3.button("Delete", key=f"del_sub_{row['name']}"):
                execute("DELETE FROM grades WHERE subject=?", (row["name"],))
                execute("DELETE FROM subjects WHERE name=?", (row["name"],))
                st.warning("Subject and its grade entries deleted.")
                st.rerun()
            st.divider()
    else:
        st.info("No subjects yet.")


elif page == "Reports":
    gdf = query_df("""SELECT s.name AS Student, s.id AS Student_ID, s.section AS Section,
                      g.subject AS Subject, g.assessment AS Assessment, g.score AS Score
                      FROM grades g JOIN students s ON s.id=g.student_id ORDER BY s.name, g.subject""")
    if gdf.empty:
        st.info("No grade records available to report.")
    else:
        avg = gdf["Score"].mean()
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Grade Entries", len(gdf))
        c2.metric("Average Score", f"{avg:.2f}%")
        c3.metric("Highest Score", f"{gdf['Score'].max():.2f}%")
        c4.metric("Lowest Score", f"{gdf['Score'].min():.2f}%")
        gdf["Grade"] = gdf["Score"].apply(grade_for)
        st.dataframe(gdf, width='stretch', hide_index=True)
        csv = gdf.to_csv(index=False).encode("utf-8")
        st.download_button("Download report as CSV", data=csv, file_name="classact-grade-report.csv", mime="text/csv", type="primary")
        st.markdown("#### Student averages")
        averages = get_students().dropna(subset=["average"])[["name","id","section","average"]].rename(columns={"name":"Student","id":"Student ID","section":"Section","average":"Average %"})
        st.dataframe(averages, width='stretch', hide_index=True)

st.divider()
