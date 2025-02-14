from flask import Flask, render_template, redirect, request, url_for, session, flash
from flask import current_app as app
from .models import *
from datetime import datetime, date
import matplotlib as plt
import os


# ----Login Part---
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


# ----Register Part----
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
    if "user_id" not in session:
        return redirect(url_for("login"))
    this_user = User.query.get_or_404(session["user_id"])
    if this_user.is_admin != "admin":
        return redirect(url_for("login"))
    if request.method == "POST":
        name = request.form.get("name")
        description = request.form.get("description")
        new_subject = Subject(name=name, description=description)
        db.session.add(new_subject)
        db.session.commit()
        return redirect(url_for("admin_dashboard"))
    return render_template("new_sub.html")

@app.route('/edit_subject/<int:subject_id>', methods=['GET', 'POST'])
def edit_subject(subject_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    this_user = User.query.get_or_404(session['user_id'])
    if this_user.is_admin != "admin":
        return redirect(url_for('login'))
    subject = Subject.query.get_or_404(subject_id)

    if request.method == 'POST':
        subject.name = request.form.get('name')
        subject.description = request.form.get('description')
        db.session.commit()
        flash('Subject updated successfully', 'success')
        return redirect(url_for('admin_dashboard'))

    return render_template('edit_subject.html', subject=subject)

@app.route('/delete_subject/<int:subject_id>', methods=['GET','POST'])
def delete_subject(subject_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    this_user = User.query.get_or_404(session['user_id'])
    if this_user.is_admin != "admin":
        return redirect(url_for('login'))
    subject = Subject.query.get_or_404(subject_id)
    db.session.delete(subject)
    db.session.commit()
    flash('Subject deleted successfully', 'success')
    return redirect(url_for('admin_dashboard'))


# Chapter COntrollers
@app.route("/new_chapter/<int:subject_id>", methods=["GET", "POST"])
def new_chapter(subject_id):
    if "user_id" not in session:
        return redirect(url_for("login"))
    this_user = User.query.get_or_404(session["user_id"])
    if this_user.is_admin != "admin":
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


@app.route('/edit_chapter/<int:chapter_id>', methods=['GET', 'POST'])
def edit_chapter(chapter_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    this_user = User.query.get_or_404(session['user_id'])
    if this_user.is_admin != "admin":
        return redirect(url_for('login'))
    chapter = Chapter.query.get_or_404(chapter_id)

    if request.method == 'POST':
        chapter.name = request.form.get('name')
        chapter.description = request.form.get('description')
        db.session.commit()
        flash('Chapter updated successfully', 'success')
        return redirect(url_for('admin_dashboard'))

    return render_template('edit_chapter.html', chapter=chapter)

@app.route('/delete_chapter/<int:chapter_id>', methods=['GET','POST'])
def delete_chapter(chapter_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    this_user = User.query.get_or_404(session['user_id'])
    if this_user.is_admin != "admin":
        return redirect(url_for('login'))
    chapter = Chapter.query.get_or_404(chapter_id)
    quizzes_to_delete = Quiz.query.filter_by(chapter_id = chapter.id).all()
    for quiz in quizzes_to_delete:
        questions_to_delete = Question.query.filter_by(quiz_id = quiz.id).all()
        for question in questions_to_delete:
            db.session.delete(question)
        db.session.delete(quiz)    
    db.session.delete(chapter)
    db.session.commit()
    flash('Chapter deleted successfully', 'success')
    return redirect(url_for('admin_dashboard'))


@app.route("/quiz_management", methods=["GET", "POST"])
def quiz_management():
    if "user_id" not in session:
        return redirect(url_for("login"))
    this_user = User.query.get_or_404(session["user_id"])
    if this_user.is_admin != "admin":
        return redirect(url_for("login"))
    search_query = request.args.get('search_query')
    if search_query:
        quizzes = Quiz.query.filter(Quiz.title.ilike(f"%{search_query}%")).all()
    else:
        quizzes = Quiz.query.all()
    for quiz in quizzes:
        quiz.questions = Question.query.filter_by(quiz_id=quiz.id).all()
    return render_template("quiz_management.html", quizzes=quizzes, search_query=search_query)




## Adding new_quiz
@app.route("/new_quiz", methods=["GET", "POST"])
def new_quiz():
    if "user_id" not in session:
        return redirect(url_for("login"))
    this_user = User.query.get_or_404(session["user_id"])
    if this_user.is_admin != "admin":
        return redirect(url_for("login"))
    chapters = Chapter.query.all()  # Fetch all chapters to populate the dropdown
    if request.method == "POST":
        title = request.form.get("title")
        chapter_id = request.form.get("chapter_id")
        chapter_id = int(chapter_id) if chapter_id else None
        if chapter_id is None or Chapter.query.get(chapter_id) is None:
            return "Invalid chapter_id"
        date_of_quiz = request.form.get("date_of_quiz")
        duration = request.form.get("duration")
        is_active = "is_active" in request.form

        try:
            new_quiz = Quiz(
                title=title,
                chapter_id=chapter_id,
                date_of_quiz=datetime.strptime(date_of_quiz, "%Y-%m-%d").date(),
                duration=datetime.strptime(duration, "%H:%M").time(),
                is_active=is_active,
            )
            db.session.add(new_quiz)
            db.session.commit()
            return redirect(url_for("quiz_management"))
        except ValueError:
            return "Invalid date or time format"

    return render_template("new_quiz.html", chapters=chapters)

# --Edit Quiz---
@app.route("/edit_quiz/<int:quiz_id>", methods=["GET", "POST"])
def edit_quiz(quiz_id):
    if "user_id" not in session:
        return redirect(url_for("login"))
    this_user = User.query.get_or_404(session["user_id"])
    if this_user.is_admin != "admin":
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
@app.route("/delete_quiz/<int:quiz_id>", methods=["GET", "POST"])
def delete_quiz(quiz_id):
    if "user_id" not in session:
        return redirect(url_for("login"))
    this_user = User.query.get_or_404(session["user_id"])
    if this_user.is_admin != "admin":
        return redirect(url_for("login"))
    quiz = Quiz.query.get_or_404(quiz_id)
    db.session.delete(quiz)
    db.session.commit()
    flash("Quiz deleted successfully", "success")
    return redirect(url_for("quiz_management"))


# Questions Controllers
@app.route("/new_question/<int:quiz_id>", methods=["GET", "POST"])
def new_question(quiz_id):
    if "user_id" not in session:
        return redirect(url_for("login"))
    this_user = User.query.get_or_404(session["user_id"])
    if this_user.is_admin != "admin":
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
        return redirect(
            url_for(
                "quiz_management",
            )
        )
    return render_template("new_question.html", quiz=quiz)


@app.route("/edit_question/<int:question_id>", methods=["GET", "POST"])
def edit_question(question_id):
    if "user_id" not in session:
        return redirect(url_for("login"))
    this_user = User.query.get_or_404(session["user_id"])
    if this_user.is_admin != "admin":
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

@app.route('/delete_question/<int:question_id>', methods=['GET','POST'])
def delete_question(question_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    this_user = User.query.get_or_404(session['user_id'])
    if this_user.is_admin != "admin":
        return redirect(url_for('login'))
    question = Question.query.get_or_404(question_id)
    db.session.delete(question)
    db.session.commit()
    flash('Question deleted successfully', 'success')
    return redirect(url_for('quiz_management'))


# ---Dashboard Controllers ----


@app.route("/admin_dashboard", methods=["GET", "POST"])
def admin_dashboard():
    if "user_id" not in session:
        return redirect(url_for("login"))
    this_user = User.query.get_or_404(session["user_id"])
    if this_user.is_admin != "admin":
        return redirect(url_for("login"))
    search_query = request.args.get('search_query') 
    if search_query:
        subjects = Subject.query.filter(Subject.name.ilike(f"%{search_query}%")).all()
        quizzes = Quiz.query.filter(Quiz.title.ilike(f"%{search_query}%")).all()
    else:
        subjects = Subject.query.all()
        quizzes = Quiz.query.all()
    for subject in subjects:
        chapters =subject.chapters
        for chapter in chapters:
            total_questions = 0
            for quiz in chapter.quizzes:
                total_questions += len(quiz.questions)
            chapter.question_count = total_questions
    return render_template("admin_dash.html", subjects=subjects, quizzes =quizzes, search_query=search_query)


# ----User Part------
@app.route("/user_dashboard/<int:user_id>", methods=["GET", "POST"])
def user_dashboard(user_id):
    if 'user_id' not in session:
        return redirect(url_for("login"))
    this_user = User.query.get_or_404(user_id)
    if session["user_id"] != user_id:
        return redirect(url_for("login"))
    search_query = request.args.get('search_query')
    date_filter = request.args.get('date_filter') 
    user_scores_query = Score.query.filter_by(user_id=user_id)
    if search_query:
        user_scores_query = user_scores_query.join(Quiz).filter(Quiz.title.ilike(f"%{search_query}%"))
    if date_filter:
        try:
            filter_date = datetime.strptime(date_filter, '%Y-%m-%d').date()
            user_scores_query = user_scores_query.filter(func.date(Score.time_stamp_of_attempt) == filter_date)
        except ValueError:
            flash("Invalid date format. Please use YYYY-MM-DD.", "error")

    user_scores = user_scores_query.all()
    today = date.today()
    upcoming_quizzes = Quiz.query.filter(Quiz.date_of_quiz >= today).all()
    return render_template(
        "user_dash.html",
        user=this_user,
        upcoming_quizzes=upcoming_quizzes,
        user_scores=user_scores,
        search_query=search_query,
        date_filter=date_filter)
    

def calculate_time_left(duration, start_time_str):
    try:
        start_time_utc = datetime.fromisoformat(start_time_str).replace(tzinfo=pytz.utc)
        now_utc = datetime.now(pytz.utc)  
        quiz_end_time_utc = start_time_utc + timedelta(hours=duration.hour, minutes=duration.minute, seconds=duration.second)

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
    if 'quiz_data' not in session or session['quiz_data'].get('quiz_id') != quiz_id:
        session['quiz_data'] = {
            'quiz_id': quiz_id,
            'question_index': 0,
            'answers': {},  # Use a dictionary to store answers
            'start_time': datetime.utcnow().isoformat()
        }
        print(f"Quiz data initialized in session: {session['quiz_data']}") 

    quiz_data = session['quiz_data'] #RETRIEVE FROM SESSION, NOT .GET()
    current_question_index = quiz_data['question_index']

    if current_question_index >= total_questions:
        # Quiz is complete, calculate and save score
        score = calculate_score(quiz_id, quiz_data['answers'])
        save_score(quiz_id, user_id, score)
        session.pop('quiz_data', None)  # Clear quiz data
        print("Quiz completed, redirecting to view_scores")
        return redirect(url_for("view_scores", user_id=user_id))

    question = questions[current_question_index]
    selected_answer = quiz_data['answers'].get(str(question.id)) 

    start_time_str = quiz_data['start_time']
    time_left = calculate_time_left(quiz.duration, start_time_str)

    if request.method == "POST":
        answer = request.form.get('answer')
        if answer:
            quiz_data['answers'][str(question.id)] = answer
            session['quiz_data'] = quiz_data
            session.modified = True
            print(f"Answer submitted: {answer}, Quiz data: {session['quiz_data']}")
        else:
            flash("Please select an answer.","error")
            
        if request.form.get('action') == 'next':
            quiz_data['question_index'] += 1
            session['quiz_data'] = quiz_data
            session.modified = True
            print("Moving to next question")
            return redirect(url_for("start_quiz", quiz_id=quiz_id))
        elif request.form.get('action') == 'submit':
            score = calculate_score(quiz_id, quiz_data['answers'])
            save_score(quiz_id, user_id, score)
            session.pop('quiz_data', None)
            print("Quiz submitted, redirecting to view_scores")
            return redirect(url_for("view_scores", user_id=user_id))

    return render_template(
        'start_quiz.html',
        quiz=quiz,
        question=question,
        current_question_index=current_question_index + 1,
        total_questions=total_questions,
        time_left=time_left,
        selected_answer=selected_answer
    )
def calculate_score(quiz_id,answers):
    quiz = Quiz.query.get_or_404(quiz_id)
    questions = quiz.questions
    score =0
    print(f"Answer in calculate_Score: {answers}")
    for question in questions:
        question_id_str = str(question.id)
        print(f"Correct option for question {question.id}:{question.correct_option}")
        if question_id_str in answers and answers[question_id_str] is not None:
            try:
                user_answer = int(answers[question_id_str])
                if user_answer == question.correct_option:
                    score +=1
            except ValueError:
                print(f"Invalid answer format for question {question.id}")
            except AttributeError:
                print(f"Question object{question.id} does not have 'correct_option attribute") 
    return score                       

def save_score(quiz_id, user_id, score):
    new_score = Score(quiz_id = quiz_id, user_id =user_id, total_scored =score)
    db.session.add(new_score)
    db.session.commit()
    return new_score


@app.route("/view_quiz/<int:quiz_id>")
def view_quiz(quiz_id):
    if "user_id" not in session:
        return redirect(url_for('login'))
    quiz = Quiz.query.get_or_404(quiz_id)
    return render_template("view_quiz.html", quiz=quiz, user_id = session["user_id"])



# Scores Controllers
@app.route("/view_scores/<int:user_id>")
def view_scores(user_id):
    user=  User.query.get_or_404(user_id)
    scores = Score.query.filter_by(user_id = user.id).all()
    return render_template("view_scores.html", scores=scores,user_id =user_id, user=user)


@app.route("/logout")
def logout():
    return render_template('login.html')

# def subject_attempt_chart(user_id):
#     scores = Score.query.filter_by(user_id = user_id).all()
#     subject_counts ={}
#     for score in scores:
#         subject_name = score.quiz.chapter.subject.name
#         subject_counts[subject_name] = subject_counts.get(subject_name,0) + 1
#     if not subject_counts:
#         return None;
#     subjects = list(subject_counts.keys())
#     counts = list(subject_counts.values())
    
#     plt.figure(figsize = (8,6))
#     plt.bar(subjects, counts, color="skyblue")
#     plt.xlabel("Subjects")
#     plt.ylabel("Number of Attempts")
#     plt.title("Subject-wise Quiz Attempts")
#     plt.xticks(rotation =45, ha ='right')
#     plt.tight_layout()
    
#     img_path = os.path.join(app.root_path, 'static', 'img1.png')
#     plt.save(img_path)
#     plt.close()
    
    
# def month_wise_attempt_chart(user_if):
#     scores = Score.query.filter_by(user_id=user_id).all()
#     month_counts = {}
#     for score in scores:
#         month = score.time_stamp_of_attempt.strftime("%B")
#         month_counts[month] = month_counts.get(month, 0) + 1

#     if not month_counts:
#         return None
    
#     months = list(month_counts.keys())
#     counts = list(month_counts.values())

#     plt.figure(figsize=(6, 6))
#     plt.pie(counts, labels=months, autopct='%1.1f%%', startangle=140)
#     plt.title("Month-wise Quiz Attempts")
#     plt.tight_layout()
    
#     img_path = os.path.join(app.root_path, 'static', 'img2.png')
#     plt.savefig(img_path)
#     plt.close()
    
    
# @app.route('/summary')
# def summary():
#     user_id = session.get("user_id")
#     if not user_id:
#         return redirect(url_for('login'))
#     return render_template("summary.html")
    