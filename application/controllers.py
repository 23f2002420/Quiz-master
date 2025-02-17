from flask import Flask, render_template, redirect, request, url_for, session, flash
from flask import current_app as app
from .models import *
from .database import db
from datetime import datetime, date, timedelta
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import os
import io
import base64
from sqlalchemy import func
import pytz

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        u_name = request.form.get("u_name")
        pwd = request.form.get("pwd")
        this_user = User.query.filter_by(username=u_name).first()
        if this_user:
            if this_user.password == pwd:
                session["user_id"] = this_user.id
                if this_user.is_admin == "admin":
                    return redirect(url_for("admin_dashboard"))
                else:
                    return redirect(url_for("user_dashboard", user_id=this_user.id))
            else:
                return "incorrect password"
        else:
            return "user does not exist!" 
    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("u_name")
        password = request.form.get("password")
        full_name = request.form.get("full_name")
        qualification = request.form.get("qualification")
        dob_string = request.form.get("dob")
        dob = datetime.strptime(dob_string, "%Y-%m-%d").date()
        this_user = User.query.filter_by(username=username).first()
        if this_user:
            return "user already exist!"
        else:
            new_user = User(
                username=username,
                password=password,
                full_name=full_name,
                qualification=qualification,
                dob=dob,
                is_admin="general",
            )
            db.session.add(new_user)
            db.session.commit()
            return redirect("login")
    return render_template("register.html")


# Subject Controllers
@app.route("/new_subject", methods=["GET", "POST"])
def new_subject():
    if ("user_id" not in session or User.query.get(session["user_id"]).is_admin != "admin"):
        return redirect(url_for("login"))
    if request.method == "POST":
        name = request.form.get("name")
        description = request.form.get("description")
        new_subject = Subject(name=name, description=description)
        db.session.add(new_subject)
        db.session.commit()
        return redirect(url_for("admin_dashboard"))
    return render_template("new_sub.html")


@app.route("/edit_subject/<int:subject_id>", methods=["GET", "POST"])
def edit_subject(subject_id):
    if ("user_id" not in session or User.query.get(session["user_id"]).is_admin != "admin"):
        return redirect(url_for("login"))
    subject = Subject.query.get_or_404(subject_id)
    if request.method == "POST":
        subject.name = request.form.get("name")
        subject.description = request.form.get("description")
        db.session.commit()
        flash("Subject updated successfully", "success")
        return redirect(url_for("admin_dashboard"))

    return render_template("edit_subject.html", subject=subject)


@app.route("/delete_subject/<int:subject_id>", methods=["POST"]) 
def delete_subject(subject_id):
    if ("user_id" not in session or User.query.get(session["user_id"]).is_admin != "admin"):
        return redirect(url_for("login"))
    subject = Subject.query.get_or_404(subject_id)
    db.session.delete(subject)
    db.session.commit()
    flash("Subject deleted successfully", "success")
    return redirect(url_for("admin_dashboard"))


@app.route("/new_chapter/<int:subject_id>", methods=["GET", "POST"])
def new_chapter(subject_id):
    if ("user_id" not in session or User.query.get(session["user_id"]).is_admin != "admin"):
        return redirect(url_for("login"))
    subject = Subject.query.get_or_404(subject_id)
    if request.method == "POST":
        name = request.form.get("name")
        description = request.form.get("description")
        new_chapter = Chapter(name=name, description=description, subject_id=subject.id)
        db.session.add(new_chapter)
        db.session.commit()
        return redirect(url_for("admin_dashboard"))
    return render_template("new_chapter.html", subject=subject)


@app.route("/edit_chapter/<int:chapter_id>", methods=["GET", "POST"])
def edit_chapter(chapter_id):
    if ("user_id" not in session or User.query.get(session["user_id"]).is_admin != "admin"):
        return redirect(url_for("login"))
    chapter = Chapter.query.get_or_404(chapter_id)
    if request.method == "POST":
        chapter.name = request.form.get("name")
        chapter.description = request.form.get("description")
        db.session.commit()
        flash("Chapter updated successfully", "success")
        return redirect(url_for("admin_dashboard"))
    return render_template("edit_chapter.html", chapter=chapter)


