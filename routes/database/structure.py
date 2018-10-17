from flask import Blueprint, render_template
from flask_sqlalchemy import SQLAlchemy, get_debug_queries
from flask_login import UserMixin
from flask_marshmallow import Marshmallow
from . import queries
from marshmallow import Schema, fields, ValidationError, validates, validate
import datetime


"""
Module where the database structure is handled
All tables are matched to a marshmallow ModelSchema for an automatic json convertion
All Schema can have their own validation rules
"""

db = SQLAlchemy()
ma = Marshmallow()

def _get_date():
    return datetime.datetime.utcnow()


"""
Task table
"""

class Task(db.Model):
    __tablename__ = 'task'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), nullable=False)
    order = db.Column(db.Integer, nullable=False)
    creation_date = db.Column(db.DateTime, default=_get_date)
    due_date = db.Column(db.Date, nullable=False)
    completed = db.Column(db.Boolean, unique=False, default=False)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)

"""
Task table to ModelSchema match
"""

class TaskSchemaConvert(ma.ModelSchema):
    class Meta:
        model = Task
        include_fk = True

"""
Schema validation rules
"""

class TaskSchemaValidate(Schema):
    user_id = fields.Integer(required=True)

    @validates('user_id')
    def validate_user_id(self, id):
        if not queries.get_user(id):
            raise ValidationError('Invalid user id')

"""
Project table
"""

class Project(db.Model):
    __tablename__ = 'project'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=False)
    creation_date = db.Column(db.DateTime, default=_get_date)
    last_updated = db.Column(db.DateTime, default=_get_date, onupdate=_get_date)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    task_proj = db.relationship("Task", backref='project')

"""
Project table to ModelSchema match
"""

class ProjectSchemaConvert(ma.ModelSchema):
    class Meta:
        model = Project
        include_fk = True

"""
Schema validation rules
"""

class ProjectSchemaValidate(Schema):
    name = fields.String(required=True, validate=[validate.Length(min=2, max=30)])
    user_id = fields.Integer(required=True)

    @validates('name')
    def validate_name(self, name):
        if queries.get_project_name(name):
            raise ValidationError('Project already exists')

    @validates('user_id')
    def validate_user_id(self, id):
        if not queries.get_user(id):
            raise ValidationError('Invalid user id')

"""
User table
"""

class User(UserMixin, db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(10), unique=True, nullable=False)
    email = db.Column(db.String(50), nullable=False)
    username = db.Column(db.String(15), nullable=False)
    password = db.Column(db.String(20), nullable=False)
    proj_user = db.relationship("Project", backref='user')

"""
User table to ModelSchema match
"""

class UserSchemaConvert(ma.ModelSchema):
    class Meta:
        model = User
        include_fk = True

"""
Schema validation rules
"""

class UserInfoSchemaValidate(Schema):
    name = fields.String(required=True, validate=[validate.Length(min=2, max=30)])
    email = fields.Email(required=True)
    username = fields.String(required=True, validate=[validate.Length(min=4, max=30)])

    @validates('username')
    def validate_username(self, username):

        if queries.get_user_name(username) and not queries.current_user.username == username:
            raise ValidationError('Name already exists')


class UserSchemaValidate(Schema):
    name = fields.String(required=True, validate=[validate.Length(min=2, max=30)])
    email = fields.Email(required=True)
    username = fields.String(required=True, validate=[validate.Length(min=4, max=30)])
    password = fields.String(required=True)

    @validates('username')
    def validate_username(self, username):
        if queries.get_user_name(username):
            raise ValidationError('Name already exists')