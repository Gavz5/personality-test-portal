from __future__ import annotations

import csv
import io
import os
import sqlite3
from datetime import datetime
from functools import wraps
from pathlib import Path

from flask import (
    Flask,
    Response,
    flash,
    g,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from werkzeug.security import check_password_hash, generate_password_hash

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "personality_test.db"

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "change-this-secret-key")
app.config["ADMIN_USERNAME"] = os.environ.get("ADMIN_USERNAME", "admin")
app.config["ADMIN_PASSWORD_HASH"] = os.environ.get(
    "ADMIN_PASSWORD_HASH", generate_password_hash("admin123")
)

QUESTIONS = [
    {"id": 1, "section": "E/I", "dimension": ("E", "I"), "text": "In a virtual breakout room, do you:", "a": "Start the conversation immediately?", "b": "Listen first and contribute later?"},
    {"id": 2, "section": "E/I", "dimension": ("E", "I"), "text": "After a long day of work and online classes, do you:", "a": "Want to call a friend?", "b": "Need quiet time alone?"},
    {"id": 3, "section": "E/I", "dimension": ("E", "I"), "text": "Do you prefer working on:", "a": "Large, cross-functional teams?", "b": "Small groups or independent tasks?"},
    {"id": 4, "section": "E/I", "dimension": ("E", "I"), "text": "In meetings, do you:", "a": "Think out loud?", "b": "Reflect internally before speaking?"},
    {"id": 5, "section": "E/I", "dimension": ("E", "I"), "text": "Networking events make you feel:", "a": "Energized and excited.", "b": "Drained and ready to leave."},
    {"id": 6, "section": "E/I", "dimension": ("E", "I"), "text": "When solving a problem, do you:", "a": "Seek immediate feedback from others?", "b": "Process the logic privately first?"},
    {"id": 7, "section": "E/I", "dimension": ("E", "I"), "text": "Do you prefer a workspace that is:", "a": "Busy and interactive?", "b": "Private and calm?"},
    {"id": 8, "section": "E/I", "dimension": ("E", "I"), "text": "Are you more likely to:", "a": "Reach out to a classmate you don't know?", "b": "Wait for them to contact you?"},
    {"id": 9, "section": "E/I", "dimension": ("E", "I"), "text": "When leading a project, you focus on:", "a": "Motivating the group.", "b": "Perfecting the strategy."},
    {"id": 10, "section": "E/I", "dimension": ("E", "I"), "text": "In your career, do you value:", "a": "Wide-reaching visibility?", "b": "Deep, specialized expertise?"},
    {"id": 11, "section": "E/I", "dimension": ("E", "I"), "text": "On LinkedIn, are you more likely to:", "a": "Post updates and comments?", "b": "Silently observe and read?"},
    {"id": 12, "section": "E/I", "dimension": ("E", "I"), "text": "Do you find group brainstorming:", "a": "Stimulating?", "b": "Distracting?"},
    {"id": 13, "section": "E/I", "dimension": ("E", "I"), "text": "If you have a question during a live lecture, do you:", "a": "Ask it immediately?", "b": "Email the professor later?"},
    {"id": 14, "section": "E/I", "dimension": ("E", "I"), "text": "Your ideal weekend involves:", "a": "A social gathering.", "b": "A book or a solo hobby."},
    {"id": 15, "section": "E/I", "dimension": ("E", "I"), "text": "People describe you as:", "a": "Approachable and expressive.", "b": "Reserved and private."},
    {"id": 16, "section": "S/N", "dimension": ("S", "N"), "text": "Do you prefer assignments that:", "a": "Have clear, proven instructions?", "b": "Allow for creative interpretation?"},
    {"id": 17, "section": "S/N", "dimension": ("S", "N"), "text": "In business, are you more interested in:", "a": "Current realities and 'what is'?", "b": "Future possibilities and 'what if'?"},
    {"id": 18, "section": "S/N", "dimension": ("S", "N"), "text": "When learning a new tech tool, do you:", "a": "Read the manual/watch a tutorial?", "b": "Explore it by trial and error?"},
    {"id": 19, "section": "S/N", "dimension": ("S", "N"), "text": "Do you consider yourself:", "a": "A practical, down-to-earth person?", "b": "An imaginative, 'big picture' person?"},
    {"id": 20, "section": "S/N", "dimension": ("S", "N"), "text": "In a report, you value:", "a": "Precise data and facts.", "b": "Themes and underlying patterns."},
    {"id": 21, "section": "S/N", "dimension": ("S", "N"), "text": "Do you prefer to master:", "a": "Established skills?", "b": "New, cutting-edge theories?"},
    {"id": 22, "section": "S/N", "dimension": ("S", "N"), "text": "When someone explains a concept, do you want:", "a": "Specific examples?", "b": "The overarching theory?"},
    {"id": 23, "section": "S/N", "dimension": ("S", "N"), "text": "Are you more focused on:", "a": "The present moment?", "b": "Future potential?"},
    {"id": 24, "section": "S/N", "dimension": ("S", "N"), "text": "You trust:", "a": "Experience and history.", "b": "Instinct and hunches."},
    {"id": 25, "section": "S/N", "dimension": ("S", "N"), "text": "In a project, do you enjoy:", "a": "The 'doing' and implementation?", "b": "The 'designing' and conceptualizing?"},
    {"id": 26, "section": "S/N", "dimension": ("S", "N"), "text": "When describing a movie, do you:", "a": "Detail the plot?", "b": "Discuss the 'meaning' of the film?"},
    {"id": 27, "section": "S/N", "dimension": ("S", "N"), "text": "Do you find repetitive tasks:", "a": "Comforting and stable?", "b": "Boring and stifling?"},
    {"id": 28, "section": "S/N", "dimension": ("S", "N"), "text": "At work, do you prefer:", "a": "Improving existing systems?", "b": "Creating entirely new ones?"},
    {"id": 29, "section": "S/N", "dimension": ("S", "N"), "text": "You are more likely to notice:", "a": "What is actually happening.", "b": "What is missing."},
    {"id": 30, "section": "S/N", "dimension": ("S", "N"), "text": "Do you value:", "a": "Common sense?", "b": "Innovation?"},
    {"id": 31, "section": "T/F", "dimension": ("T", "F"), "text": "When giving feedback, are you:", "a": "Direct and honest?", "b": "Tactful and encouraging?"},
    {"id": 32, "section": "T/F", "dimension": ("T", "F"), "text": "In a disagreement, you care more about:", "a": "Being right/logical.", "b": "Maintaining harmony."},
    {"id": 33, "section": "T/F", "dimension": ("T", "F"), "text": "Do you make decisions based on:", "a": "Objective criteria?", "b": "Personal values and impact on people?"},
    {"id": 34, "section": "T/F", "dimension": ("T", "F"), "text": "In leadership, is it more important to be:", "a": "Just and fair?", "b": "Kind and compassionate?"},
    {"id": 35, "section": "T/F", "dimension": ("T", "F"), "text": "When an employee fails, do you look at:", "a": "The technical error?", "b": "The circumstances they were facing?"},
    {"id": 36, "section": "T/F", "dimension": ("T", "F"), "text": "Are you more convinced by:", "a": "A logical argument?", "b": "A touching personal story?"},
    {"id": 37, "section": "T/F", "dimension": ("T", "F"), "text": "Do you prefer a boss who is:", "a": "Competent and challenging?", "b": "Supportive and appreciative?"},
    {"id": 38, "section": "T/F", "dimension": ("T", "F"), "text": "When analyzing a business case, do you focus on:", "a": "Profit and efficiency?", "b": "Employee morale and social impact?"},
    {"id": 39, "section": "T/F", "dimension": ("T", "F"), "text": "Is it worse to be:", "a": "Too emotional?", "b": "Too cold?"},
    {"id": 40, "section": "T/F", "dimension": ("T", "F"), "text": "In a team, do you play the role of:", "a": "The critic who finds flaws?", "b": "The mediator who heals rifts?"},
    {"id": 41, "section": "T/F", "dimension": ("T", "F"), "text": "Do you believe truth is:", "a": "Absolute?", "b": "Subjective?"},
    {"id": 42, "section": "T/F", "dimension": ("T", "F"), "text": "You are motivated by:", "a": "Achievement and recognition.", "b": "Feeling valued and helpful."},
    {"id": 43, "section": "T/F", "dimension": ("T", "F"), "text": "Do you find it easy to:", "a": "Fire someone if necessary?", "b": "Empathize even with difficult people?"},
    {"id": 44, "section": "T/F", "dimension": ("T", "F"), "text": "Do you analyze problems with:", "a": "Your head?", "b": "Your heart?"},
    {"id": 45, "section": "T/F", "dimension": ("T", "F"), "text": "In a debate, you prioritize:", "a": "Clarity.", "b": "Diplomacy."},
    {"id": 46, "section": "J/P", "dimension": ("J", "P"), "text": "Do you prefer a schedule that is:", "a": "Structured and planned?", "b": "Flexible and spontaneous?"},
    {"id": 47, "section": "J/P", "dimension": ("J", "P"), "text": "When starting an assignment, do you:", "a": "Start early to avoid stress?", "b": "Wait for the 'pressure' of the deadline?"},
    {"id": 48, "section": "J/P", "dimension": ("J", "P"), "text": "Is your desk/workspace usually:", "a": "Organized and tidy?", "b": "A 'messy' but functional space?"},
    {"id": 49, "section": "J/P", "dimension": ("J", "P"), "text": "Do you like to:", "a": "Make lists and check things off?", "b": "Keep your options open?"},
    {"id": 50, "section": "J/P", "dimension": ("J", "P"), "text": "In a group project, does it bother you more:", "a": "If things are disorganized?", "b": "If things are too rigid?"},
    {"id": 51, "section": "J/P", "dimension": ("J", "P"), "text": "Before a trip, do you:", "a": "Plan every detail?", "b": "Just show up and see what happens?"},
    {"id": 52, "section": "J/P", "dimension": ("J", "P"), "text": "Do you feel better when a decision is:", "a": "Settled and finalized?", "b": "Open for change?"},
    {"id": 53, "section": "J/P", "dimension": ("J", "P"), "text": "At work, do you:", "a": "Focus on finishing one task at a time?", "b": "Multitask on various projects?"},
    {"id": 54, "section": "J/P", "dimension": ("J", "P"), "text": "Do you view rules as:", "a": "Essential for order?", "b": "Helpful suggestions that can be bypassed?"},
    {"id": 55, "section": "J/P", "dimension": ("J", "P"), "text": "When attending an online lecture, do you:", "a": "Arrive 5 minutes early?", "b": "Join exactly on time or slightly late?"},
    {"id": 56, "section": "J/P", "dimension": ("J", "P"), "text": "Do you prefer to:", "a": "Know what you're doing next week?", "b": "See how you feel when the time comes?"},
    {"id": 57, "section": "J/P", "dimension": ("J", "P"), "text": "'Work first, play later' is:", "a": "Your motto.", "b": "A difficult rule to follow."},
    {"id": 58, "section": "J/P", "dimension": ("J", "P"), "text": "In a meeting, do you want:", "a": "An agenda followed strictly?", "b": "A free-flowing discussion?"},
    {"id": 59, "section": "J/P", "dimension": ("J", "P"), "text": "Are you more productive:", "a": "In a routine?", "b": "In a crisis?"},
    {"id": 60, "section": "J/P", "dimension": ("J", "P"), "text": "Do you find surprises:", "a": "Stressful?", "b": "Exciting?"},
]