@app.route("/delete_chapter/<int:chapter_id>", methods=['GET','POST'])
def delete_chapter(chapter_id):
    if ("user_id" not in session or User.query.get(session["user_id"]).is_admin != "admin"):
        return redirect(url_for("login"))
    chapter = Chapter.query.get_or_404(chapter_id)
    quizzes_to_delete = Quiz.query.filter_by(chapter_id=chapter.id).all()
    for quiz in quizzes_to_delete:
        questions_to_delete = Question.query.filter_by(quiz_id=quiz.id).all()
        for question in questions_to_delete:
            db.session.delete(question)
        db.session.delete(quiz)
    db.session.delete(chapter)
    db.session.commit()
    flash("Chapter deleted successfully", "success")
    return redirect(url_for("admin_dashboard"))


@app.route("/quiz_management", methods=["GET", "POST"])
def quiz_management():
    if ("user_id" not in session or User.query.get(session["user_id"]).is_admin != "admin"):
        return redirect(url_for("login"))
    search_query = request.args.get("search_query")
    quizzes = (
        Quiz.query.filter(Quiz.title.ilike(f"%{search_query}%"))
        if search_query
        else Quiz.query.all()
    )
    for quiz in quizzes:
        quiz.questions = Question.query.filter_by(quiz_id=quiz.id).all()
    return render_template("quiz_management.html", quizzes=quizzes, search_query=search_query)


## Adding new_quiz
@app.route("/new_quiz", methods=["GET", "POST"])
def new_quiz():
    if ("user_id" not in session or User.query.get(session["user_id"]).is_admin != "admin"):
        return redirect(url_for("login"))
    chapters = Chapter.query.all()
    if request.method == "POST":
        title = request.form.get("title")
        chapter_id = request.form.get("chapter_id")
        date_of_quiz = request.form.get("date_of_quiz")
        duration = request.form.get("duration")
        is_active = "is_active" in request.form
        try:
            chapter_id = int(chapter_id) if chapter_id else None
            if chapter_id is None or Chapter.query.get(chapter_id) is None:
                flash("Invalid chapter_id", "error")
                return render_template("new_quiz.html", chapters=chapters)
            new_quiz = Quiz(
                title=title,
                chapter_id=chapter_id,
                date_of_quiz=datetime.strptime(date_of_quiz, "%Y-%m-%d").date(),
                time_duration=datetime.strptime(duration, "%H:%M").time(),
                is_active=is_active,
            )
            db.session.add(new_quiz)
            db.session.commit()
            return redirect(url_for("quiz_management"))
        except ValueError:
            flash("Invalid date or time format", "error")
            return render_template("new_quiz.html", chapters=chapters)
    return render_template("new_quiz.html", chapters=chapters)


# --Edit Quiz---
@app.route("/edit_quiz/<int:quiz_id>", methods=["GET", "POST"])
def edit_quiz(quiz_id):
    if ("user_id" not in session or User.query.get(session["user_id"]).is_admin != "admin"):
        return redirect(url_for("login"))
    quiz = Quiz.query.get_or_404(quiz_id)
    chapters = Chapter.query.all()
    if request.method == "POST":
        quiz.title = request.form.get("title")
        quiz.chapter_id = request.form.get("chapter_id")
        date_of_quiz = request.form.get("date_of_quiz")
        duration = request.form.get("duration")
        quiz.is_active = "is_active" in request.form
        try:
            quiz.date_of_quiz = datetime.strptime(date_of_quiz, "%Y-%m-%d").date()
            quiz.duration = datetime.strptime(duration, "%H:%M").time()
            db.session.commit()
            flash("Quiz updated successfully", "success")
            return redirect(url_for("quiz_management"))
        except ValueError:
            flash("Invalid date or time format", "danger")
            return render_template("edit_quiz.html", quiz=quiz, chapters=chapters)
    return render_template("edit_quiz.html", quiz=quiz, chapters=chapters)


# ----Delete quiz----
@app.route("/delete_quiz/<int:quiz_id>", methods=["POST"])
def delete_quiz(quiz_id):
    if ("user_id" not in session or User.query.get(session["user_id"]).is_admin != "admin"):
        return redirect(url_for("login"))
    quiz = Quiz.query.get_or_404(quiz_id)
    db.session.delete(quiz)
    db.session.commit()
    flash("Quiz deleted successfully", "success")
    return redirect(url_for("quiz_management"))


