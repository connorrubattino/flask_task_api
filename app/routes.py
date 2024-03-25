from flask import request
from . import app
from fake_tasks.tasks import tasks_list


#just a little message for the main page
@app.route('/') 
def home():
    home_st = 'Still building out the site, check out the tasks though!'
    return home_st


#get all tasks
@app.route('/tasks')
def get_tasks():
    tasks = tasks_list
    return tasks


#get single post
@app.route('/tasks/<int:task_id>')
def get_task(task_id):
    tasks = tasks_list
    for task in tasks:
        if task['id'] == task_id:
            return task
    return {'error': f"Task with an ID of {task_id} does not exist"}, 404