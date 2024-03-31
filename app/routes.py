from flask import request, render_template
from . import app, db
from datetime import datetime
from .models import Task, User
from .auth import basic_auth, token_auth

#just a little message for the main page
@app.route('/') 
def home():
    home_st = 'Still building out the site, check out the tasks though!'
    return home_st



#USER endpoints!!!

#create a new user POST
@app.route('/users', methods=['POST'])
def create_user():
    #check to make sure the request body is JSON
    if not request.is_json:
        return {'error': 'You content-type must be application/json'}, 400
    # Get the data from the request body
    data = request.json

    # Validate that the data has all of the required fields
    required_fields = ['firstName', 'lastName', 'username', 'email', 'password']
    missing_fields = []
    for field in required_fields:
        if field not in data:
            missing_fields.append(field)
    if missing_fields:
        return {'error': f"{', '.join(missing_fields)} must be in the request body"}, 400
    #pull the individual data from the body
    first_name = data.get('firstName')
    last_name = data.get('lastName')
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    #check to see if any current users already have the username and/or email
            #in terminal - select_stmt3 = db.select(User).where(User.id > 3)   ----  select_stmt5 = db.select(User).where( (User.id > 3) | (User.username=='bstanton')  --- db.session.execute(select_stmt5).scalars().all()
            #db.session.execute(db.select(User).where( (User.username == username) | (User.email == email) )).scalars().all()
    check_users = db.session.execute(db.select(User).where( (User.username == username) | (User.email == email) )).scalars().all()
    if check_users:
        return {'error': "A user with that username and/or email already exists"}, 400

    #create a new instance of user with the data rom the request
    new_user = User(first_name=first_name, last_name=last_name,  username=username, email=email, password=password)

    return new_user.to_dict(), 201

#get token route
@app.route('/token')
@basic_auth.login_required
def get_token():
    user = basic_auth.current_user()
    return user.get_token()


#- [GET] /users/<user_id> - Get a user by id in dictionary form or return a 404 status
@app.route('/users/<int:user_id>')
def get_user(user_id):
    #get user from db by id
    user = db.session.get(User, user_id)
    if user:
        return user.to_dict()
    else:
        return {'error': f"User with an ID of {user_id} does not exist"}, 404
    
# [PUT] /users/<user_id> *token auth required - Update a user by id, user must be trying to update itself
@app.route('/users/<int:user_id>', methods=['PUT'])
@token_auth.login_required
def edit_user(user_id):
    # Check to see that they have a JSON body
    if not request.is_json:
        return {'error': 'You content-type must be application/json'}, 400
    # Let's the find user in the db
    user = db.session.get(User, user_id)
    if user is None:
        return {'error': f"User with an ID of {user_id} does not exist"}, 404
    # Get the current user based on the token
    current_user = token_auth.current_user()
    if current_user != user:
        return {'error': "This is not your account. You do not have permission to edit"}, 403

    # Get the data from the request
    data = request.json
    #pass data into users update method
    user.update(**data)
    return user.to_dict()


#[DELETE] /users/<user_id> *token auth required - Delete a user by id, user must be trying to delete itself
@app.route('/users/<int:user_id>', methods=['DELETE'])
@token_auth.login_required
def delete_user(user_id):
    #see if post exists - no need to check json because just deleting anyway
    user = db.session.get(User, user_id)
    if user is None:
        return {'error': f"User with an ID of {user_id} does not exist"}, 404
    
    #ensure that person deleting account is same person that owns account
    current_user = token_auth.current_user()
    if user != current_user:
        return {'error': "This is not your account. You do not have permission to edit"}, 403
    
    #delete user
    user.delete()
    return {'success': f"User with ID-{user.id} was successfully deleted"}, 200






#get all tasks
@app.route('/tasks')
def get_tasks():
    select_stmt = db.select(Task)
    search = request.args.get('search')
    if search:
        select_stmt = select_stmt.where(Task.title.ilike(f"%{search}%"))
    tasks = db.session.execute(select_stmt).scalars().all()    
    return [t.to_dict() for t in tasks]


#get single task [GET] /tasks/<task_id> - Get a task in dictionary form based on the ID or return a 404 status
@app.route('/tasks/<int:task_id>')
def get_task(task_id):
    task = db.session.get(Task, task_id)
    if task:
        return task.to_dict()
    else:
        return {'error': f"Task with an ID of {task_id} does not exist"}, 404


#[POST] /tasks *token auth required - Create a new task with a title and description, returns the new task with a 201 status
@app.route('/tasks', methods=['POST']) #make a post request by setting method
@token_auth.login_required
def create_task():
    #check if JSON
    if not request.is_json:
        return {'error': 'Your content-type must be application/json'}, 400
    #get data
    data = request.json
    #make sure required fields(title, description) are validated
    required_fields = ['title', 'description']
    missing_fields = []
    for field in required_fields:
        if field not in data:
            missing_fields.append(field)
    if missing_fields:
        return {'error': f"{', '.join(missing_fields)} must be in the request body"}, 400
    
    title = data.get('title')
    description = data.get('description')

    current_user = token_auth.current_user()

    #not too much required info to check for and cant access ID yet
    # for task in tasks:
    #     if task['title'] == title or task['description'] == description:
    #         return {'error': "A task with that title and/or description already exists"}, 400

    new_task = Task(title=title, description=description, user_id=current_user.id)

    return new_task.to_dict(), 201


#[PUT] /tasks/<task_id> *token auth required - Update a task by id, task must be created by user trying to update
@app.route('/tasks/<int:task_id>', methods=['PUT'])
@token_auth.login_required
def edit_task(task_id): 
    # Check to see that they have a JSON body
    if not request.is_json:
        return {'error': 'You content-type must be application/json'}, 400
    # Let's the find task in the db
    task = db.session.get(Task, task_id)
    if task is None:
        return {'error': f"Task with ID #{task_id} does not exist"}, 404
    # Get the current user based on the token
    current_user = token_auth.current_user()
    #make sure current user is author of task
    if current_user != task.author:
        return {'error': "This is not your task. You do not have permission to edit"}, 403
    
    #get data from req
    data = request.json
    #pass data into update method
    task.update_task(**data)
    return task.to_dict()


#[DELETE] /tasks/<task_id> *token auth required - Delete a task by id, task must be created by user trying to delete
@app.route('/tasks/<int:task_id>', methods=['DELETE'])
@token_auth.login_required
def delete_task(task_id):
    #no need to check json just see if it exists
    task = db.session.get(Task, task_id)
    if task is None:
        return {'error': f"Task with ID #{task_id} does not exist"}, 404
    
    #make sure person deleting task is the author
    current_user = token_auth.current_user()
    if task.author != current_user:
        return {'error': "This is not your task. You do not have permission to delete"}, 403    
    
    #if it is theirs - let them delete
    task.delete_task()
    return {'success': f"{task.title} was successfully deleted"}, 200