# Questions Controllers
@app.route("/new_question/<int:quiz_id>", methods=["GET", "POST"])
def new_question(quiz_id):
    if ("user_id" not in session or User.query.get(session["user_id"]).is_admin != "admin"):
        return redirect(url_for("login"))
    quiz = Quiz.query.get_or_404(quiz_id)
    if request.method == "POST":
        question_title = request.form.get("question_title")
        option1 = request.form.get("option1")
        option2 = request.form.get("option2")
        option3 = request.form.get("option3")
        option4 = request.form.get("option4")
        correct_option = request.form.get("correct_option")
        new_question = Question(
            question_title=question_title,
            option1=option1,
            option2=option2,
            option3=option3,
            option4=option4,
            correct_option=int(correct_option),
            quiz_id=quiz.id,
        )
        db.session.add(new_question)
        db.session.commit()
        return redirect(url_for("quiz_management"))
    return render_template("new_question.html", quiz=quiz)


@app.route("/edit_question/<int:question_id>", methods=["GET", "POST"])
def edit_question(question_id):
    if ("user_id" not in session or User.query.get(session["user_id"]).is_admin != "admin"):
        return redirect(url_for("login"))
    question = Question.query.get_or_404(question_id)
    if request.method == "POST":
        question.question_title = request.form.get("question_title")
        question.option1 = request.form.get("option1")
        question.option2 = request.form.get("option2")
        question.option3 = request.form.get("option3")
        question.option4 = request.form.get("option4")
        question.correct_option = int(request.form.get("correct_option"))
        db.session.commit()
        flash("Question updated successfully", "success")
        return redirect(url_for("quiz_management"))
    return render_template("edit_question.html", question=question)


@app.route("/delete_question/<int:question_id>", methods=['GET',"POST"])
def delete_question(question_id):
    if ("user_id" not in session or User.query.get(session["user_id"]).is_admin != "admin"):
        return redirect(url_for("login"))
    question = Question.query.get_or_404(question_id)
    db.session.delete(question)
    db.session.commit()
    flash("Question deleted successfully", "success")
    return redirect(url_for("quiz_management"))


# ---Dashboard Controllers ----
@app.route("/admin_dashboard", methods=["GET", "POST"])
def admin_dashboard():
    if ("user_id" not in session or User.query.get(session["user_id"]).is_admin != "admin"):
        return redirect(url_for("login"))
    search_query = request.args.get("search_query")
    subjects = (
        Subject.query.filter(Subject.name.ilike(f"%{search_query}%")).all()
        if search_query
        else Subject.query.all()
    )

    quizzes = []
    for subject in subjects:
        chapters = subject.chapters
        for chapter in chapters:
            total_questions = sum(len(quiz.questions) for quiz in chapter.quizzes)
            chapter.question_count = total_questions
            quizzes.extend(
                [
                    quiz
                    for quiz in chapter.quizzes
                    if not search_query or search_query.lower() in quiz.title.lower()
                ]
            )
    return render_template(
        "admin_dash.html", subjects=subjects, quizzes=quizzes, search_query=search_query
    )


# ----User Part------
@app.route("/user_dashboard/<int:user_id>", methods=["GET", "POST"])
def user_dashboard(user_id):
    if "user_id" not in session or session["user_id"] != user_id:
        return redirect(url_for("login"))
    this_user = User.query.get_or_404(user_id)
    search_query = request.args.get("search_query")
    date_filter = request.args.get("date_filter")
    user_scores_query = Score.query.filter_by(user_id=user_id)
    if search_query:
        user_scores_query = user_scores_query.join(Quiz).filter(
            Quiz.title.ilike(f"%{search_query}%")
        )
    if date_filter:
        try:
            filter_date = datetime.strptime(date_filter, "%Y-%m-%d").date()
            user_scores_query = user_scores_query.filter(
                func.date(Score.time_stamp_of_attempt) == filter_date
            )
        except ValueError:
            flash("Invalid date format. Please use YYYY-MM-DD.", "error")
    user_scores = user_scores_query.all()
    today = date.today()
    upcoming_quizzes = Quiz.query.filter(Quiz.date_of_quiz >= today)
    if search_query:
        upcoming_quizzes = upcoming_quizzes.filter(
            Quiz.title.ilike(f"%{search_query}%")
        )
    upcoming_quizzes = upcoming_quizzes.all()
    return render_template(
        "user_dash.html",
        user=this_user,
        upcoming_quizzes=upcoming_quizzes,
        user_scores=user_scores,
        search_query=search_query,
        date_filter=date_filter,
    )


