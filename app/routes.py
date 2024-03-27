from flask import request
from . import app, db
from datetime import datetime
from .models import Task


#just a little message for the main page
@app.route('/') 
def home():
    home_st = 'Still building out the site, check out the tasks though!'
    return home_st


#get all tasks
@app.route('/tasks')
def get_tasks():
    tasks = db.session.execute(db.select(Task)).scalars().all()    
    return [t.to_dict() for t in tasks]


#get single task
@app.route('/tasks/<int:task_id>')
def get_task(task_id):
    task = db.session.get(Task, task_id)
    if task:
        return task.to_dict()
    else:
        return {'error': f"Task with an ID of {task_id} does not exist"}, 404


#WILL SET UP DB LATER BUT TO CHECK AS OF NOW
tasks = []


@app.route('/tasks', methods=['POST']) #make a post request by setting method
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
    
    title = data['title'] #title = data.get('title')
    description = data['subscription']


    #not too much required info to check for and cant access ID yet
    # for task in tasks:
    #     if task['title'] == title or task['description'] == description:
    #         return {'error': "A task with that title and/or description already exists"}, 400

    new_task = {
        'id': len(tasks_list) + 1,
        'title': title,
        'description': description,
        'completed': False,
        'createdAt': datetime.utcnow(),
        'dueDate': data.get('dueDate')
    }

    tasks_list.append(new_task)

    return new_task, 201
    