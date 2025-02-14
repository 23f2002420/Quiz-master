from flask import Flask
import os
import pytz
from application.database import db
from application.resources import Api 
from flask_restful import Api as FR_Api

app= None

def create_app():
    app = Flask(__name__)
    app.debug=True
    app.config['SECRET_KEY'] = os.urandom(24)
    
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///quizmaster.sqlite3"
    db.init_app(app)
    api = FR_Api(app)  # create the Flask-RESTful Api instance

    from application.resources import SubjectListResource, SubjectResource, ChapterListResource, ChapterResource, QuizListResource, QuizResource # Import resources here!

    api.add_resource(SubjectListResource, '/subjects')
    api.add_resource(SubjectResource, '/subjects/<int:subject_id>')
    api.add_resource(ChapterListResource, '/chapters')
    api.add_resource(ChapterResource, '/chapters/<int:chapter_id>')
    api.add_resource(QuizListResource, '/quizzes')
    api.add_resource(QuizResource, '/quizzes/<int:quiz_id>')
    
    app.app_context().push()
    return app

app = create_app()
from application.controllers import *

if __name__=="__main__":
    app.run()