def calculate_time_left(duration, start_time_str):
    try:
        start_time_utc = datetime.fromisoformat(start_time_str).replace(tzinfo=pytz.utc)
        now_utc = datetime.now(pytz.utc)
        quiz_end_time_utc = start_time_utc + timedelta(
            hours=duration.hour, minutes=duration.minute, seconds=duration.second
        )
        time_left_delta = quiz_end_time_utc - now_utc
        if time_left_delta.total_seconds() <= 0:
            return "00:00:00"
        hours, remainder = divmod(time_left_delta.total_seconds(), 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}"
    except Exception as e:
        print(f"Error calculating time left: {e}")
        return "00:00:00"


@app.route("/start_quiz/<int:quiz_id>", methods=["GET", "POST"])
def start_quiz(quiz_id):
    user_id = session.get("user_id")
    if not user_id:
        return redirect(url_for("login"))
    quiz = Quiz.query.get_or_404(quiz_id)
    questions = quiz.questions
    total_questions = len(questions)
    if "quiz_data" not in session or session["quiz_data"].get("quiz_id") != quiz_id:
        session["quiz_data"] = {
            "quiz_id": quiz_id,
            "question_index": 0,
            "answers": {},
            "start_time": datetime.utcnow().isoformat(),
        }
        print(f"Quiz data initialized in session: {session['quiz_data']}")
    quiz_data = session["quiz_data"] 
    current_question_index = quiz_data["question_index"]
    if current_question_index >= total_questions:
        score = calculate_score(quiz_id, quiz_data["answers"])
        save_score(quiz_id, user_id, score)
        session.pop("quiz_data", None)  
        print("Quiz completed, redirecting to view_scores")
        return redirect(url_for("view_scores", user_id=user_id))
    question = questions[current_question_index]
    selected_answer = quiz_data["answers"].get(str(question.id))
    start_time_str = quiz_data["start_time"]
    time_left = calculate_time_left(quiz.time_duration, start_time_str)
    if request.method == "POST":
        answer = request.form.get("answer")
        if answer:
            quiz_data["answers"][str(question.id)] = answer
            session["quiz_data"] = quiz_data
            session.modified = True
            print(f"Answer submitted: {answer}, Quiz data: {session['quiz_data']}")
        else:
            flash("Please select an answer.", "error")
        if request.form.get("action") == "next":
            quiz_data["question_index"] += 1
            session["quiz_data"] = quiz_data
            session.modified = True
            print("Moving to next question")
            return redirect(url_for("start_quiz", quiz_id=quiz_id))
        elif request.form.get("action") == "submit":
            score = calculate_score(quiz_id, quiz_data["answers"])
            save_score(quiz_id, user_id, score)
            session.pop("quiz_data", None)
            print("Quiz submitted, redirecting to view_scores")
            return redirect(url_for("view_scores", user_id=user_id))
        elif request.form.get("action") == "Previous":
            if quiz_data["question_index"] >0:
                quiz_data["question_index"] -=1
                session['quiz_data'] = quiz_data
                session.modified = True
                print("Moving to previous question")
            else:
                flash("You are already at the first question.")
                return redirect(url_for("start_quiz", quiz_id =quiz_id))
    return render_template(
        "start_quiz.html",
        quiz=quiz,
        question=question,
        current_question_index=current_question_index + 1,
        total_questions=total_questions,
        time_left=time_left,
        selected_answer=selected_answer,
    )

def calculate_score(quiz_id, answers):
    quiz = Quiz.query.get_or_404(quiz_id)
    questions = quiz.questions
    score = 0
    print(f"Answer in calculate_Score: {answers}")
    for question in questions:
        question_id_str = str(question.id)
        print(f"Correct option for question {question.id}:{question.correct_option}")
        if question_id_str in answers and answers[question_id_str] is not None:
            try:
                user_answer = int(answers[question_id_str])
                if user_answer == question.correct_option:
                    score += 1
            except ValueError:
                print(f"Invalid answer format for question {question.id}")
            except AttributeError:
                print(
                    f"Question object{question.id} does not have 'correct_option attribute"
                )
    return score


def save_score(quiz_id, user_id, score):
    new_score = Score(quiz_id=quiz_id, user_id=user_id, total_scored=score)
    db.session.add(new_score)
    db.session.commit()
    return new_score


