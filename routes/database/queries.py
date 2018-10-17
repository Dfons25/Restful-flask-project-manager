from flask import Flask
from flask_login import LoginManager,  current_user
from flask_sqlalchemy import SQLAlchemy, get_debug_queries
from .structure import User, Task, Project, db
from flask_httpauth import HTTPBasicAuth
from bcrypt import checkpw, hashpw, gensalt
import datetime


login_manager = LoginManager()
auth = HTTPBasicAuth()


"""
Wrappers/Decorators to check if the owner of the object is the same as the current logged user
"""

def checkProjectOwner(func):

    def wrapper(*args, **kwargs):

        print(args)
        if args[0]['user_id']:
            if int(args[0]['user_id']) == int(current_user.get_id()):
                content = func(*args, **kwargs)
                return content

            return
    return wrapper


def checkUserIdIsCurrentId(func):

    def wrapper(*args, **kwargs):

        if int(args[0]) == int(current_user.get_id()):
            content = func(*args, **kwargs)
            return content

        return

    return wrapper



def checkProjectIdIsCurrentId(func):

    def wrapper(*args, **kwargs):

        project = Project.query.get(int(args[0]))

        if project.user_id == int(current_user.get_id()):
            content = func(*args, **kwargs)
            return content

        return

    return wrapper


@login_manager.user_loader
def get_user(user_id):
    if user_id:
        return User.query.get(int(user_id))
    return


def get_user_name(username):
    return User.query.filter_by(username=username).first()


def get_user_id_username(id):
    user = User.query.filter_by(id=id).first()
    return user.username


def update_user(user, newInfo):

    if user.id == int(current_user.get_id()):

        if 'password_n' in newInfo:
            User.query.filter_by(id=user.id).update(dict(password=hashpw(newInfo['password_n'].encode(), gensalt())))
        else:
            User.query.filter_by(id=user.id).update(dict(name=newInfo['name'],
                                                         email=newInfo['email'],
                                                         username=newInfo['username']))
        db.session.commit()
        updated_user = User.query.get(int(user.id))
        return updated_user


@checkUserIdIsCurrentId
def remove_user(user_id):
    user = User.query.get(int(user_id))
    user_projects = Project.query.join(User).filter(
        Project.user_id == user_id).order_by(Project.last_updated.desc()).all()
    for project in user_projects:
        for task in project.task_proj:
            db.session.delete(task)
        remove_project(project.id)
    db.session.delete(user)
    db.session.commit()


def register_user(form):
    user = User(**form)
    user.password = hashpw(user.password.encode(), gensalt())
    db.session.add(user)
    db.session.commit()
    return user


def check_password(outside_password, db_password):
    if checkpw(outside_password.encode(), db_password):
        return True
    return False


@auth.verify_password
def login(username, password):
    temp_user = User.query.filter_by(username=username).first()
    if not temp_user or not check_password(password, temp_user.password):
        return False
    return temp_user


@checkProjectIdIsCurrentId
def get_project(project_id):
    return Project.query.get(int(project_id))


def get_project_name(name):
    return Project.query.filter_by(name=name).first()


@checkProjectOwner
def add_project(project):

    db.session.add(
        Project(name=project['name'], user_id=project['user_id']))
    db.session.commit()
    project = Project.query.filter_by(
        user_id = project['user_id'], name = project['name']).first()
    return project



@checkUserIdIsCurrentId
def get_user_projects(user_id):
    return Project.query.join(User).filter(
        Project.user_id == user_id).order_by(Project.last_updated.desc()).all()


@checkProjectIdIsCurrentId
def get_project(project_id):
    return Project.query.get(int(project_id))


@checkProjectOwner
def update_project(newInfo, project):
    Project.query.filter_by(id=project.id).update(dict(name=newInfo['name'].encode()))
    db.session.commit()
    updated_project = Project.query.get(int(project.id))
    return updated_project


@checkProjectIdIsCurrentId
def remove_project(project_id):
    project = Project.query.filter_by(id=int(project_id)).first()
    if project.user.id == int(current_user.get_id()):
        for task in project.task_proj:
            db.session.delete(task)
        Project.query.filter_by(id=int(project_id)).delete()
        db.session.commit()


@checkProjectOwner
def add_task(task, id):
    project = get_project(id)

    due_date = datetime.datetime.strptime(task['due_date'], '%Y-%m-%d').date()
    next_order = get_task_next_order(id)

    db.session.add(
        Task(title=task['title'], order=next_order, due_date=due_date
                , project_id=project.id))
    db.session.commit()

    new_task = Task.query.filter_by(
        title=task['title'], project_id=project.id).first()

    return new_task


def get_task_next_order(project_id):
    task = Task.query.join(Project).filter(
        Task.project_id == project_id).order_by(Task.order.desc()).first()
    if not task:
        return 1
    return task.order + 1


def get_task_title(title, project_id):
    return Task.query.join(Project).filter(Task.title == title, Task.project_id == project_id).first()


@checkProjectIdIsCurrentId
def get_tasks(project_id):
    return Task.query.join(Project).filter(
        Task.project_id == project_id).order_by(Task.order.asc()).all()


@checkProjectIdIsCurrentId
def get_project_task(project_id, task_id):
    return Task.query.join(Project).filter(
        Task.project_id == project_id, Task.id == task_id).first()


@checkProjectIdIsCurrentId
def get_project_task_order(project_id, order):
    return Task.query.join(Project).filter(
        Task.project_id == project_id, Task.order == order).first()


@checkProjectIdIsCurrentId
def get_project_task_max(project_id):
    task = Task.query.join(Project).filter(
        Task.project_id == project_id).order_by(Task.order.desc()).first()
    return task.order


def reorder_task(task, new_info):

    max_task_order = get_project_task_max(task.project_id)

    if task.order == 1 and new_info['order'] == -1 or task.order == max_task_order and new_info['order'] == 1:
        return

    next_task = get_project_task_order(task.project_id, task.order + new_info['order'])
    aux_order = task.order

    Task.query.filter_by(id=task.id).update(dict(order=next_task.order))
    Task.query.filter_by(id=next_task.id).update(dict(order=aux_order))
    db.session.commit()

    updated_task = Task.query.get(int(task.id))

    return updated_task


def update_task(task, newInfo):

    due_date = datetime.datetime.strptime(newInfo['due_date'], '%Y-%m-%d').date()
    if newInfo['title'] == '':
        title = task.title
    else:
        title = newInfo['title']

    Task.query.filter_by(id=task.id).update(
        dict(title=title, due_date=due_date, completed=newInfo['completed']))

    db.session.commit()
    updated_task = Task.query.get(int(task.id))
    return updated_task


def remove_task(task_id):
    task = Task.query.filter_by(id=int(task_id)).first()
    if task.project.user.id == int(current_user.get_id()):
        Task.query.filter_by(id=int(task_id)).delete()
        db.session.commit()
