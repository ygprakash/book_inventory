__author__ = "Gowtham"
__date__ = "6th Nov 2021"

from bottle import get, route, request, static_file, abort, post, default_app, response  # RESTAPI framework
from gevent.pywsgi import WSGIServer  # Server
from geventwebsocket.handler import WebSocketHandler

import os
import datetime
import simplejson as json

root = os.path.dirname(os.path.realpath(__file__))  # Global Root path definition to find the file locations/directories

@get('/') # base dir
@get('/index.html')
@get('/index')
@get('/index/index.html')
@get('/index/')
def home():
    return static_file('index.html',root=os.path.join(root, 'templates'))

@get('/<path:path>') # Other routes to handle dependant front end libraries
@get('/index.html/<path:path>')
@get('/login.html/<path:path>')
@get('/index/<path:path>')
@get('/login')
@get('/login/<path:path>')
@get('/redirect.html/<path:path>')
def get_js(path):
    return static_file(path,root=os.path.join(root, 'templates'))

if __name__ == '__main__':  # Set up when running stand alone

    print('Starting localhost webserver at port 3031')
    server = WSGIServer(('localhost', 3031), default_app(), handler_class=WebSocketHandler)
    server.serve_forever()