TYPE_DESCRIPTIONS = {
    "INTJ": "Strategic and independent. You tend to think ahead, value competence, and enjoy building long-term systems and plans.",
    "INTP": "Analytical and curious. You enjoy understanding how things work and often explore ideas deeply before acting.",
    "ENTJ": "Decisive and goal-oriented. You are energized by leadership, structure, and driving outcomes.",
    "ENTP": "Innovative and quick-thinking. You enjoy ideas, possibilities, experimentation, and debate.",
    "INFJ": "Insightful and values-driven. You often balance vision with empathy and meaningful purpose.",
    "INFP": "Reflective and idealistic. You value authenticity, personal meaning, and thoughtful growth.",
    "ENFJ": "Supportive and influential. You tend to motivate others, organize people, and build positive collaboration.",
    "ENFP": "Energetic and imaginative. You bring enthusiasm, creativity, and people focus into new opportunities.",
    "ISTJ": "Reliable and detail-focused. You value consistency, order, and doing work correctly.",
    "ISFJ": "Practical and caring. You are dependable, attentive, and often help teams run smoothly.",
    "ESTJ": "Organized and action-driven. You value clear expectations, efficiency, and measurable results.",
    "ESFJ": "Cooperative and responsible. You are attentive to people, structure, and shared commitments.",
    "ISTP": "Calm and hands-on. You often solve problems through observation, logic, and practical action.",
    "ISFP": "Quiet and adaptable. You tend to work in a grounded way while staying true to personal values.",
    "ESTP": "Bold and responsive. You move quickly, adapt in real time, and like action-oriented environments.",
    "ESFP": "Expressive and engaging. You often bring energy, spontaneity, and warmth into group settings.",
}


