import json
from flask_login import LoginManager, current_user, login_user, login_required
from flask import Flask, request, render_template, redirect, flash, url_for
from sqlalchemy.exc import IntegrityError
from datetime import timedelta 

from models import db, User, Todo
from forms import SignUp, LogIn, AddTodo

''' Begin boilerplate code '''

''' Begin Flask Login Functions '''
login_manager = LoginManager()
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

''' End Flask Login Functions '''

def create_app():
  app = Flask(__name__)
  app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
  app.config['SECRET_KEY'] = "MYSECRET"
  login_manager.init_app(app)
  db.init_app(app)
  return app

app = create_app()

app.app_context().push()
db.create_all(app=app)
''' End Boilerplate Code '''

@app.route('/', methods=['GET', 'POST'])
def index():
  form = LogIn()
  if form.validate_on_submit(): # respond to form submission
    data = request.form
    user = User.query.filter_by(username = data['username']).first()
    if user and user.check_password(data['password']): # check credentials
      flash('Logged in successfully.') # send message to next page
      login_user(user) # login the user
      return redirect(url_for('todos')) # redirect to main page if login successful
    else:
      flash('Invalid username or password') # send message to next page
      return redirect(url_for('index')) # redirect to login page if login unsuccessful
  return render_template('login.html', form=form)



@app.route('/signup', methods=['GET', 'POST'])
def signup():
  form = SignUp() # create form object
  if form.validate_on_submit():
    data = request.form # get data from form submission
    newuser = User(username=data['username'], email=data['email']) # create user object
    newuser.set_password(data['password']) # set password
    db.session.add(newuser) # save new user
    db.session.commit()
    flash('Account Created!')# send message
    return redirect(url_for('index'))# redirect to login page
  return render_template('signup.html', form=form) # pass form object to template



@app.route('/todos', methods=['GET', 'POST'])
@login_required
def todos():
  toggle_id = request.args.get('toggle')
  if toggle_id:
    todo = Todo.query.get(toggle_id) # retrieve todo
    if todo:
      todo.done = not todo.done # toggle the done state
      db.session.add(todo) # save the todo
      db.session.commit()
  todos = Todo.query.filter_by(userid=current_user.id).all()
  if todos is None:
      todos = []
  form = AddTodo()
  if form.validate_on_submit():
    data = request.form
    todo = Todo(text=data['text'], done=False, userid=current_user.id)
    db.session.add(todo)
    db.session.commit()
    flash('Todo Created!')
    return redirect(url_for('todos'))
  return render_template('todo.html', form=form, todos=todos)




@app.route('/editTodo/<id>', methods=['GET', 'POST'])
@login_required
def edit_todo(id):
  data = request.form
  if data : # if data exists a form submission occured
    todo = Todo.query.filter_by(userid=current_user.id, id=id).first() # query  todo
    todo.text = data['text'] # update text
    db.session.add(todo) # save todo
    db.session.commit()
    flash('Todo Updated!')
    return redirect(url_for('todos'))
  return render_template('edit.html', id=id) # pass id to template  

  
app.run(host='0.0.0.0', port=8080)