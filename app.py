__author__ = "Gowtham"
__date__ = "6th Nov 2021"

from bottle import get, route, request, static_file, abort, post, default_app, response  # RESTAPI framework
from gevent.pywsgi import WSGIServer  # Server
from geventwebsocket.handler import WebSocketHandler
from db_connector import BooksInventory
from datetime import datetime

import os
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

@post("/register")
def register():
    """
    Handles new registrations
    Input : username,userpassword,useremail,isadmin - auto assigned / modified by admin ,issuper - auto assigned / modified by admin
    ,isactive- auto assigned ,lastlog - auto assigned ,datejoined - auto assigned,team
    :return:
    Message for visualization
    """
    if request.method == 'POST':
        dict_struct = request.params.dict
        username = dict_struct['uname'][0]
        userpassword = dict_struct['passw'][0]
        useremail = dict_struct['mail'][0]
        isadmin = False
        issuper = False
        isactive = True
        lastlog = datetime.utcnow()
        datejoined = datetime.utcnow()
        team = dict_struct['team'][0]
        params = {
        'user_name': username,
        'user_email': useremail,
        'user_password' : userpassword,
        'is_admin' : isadmin,
        'is_super_user' : issuper,
        'is_active': isactive,
        'last_login' : lastlog,
        'date_joined' : datetime.utcnow()
        }
        q = session.add_user_details(**params)
        if q:
            return 'Registered'
        else:
            return 'Failed'

@get("/userlogin")
def login():
    """
    It takes 2 parameters:-
    Username, Password to verify the credentials and update the last_login record in the user database table.
     Return the information either in json / handle authorization replies
     Auto assigns the folder access based on the Team name selection.
     Files comes under that team will be read accessible to user
    :return: json structure with following data
    Name, directory, list of code snippets user has access
     or if the user is admin returns a table with all records information fetched from database.
    """
    if request.method == 'GET':
        uname = request.params.dict['user'][0]
        passwd = request.params.dict['pwd'][0]
        login = session.get_all(uname,passwd,datetime.utcnow())
        if login and uname=='admin':
            complete_table = session.complete_table()
            return json.dumps(complete_table,indent=2)
        if login:
            complete_table = session.complete_table()
            return json.dumps(complete_table, indent=2)
        else:
             return 'Unauthorized'

@get('/update')
def update():
    """
    Only for admin, to grant access with admin or super user
    :return: Complete records after update in json
    """
    try:
        id = int(request.params.get('id'))
        author = request.params.get('author')
        book_name = request.params.get('bname')
        published_on = request.params.get('pubon')
        # Check if book id already exists in the db
        complete_table = [r for r in session.complete_table()]
        if id in complete_table:
            params = {'book_id': id, 'book_author': author, 'book_title': book_name,
                      'book_published_date': published_on, 'book_updated_date': datetime.utcnow()}
            update_field = session.update_book(**params)
            if update_field:
                # complete_table = session.complete_table()
                # return json.dumps(complete_table, indent=2)
                return 'Record updated'
            else:
                return 'Failed to update'
        else:
            return 'Book id doesnot exist'
    except Exception as e:
        return 'Update falied'+str(e)


@get('/add')
def add():
    """

    :return:
    """
    res = {}
    try:
        id = int(request.params.get('id'))
        book_name = request.params.get('name')
        book_author = request.params.get('author')
        published_date = request.params.get('date_published')
        date_added = datetime.utcnow()
        date_updated = datetime.utcnow()
        params = {'book_id': id,
                  'book_author': book_author,
                  'book_title': book_name,
                  'book_published_date': published_date,
                  'book_added_date': date_added.date(),
                  'book_updated_date': date_updated.date()}
        # Check if book id already exists in the db
        complete_table = [r for r in session.complete_table()]
        if id in complete_table:
            res = {'Book id exists':'Book id exists'}
        else:
            add_data = session.add_book_details(**params)
            res = {'Book added':'Book added'}

    except Exception as e:
        print(e)
        res = {'unable to add data':str(e)}
    return res

@get('/del')
def del_user():
    """
    Requires user id to delete the records from Database . Only accessible to admin
    :return:
    Message for visualization
    """
    user_id = request.params.get('id')
    delete_user = session.del_rec(user_id)
    if delete_user:
        # complete_table = session.complete_table()
        # return json.dumps(complete_table, indent=2)
        return 'Record Updated'
    else:
        return 'Unable to delete the record or no record found with current selection, Please logout and and login'

if __name__ == '__main__':  # Set up when running stand alone
    try:
        user_name = request.get_header('X-WEBAUTH-USER', 'admin')
        session = BooksInventory()
        check = session.get_all(user_name,'',datetime.utcnow())
        if check or user_name=='admin':
            pass
            db = BooksInventory()
            print('DB set')
        else:
            abort(401,'Un-authorized to view this webpage')
    except Exception as e:
        print(e)
    print('Starting localhost webserver at port 3031')
    server = WSGIServer(('localhost', 3031), default_app(), handler_class=WebSocketHandler)
    server.serve_forever()