def get_db() -> sqlite3.Connection:
    if "db" not in g:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        g.db = conn
    return g.db


@app.teardown_appcontext
def close_db(_: object | None) -> None:
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db() -> None:
    db = sqlite3.connect(DB_PATH)
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS submissions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            email TEXT NOT NULL,
            student_id TEXT,
            course TEXT,
            department TEXT,
            year_semester TEXT,
            section_name TEXT,
            phone TEXT,
            score_e INTEGER NOT NULL,
            score_i INTEGER NOT NULL,
            score_s INTEGER NOT NULL,
            score_n INTEGER NOT NULL,
            score_t INTEGER NOT NULL,
            score_f INTEGER NOT NULL,
            score_j INTEGER NOT NULL,
            score_p INTEGER NOT NULL,
            personality_type TEXT NOT NULL,
            answers_json TEXT NOT NULL,
            submitted_at TEXT NOT NULL
        )
        """
    )
    db.commit()
    db.close()


def admin_required(view_func):
    @wraps(view_func)
    def wrapped(*args, **kwargs):
        if not session.get("admin_logged_in"):
            return redirect(url_for("admin_login"))
        return view_func(*args, **kwargs)

    return wrapped


def calculate_result(form_data: dict[str, str]) -> tuple[dict[str, int], str]:
    scores = {"E": 0, "I": 0, "S": 0, "N": 0, "T": 0, "F": 0, "J": 0, "P": 0}
    for q in QUESTIONS:
        selected = form_data.get(f"q{q['id']}")
        if selected == "A":
            scores[q["dimension"][0]] += 1
        elif selected == "B":
            scores[q["dimension"][1]] += 1
    personality = (
        ("E" if scores["E"] >= scores["I"] else "I")
        + ("S" if scores["S"] >= scores["N"] else "N")
        + ("T" if scores["T"] >= scores["F"] else "F")
        + ("J" if scores["J"] >= scores["P"] else "P")
    )
    return scores, personality


@app.route("/")
def index():
    return render_template("index.html", questions=QUESTIONS)


@app.route("/submit", methods=["POST"])
def submit():
    required_fields = ["full_name", "email"]
    for field in required_fields:
        if not request.form.get(field, "").strip():
            flash("Please fill all required student details.", "error")
            return redirect(url_for("index"))

    missing_answers = [str(q["id"]) for q in QUESTIONS if not request.form.get(f"q{q['id']}")]
    if missing_answers:
        flash(f"Please answer all 60 questions. Missing: {', '.join(missing_answers[:8])}{'...' if len(missing_answers) > 8 else ''}", "error")
        return redirect(url_for("index"))

    scores, personality = calculate_result(request.form)
    answers = {f"q{q['id']}": request.form.get(f"q{q['id']}") for q in QUESTIONS}

    db = get_db()
    db.execute(
        """
        INSERT INTO submissions (
            full_name, email, student_id, course, department, year_semester, section_name, phone,
            score_e, score_i, score_s, score_n, score_t, score_f, score_j, score_p,
            personality_type, answers_json, submitted_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            request.form.get("full_name", "").strip(),
            request.form.get("email", "").strip(),
            request.form.get("student_id", "").strip(),
            request.form.get("course", "").strip(),
            request.form.get("department", "").strip(),
            request.form.get("year_semester", "").strip(),
            request.form.get("section_name", "").strip(),
            request.form.get("phone", "").strip(),
            scores["E"], scores["I"], scores["S"], scores["N"],
            scores["T"], scores["F"], scores["J"], scores["P"],
            personality,
            str(answers),
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        ),
    )
    db.commit()

    return render_template(
        "result.html",
        personality=personality,
        description=TYPE_DESCRIPTIONS.get(personality, "Your result has been calculated successfully."),
        scores=scores,
        student_name=request.form.get("full_name", "").strip(),
    )


