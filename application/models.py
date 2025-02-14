from .database import db 
from datetime import datetime, date


class User(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(), unique=True, nullable = False)
    password = db.Column(db.String(), nullable=False)
    full_name = db.Column(db.String(), nullable=False)
    qualification = db.Column(db.String())
    dob = db.Column(db.Date)
    is_admin = db.Column(db.String(), default = "general")
    scores = db.relationship('Score', backref = 'user', lazy=True)
    
    
class Subject(db.Model):
    id =db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(), nullable=False)
    description = db.Column(db.Text, nullable =True)
    chapters = db.relationship('Chapter', backref ='subject',lazy = True)
    
    
class Chapter(db.Model):
    id = db.Column(db.Integer, primary_key = True) 
    name = db.Column(db.String(), nullable=False)
    description = db.Column(db.Text, nullable =False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)
    quizzes = db.relationship('Quiz', backref = 'chapter', cascade = "all, delete-orphan", lazy = True)    

class Quiz(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(100), nullable=False)
    chapter_id = db.Column(db.Integer, db.ForeignKey('chapter.id'), nullable=False)
    date_of_quiz = db.Column(db.Date, nullable=False)
    duration = db.Column(db.Time, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    questions = db.relationship('Question', backref = 'quiz', lazy = True)
    scores = db.relationship('Score', backref ='quiz',cascade = "all, delete, delete-orphan", lazy=True)
    
    
class Question(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'),nullable=False)
    question_title = db.Column(db.String(), nullable=False)
    option1 = db.Column(db.String(), nullable=False)
    option2 = db.Column(db.String(), nullable=False)
    option3 = db.Column(db.String(), nullable=False)
    option4 = db.Column(db.String(), nullable=False)
    correct_option = db.Column(db.Integer, nullable=False)
    

class Score(db.Model):
    id = db.Column(db.Integer, primary_key = True) 
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    time_stamp_of_attempt = db.Column(db.DateTime, default =datetime.utcnow)
    total_scored = db.Column(db.Integer, nullable = False)