#start by importing Flack class from flask module
from flask import Flask

# Create an instance of Flask called app which will be the central object
app = Flask(__name__)

#import the routes to the app -- need this below the app or else will cause circular import because when it goes over to routes to look for app, app will not yet be defined
from . import routes