@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")
        if username == app.config["ADMIN_USERNAME"] and check_password_hash(app.config["ADMIN_PASSWORD_HASH"], password):
            session["admin_logged_in"] = True
            return redirect(url_for("admin_dashboard"))
        flash("Invalid admin credentials.", "error")
    return render_template("admin_login.html")


@app.route("/admin/logout")
def admin_logout():
    session.clear()
    return redirect(url_for("admin_login"))


@app.route("/admin/dashboard")
@admin_required
def admin_dashboard():
    db = get_db()
    rows = db.execute(
        "SELECT * FROM submissions ORDER BY id DESC"
    ).fetchall()
    stats = db.execute(
        "SELECT personality_type, COUNT(*) AS total FROM submissions GROUP BY personality_type ORDER BY total DESC, personality_type ASC"
    ).fetchall()
    return render_template("admin_dashboard.html", rows=rows, stats=stats)


@app.route("/admin/export")
@admin_required
def admin_export():
    db = get_db()
    rows = db.execute("SELECT * FROM submissions ORDER BY id DESC").fetchall()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "ID", "Full Name", "Email", "Student ID", "Course", "Department", "Year/Semester",
        "Section", "Phone", "E", "I", "S", "N", "T", "F", "J", "P", "Personality Type", "Submitted At"
    ])
    for row in rows:
        writer.writerow([
            row["id"], row["full_name"], row["email"], row["student_id"], row["course"], row["department"],
            row["year_semester"], row["section_name"], row["phone"], row["score_e"], row["score_i"], row["score_s"],
            row["score_n"], row["score_t"], row["score_f"], row["score_j"], row["score_p"], row["personality_type"], row["submitted_at"]
        ])

    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=personality_test_submissions.csv"},
    )


if __name__ == "__main__":
    init_db()
    app.run(debug=True, host="0.0.0.0", port=5000)
