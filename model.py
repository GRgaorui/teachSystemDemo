from flask_sqlalchemy import SQLAlchemy
from config import *

db = SQLAlchemy(app)

class Course(db.Model):
    __tablename__ = 'Course_info'
    id = db.Column(db.Integer , primary_key = True)
    Course_name = db.Column(db.String(16), nullable=False)
    Course_college = db.Column(db.String(16), nullable=False)
    Course_major = db.Column(db.String(16), nullable=False)
    Course_class = db.Column(db.String(16), nullable=False)
    Course_teacher = db.Column(db.String(16), nullable=False)
    Course_leader = db.Column(db.String(16))
    Major_leader = db.Column(db.String(16))
    Course_state = db.Column(db.Integer, db.ForeignKey('course_state.id'))
    info = db.Column(db.Text(65535))
    def to_json(self):
        json_Courses = {
            'id': self.id,
            'Course_name': self.Course_name,
            'Course_college': self.Course_college,
            'Course_major': self.Course_major,
            'Course_class': self.Course_class,
            'Course_teacher': self.Course_teacher,
            'Course_leader':self.Course_leader,
            'Major_leader':self.Major_leader,
            'Course_state':self.state_name.state,
            'info':self.info
        }
        return json_Courses
    def __repr__(self):
        return '<Course {}>'.format(self.Course_name)
    

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer , primary_key = True)
    User_num = db.Column(db.String(16), nullable=False)
    User_name = db.Column(db.String(16), nullable=False)
    User_email = db.Column(db.String(32), nullable=False)
    User_password = db.Column(db.String(16), nullable=False)
    Type_admin = db.Column(db.Integer, server_default='0')
    Type_Course_teacher = db.Column(db.Integer, server_default='0')
    Type_Course_leader = db.Column(db.Integer, server_default='0')
    Type_Major_leader = db.Column(db.Integer, server_default='0')
    def to_json(self):
        json_users = {
            'id': self.id,
            'User_num': self.User_num,
            'User_name': self.User_name,
            'User_email': self.User_email,
            'User_password': self.User_password,
            'Type_admin':self.Type_admin,
            'Type_Course_teacher':self.Type_Course_teacher,
            'Type_Course_leader':self.Type_Course_leader,
            'Type_Major_leader':self.Type_Major_leader
        }
        return json_users
    def __repr__(self):
        return '<User {}>'.format(self.User_name)

class Type(db.Model):
    __tablename__ = 'user_type'
    id = db.Column(db.Integer , primary_key = True)
    Type_name = db.Column(db.String(16), nullable=False)
    def to_json(self):
        json_type = {
            'id': self.id,
            'Type_name': self.Type_name,
        }
        return json_type
    def __repr__(self):
        return '<Type {}>'.format(self.Type_name)

class Up_file(db.Model):
    __tablename__ = 'Up_file'
    id = db.Column(db.Integer , primary_key = True)
    course_id = db.Column(db.Integer , nullable=False)
    Material_upload = db.Column(db.String(510))
    def to_json(self):
        json_up_file = {
            'id': self.id,
            'course_id': self.course_id,
            'Material_upload': self.Material_upload,
        }
        return json_up_file
    def __repr__(self):
        return '<Type {}>'.format(self.id)

class course_state(db.Model):
    __tablename__ = 'course_state'
    id = db.Column(db.Integer , primary_key = True)
    state = db.Column(db.String(128))
    courses = db.relationship('Course', backref='state_name') #relationship 一对多，要写在一的那一边
    def to_json(self):
        json_course_state = {
            'id': self.id,
            'state': self.state,
        }
        return json_course_state