@app.route("/view_quiz/<int:quiz_id>")
def view_quiz(quiz_id):
    if "user_id" not in session:
        return redirect(url_for("login"))
    quiz = Quiz.query.get_or_404(quiz_id)
    return render_template("view_quiz.html", quiz=quiz, user_id=session["user_id"])


# Scores Controllers
@app.route("/view_scores/<int:user_id>")
def view_scores(user_id):
    user = User.query.get_or_404(user_id)
    scores = Score.query.filter_by(user_id=user.id).all()
    return render_template(
        "view_scores.html", scores=scores, user_id=user_id, user=user
    )


@app.route("/logout")
def logout():
    return render_template("login.html")


@app.route("/admin_summary")
def admin_summary():
    if ("user_id" not in session or User.query.get(session["user_id"]).is_admin != "admin"):
        return redirect(url_for("login"))
    chart_image = create_admin_charts()
    return render_template("admin_summary.html", chart_image=chart_image)


def create_admin_charts():
    subjects = Subject.query.all()
    subject_scores = []
    subject_labels = []
    for subject in subjects:
        average_score = (
            db.session.query(func.avg(Score.total_scored))
            .join(Quiz)
            .join(Chapter)
            .filter(Chapter.subject_id == subject.id)
            .scalar()
        )
        subject_labels.append(subject.name)
        subject_scores.append(average_score or 0)
    subject_attempts = []
    for subject in subjects:
        attempt_count = (
            db.session.query(func.count(Score.id))
            .join(Quiz)
            .join(Chapter)
            .filter(Chapter.subject_id == subject.id)
            .scalar()
        )
        subject_attempts.append(attempt_count or 0)
    fig, axs = plt.subplots(1, 2, figsize=(12, 6))
    axs[0].bar(subject_labels, subject_scores)
    axs[0].set_title("Subject Wise Top Scores")
    axs[0].set_xlabel("Subjects")
    axs[0].set_ylabel("Average Score")
    axs[0].tick_params(axis="x", rotation=45)

    axs[1].pie(
        subject_attempts, labels=subject_labels, autopct="%1.1f%%", startangle=90
    )
    axs[1].set_title("Subject Wise User Attempts")

    img = io.BytesIO()
    plt.savefig(img, format="png")
    img.seek(0)
    plt.close(fig)
    img_str = base64.b64encode(img.read()).decode("utf-8")
    return img_str


@app.route("/user_summary")
def user_summary():
    if "user_id" not in session:
        return redirect(url_for("login"))
    user_id = session["user_id"]
    chart_image = create_user_charts(user_id)
    user = User.query.get_or_404(user_id)
    return render_template("user_summary.html", chart_image=chart_image, user=user)


def create_user_charts(user_id):
    subjects = Subject.query.all()
    subject_labels = []
    subject_counts = []
    for subject in subjects:
        quiz_count = (
            db.session.query(func.count(Score.quiz_id))
            .join(Quiz)
            .join(Chapter)
            .filter(Score.user_id == user_id, Chapter.subject_id == subject.id)
            .scalar()
        )
        subject_labels.append(subject.name)
        subject_counts.append(quiz_count or 0)
    month_labels = [
        "01",
        "02",
        "03",
        "04",
        "05",
        "06",
        "07",
        "08",
        "09",
        "10",
        "11",
        "12",
    ]
    month_counts = [0] * 12
    scores = Score.query.filter_by(user_id=user_id).all()
    for score in scores:
        month = score.time_stamp_of_attempt.strftime("%m")
        month_index = int(month) - 1
        if 0 <= month_index < 12:
            month_counts[month_index] += 1
    fig, axs = plt.subplots(1, 2, figsize=(12, 6))

    axs[0].bar(subject_labels, subject_counts)
    axs[0].set_title("Subject-wise Number of Quizzes Attempted")
    axs[0].set_xlabel("Subjects")
    axs[0].set_ylabel("Number of Quizzes")
    axs[0].tick_params(axis="x", rotation=45)

    axs[1].pie(month_counts, labels=month_labels, autopct="%1.1f%%", startangle=90)
    axs[1].set_title("Month-wise Most Quizzes Attempted")

    img = io.BytesIO()
    plt.savefig(img, format="png")
    img.seek(0)
    plt.close(fig)
    img_str = base64.b64encode(img.read()).decode("utf-8")
    return img_str
