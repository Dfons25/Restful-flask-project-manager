from flask_restplus import Resource, fields, Namespace
from flask_login import login_user, login_required, logout_user, current_user
import routes.database.queries as db
import routes.database.structure as models

"""
Module responsible for handling the api
Will only recieve and send json 
"""

endpoint = Namespace('api', description='api related endpoints')


"""
Models used by flask_restplus to determine the type of data the api should expect
"""

rf_user_login = endpoint.model('user_login', {
    'username': fields.String,
    'password': fields.String
})


rf_user = endpoint.inherit('user', rf_user_login, {
    'name': fields.String,
    'email': fields.String
})

rf_userbasic = endpoint.model('userbasic', {
    'username': fields.String,
    'name': fields.String,
    'email': fields.String
})

rf_userpw = endpoint.model('userpw', {
    'password_a': fields.String,
    'password_n': fields.String
})

rf_task = endpoint.model('task', {
    'user_id': fields.Integer,
    'title': fields.String,
    'due_date': fields.Date,
    'completed': fields.Boolean
})

rf_order = endpoint.model('order', {
    'order': fields.Integer,
})

rf_project = endpoint.model('project', {
    'user_id': fields.Integer,
    'name': fields.String
})


"""
Register a new user
Will check if the data is correct according the Marshmallow validation pattern
Will check if username is avaliable
"""

@endpoint.route('/user/register/')
class RegisterUser(Resource):

    @endpoint.expect(rf_user)
    def post(self):

        json_object = endpoint.payload

        user = models.UserSchemaValidate().load(json_object)
        if not user.errors:

            saved_user = db.register_user(json_object)
            if saved_user:

                return models.UserSchemaConvert().dump(saved_user).data, 200

        return user.errors, 400

"""
Login user
Will check if the data is correct according the Marshmallow validation pattern
"""


@endpoint.route('/user/login/')
class LoginUser(Resource):

    @endpoint.expect(rf_user_login)
    def post(self):

        json_object = endpoint.payload

        user = db.login(json_object['username'], json_object['password'])
        if user:

            login_user(user)
            return ({'redirect': '/app/board'}), 200

        return {'message': 'Invalid credentials'}, 400

"""
Logout user
"""

@endpoint.route('/user/logout/')
class LogoutUser(Resource):

    @login_required
    def get(self):

        logout_user()

        return {'redirect': '/app/user/logout'}, 200

"""
Will return the current logged user
In other words, the user will return itself in order to know his id within the app
"""

@endpoint.route('/current_user')
@endpoint.hide
class GetCurrentUser(Resource):

    @login_required
    def get(self):

        return models.UserSchemaConvert().dump(current_user).data, 200

"""
Get Delete Put endpoints of a user object
Will check if the data is correct according the Marshmallow validation pattern
"""

@endpoint.doc(params={'id': 'User id'})
@endpoint.route('/user/<id>')
class UserGDP(Resource):

    @login_required
    def get(self, id):

        user = db.get_user(id)

        if user and id == db.current_user.get_id():
            return models.UserSchemaConvert().dump(user).data, 200
        return {'message': 'Invalid operation'}, 404

    @login_required
    def delete(self, id):

        user = db.get_user(id)

        if user and id == db.current_user.get_id():
            db.remove_user(id)
            return {'message': 'User removed'}, 201

        return {'message': 'Invalid operation'}, 404

    @login_required
    @endpoint.expect(rf_userbasic)
    def put(self, id):
        user = db.get_user(id)
        json_object = endpoint.payload

        updated_user = models.UserInfoSchemaValidate().load(json_object)

        if not updated_user.errors:

            updated_user = db.update_user(user, json_object)

            if updated_user:
                return models.UserSchemaConvert().dump(updated_user).data, 200
            return {'message': 'Invalid operation'}, 404

        return updated_user.errors, 400


"""
Put endpoint of a user password
Since the user password will be encrypted, the user has to provide the old password in order
to get a valid match
"""


@endpoint.doc(params={'id': 'User id'})
@endpoint.route('/userpw/<id>')
class UserGDP(Resource):

    @endpoint.expect(rf_userpw)
    def put(self, id):

        user = db.get_user(id)
        json_object = endpoint.payload

        if db.check_password(json_object['password_a'], user.password):

            updated_user = db.update_user(user, json_object)
            if updated_user:
                return models.UserSchemaConvert().dump(updated_user).data, 200

        return {'message': 'Invalid operation'}, 404

"""
Get Put Delete endpoints of a Project object
Will check if the data is correct according the Marshmallow validation pattern
"""

