from flask_restful import Api, Resource, reqparse, abort 
from .models import *
from .database import db

subject_parser = reqparse.RequestParser()
subject_parser.add_argument('name', type=str, required =True, help ='Subject name is required')
subject_parser.add_argument('description', type =str)

chapter_parser = reqparse.RequestParser()
chapter_parser.add_argument('name', type =str, required= True,help ='Chapter name is required' )
chapter_parser.add_argument('description', type=str)
subject_parser.add_argument('subject_id', type =int, required=True, help ="subject id is required")

quiz_parser = reqparse.RequestParser()
quiz_parser.add_argument('chapter_id', type =int, required=True,help="Chapter id is required" )
quiz_parser.add_argument('date_of_quiz', type=str)
quiz_parser.add_argument('time_duration',type=str)
quiz_parser.add_argument('remarks', type=str)



class SubjectResource(Resource):
    def get(self, subject_id):
        subject =Subject.query.get_or_404(subject_id)
        return {'id':subject.id, 'name': subject.name, 'description':subject.desciption}
        
    def put(self, subejct_id):
        subject = Subject.query.get_or_404(subject_id)
        args = subejct_parser.parse_args()
        subject.name =args['name']
        subejct.description  = args['description']
        db.session.commit()
        return {'message': 'Subject updated', 'subject':{'id':subject.id, 'name': subject.name, 'description':subject.description}}
        
    def delete(self,subject_id):
        subject = Subject.query.get_or_404(subject_id)
        db.session.delete(subject)
        db.session.commit()
        return {'message':'subject deleted'}



class SubjectListResource(Resource):
    def get(self):
        subjects = Subject.query.all()
        subject_list = [{'id': s.id, 'name':s.name, 'description':s.description} for s in subjects]
        return {'subjects': subject_list}
        
    def post(self):
        args = subejct_parser.parse_args()
        new_subject = Subject(name =args['name'], description = args['description'])
        db.session.add(new_subject)
        db.session.commit()
        return {'message': 'Subject created', 'subject':{'id':new_subject.id, 'name': new_subject.name, 'description':new_subject.description }},201
        
        
class ChapterResource(Resource):
    def get(self, chapter_id):
        chapter = Chapter.query.get_or_404(chapter_id)
        return {'id': chapter_id,'name': chapter.name, 'description':chapter.description, 'subject_id': chapter.subject_id}
        
    def put(self, chapter_id):
        chapter = Chapter.query.get_or_404(chapter_id)
        args = chapter_parser.parse_args()
        chapter.name =args['name']
        chapter.description = args['description']
        chapter.subject_id = args['subject_id']
        db.session.commit()
        return {'message': 'Chapter updated', 'chapter':{'id':chapter.id, 'name': chapter.name, 'description': chapter.description, 'subject_id': chapter.subject_id}}
    
    
    def delete(self, chapter_id):
        chapter = Chapter.query.get_or_404(chapter_id)
        db.session.delete(chapter)
        db.session.commit()
        return {'message': 'Chapter deleted'}
        
        
        
class ChapterListResource(Resource):
    def get(self):
        chapters =Chapter.query.all()
        chapter_list = [{'id': c.id, 'name': c.name, 'description':c.description, 'subject_id': c.subject_id} for c in chapters ]
        return {'chapters': chapter_list}
        
    def post(self):
        args = chapter_parser.parse_args()
        new_chapter = Chapter(name =args['name'], description = args['description'],subject_id =args['subject_id'])
        db.session.add(new_chapter)
        db.session.commit()
        return {'message': 'Chapter created', 'chapter':{'id': new_chapter.id,'name': new_chapter.name, 'description': new_chapter.description, 'subject_id': new_chapter.subject.id}},201
        
    

class QuizResource(Resource):
    def get(self, quiz_id):
        quiz = Quiz.query.get_or_404(quiz_id)
        return {'id': quiz.id, 'chapter_id': quiz.chapter_id,'date_of_quiz':quiz.date_of_quiz, 'time_duration':quiz.time_duration, 'remarks': quiz.remarks  }
    
    def  put(self, quiz_id):
        quiz = Quiz.query.get_or_404(quiz_id)
        args = quiz_parser.parse_args()
        quiz.chapter_id = args['chapter_id']
        quiz.date_of_quiz =args['date_of_quiz']
        quiz.time_duration =args['time_duration']
        quiz.remarks = args['remarks']
        db.session.commit()
        return {'message':'Quiz updated', 'quiz':{'id':quiz.id, 'chapter_id':quiz.chapter_id, 'date_of_quiz':quiz.date_of_quiz, 'time_duration': quiz.time_duration,'remarks':quiz.remarks}}
        
        
    def delete(self, quiz_id):
        quiz= Quiz.query.get_or_404(quiz_id)
        db.session.delete(quiz)
        db.session.commit()
        return {'message':'Quiz deleted'}
        
        
        
class QuizListResource(Resource):
    def get(self):
        quizzes = Quiz.query.all()
        quiz_list = [{'id': q.id, 'chapter_id': q.chapter_id, 'date_of_quiz': q.date_of_quiz, 'time_duration': q.time_duration, 'remarks': q.remarks}for q in quizzes]
        return {'quizzes': quiz_list}

    def post(self):
        args= quiz_parser.parse_args()
        new_quiz = Quiz(chapter_id = args['chapter_id'], date_of_quiz = args['date_of_quiz'], time_duration = args['time_duration'],remarks =args['remarks']) 
        db.session.add(new_quiz)
        db.session.commit()
        return {'message': 'Quiz Created', 'quiz': {'id':new_quiz.id, 'chapter_id': new_quiz.chapter_id, 'date_of_quiz': new_quiz.date_of_quiz, 'time_duration': new_quiz.time_duration, 'remarks': new_quiz.remarks}},201
        