@endpoint.doc(params={'id': 'Project id'})
@endpoint.route('/projects/<id>')
class ProjectGPD(Resource):

    @login_required
    def get(self, id):
        project = db.get_project(id)
        if project:
            return models.ProjectSchemaConvert().dump(project).data, 200

        return {'message': 'Invalid operation'}, 404

    @login_required
    @endpoint.expect(rf_project)
    def put(self, id):

        json_object = endpoint.payload

        old_project = db.get_project(id)
        project = models.ProjectSchemaValidate().load(json_object)

        if not project.errors:
            updated_project = db.update_project(json_object, old_project)

            if updated_project:
                return models.ProjectSchemaConvert().dump(updated_project).data, 200

        return project.errors, 400

    @login_required
    def delete(self, id):

        project = db.get_project(id)
        if project:
            db.remove_project(id)
            return {'message': 'Removed Project'}, 201

        return {'message': 'Invalid operation'}, 404

"""
Get Put endpoints of Project objects
Will check if the data is correct according the Marshmallow validation pattern
"""

@endpoint.route('/projects')
class UserProjects(Resource):

    @login_required
    def get(self):

        project_list = db.get_user_projects(current_user.get_id())
        if project_list:
            return models.ProjectSchemaConvert().dump(project_list, many=True).data, 200
        return {'message': 'Invalid operation'}, 400

    @login_required
    @endpoint.expect(rf_project)
    def post(self):

        json_object = endpoint.payload

        project = models.ProjectSchemaValidate().load(json_object)

        if not project.errors:

            saved_project = db.add_project(json_object)
            if saved_project:

                return models.ProjectSchemaConvert().dump(saved_project).data, 200

            return {'message': 'Invalid operation'}, 404
        return project.errors, 400

"""
Get Put endpoints of Task objects
Will check if the data is correct according the Marshmallow validation pattern
"""

@endpoint.doc(params={'id': 'Project id'})
@endpoint.route('/projects/<id>/tasks')
class TasksGP(Resource):

    @login_required
    def get(self, id):

        task_list = db.get_tasks(id)

        if task_list:
            return models.TaskSchemaConvert().dump(task_list, many=True).data, 200
        return {'message': 'Invalid operation'}, 404

    @login_required
    @endpoint.expect(rf_task)
    def post(self, id):

        json_object = endpoint.payload

        task = models.TaskSchemaValidate().load(json_object)

        if db.get_task_title(json_object['title'], id):
            task.errors.update({'Task_Name': 'Task already exists'})

        if not task.errors:
            saved_task = db.add_task(json_object, id)

            if saved_task:
                return models.TaskSchemaConvert().dump(saved_task).data, 200
            return {'message': 'Invalid operation'}, 404

        return task.errors, 400

"""
Put endpoints of a Task object
This endpoint has the purpose of differenciate the update task info from the reorder task options
"""

@endpoint.doc(params={'project_id': 'Project id', 'task_id': 'Task id'})
@endpoint.route('/projects/<project_id>/tasksReorder/<task_id>')
class ProjectGPD(Resource):

    @endpoint.expect(rf_order)
    @login_required
    def put(self, project_id, task_id):

        json_object = endpoint.payload

        old_task = db.get_project_task(project_id, task_id)

        if old_task:
            updated_task = db.reorder_task(old_task, json_object)
            if updated_task:
                return models.TaskSchemaConvert().dump(updated_task).data, 200
        return {'message': 'Invalid operation'}, 404

"""
Get Put Delete endpoints of a Project object
Will check if the data is correct according the Marshmallow validation pattern
"""

@endpoint.doc(params={'project_id': 'Project id', 'task_id': 'Task id'})
@endpoint.route('/projects/<project_id>/tasks/<task_id>')
class TasksGPD(Resource):

    @login_required
    def get(self, project_id, task_id):
        task = db.get_project_task(project_id, task_id)
        if task:
            return models.TaskSchemaConvert().dump(task).data, 200
        return {'message': 'Invalid operation'}, 404

    @endpoint.expect(rf_task)
    @login_required
    def put(self, project_id, task_id):

        json_object = endpoint.payload

        old_task = db.get_project_task(project_id, task_id)

        task = models.TaskSchemaValidate().load(json_object)

        if not task.errors:
            updated_task = db.update_task(old_task, json_object)

            if updated_task:
                return models.TaskSchemaConvert().dump(updated_task).data, 200
            return {'message': 'Invalid operation'}, 404

        return task.errors, 400

    @login_required
    def delete(self, project_id, task_id):
        task = db.get_project_task(project_id, task_id)
        if task:
            db.remove_task(task_id)
            return {'message': 'Removed Task'}
        return {'message': 'Invalid operation'}, 404
