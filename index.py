
from config import app, db, bcrypt, User, Note, login_manager
from flask import render_template, request, redirect, url_for, render_template_string
from flask_login import current_user, logout_user, login_required, login_user, UserMixin
import forms
import sys
sys.path.append('backend/CRUD')
from CRUD import create
from CRUD import update
from CRUD import delete
from CRUD import actions


@app.route('/', methods = ['GET','POST'])
@app.route('/index', methods = ['GET','POST'])
def hello_world():

    # if there is a register request
    if forms.RegistrationForm().validate_on_submit():
        create.user(forms.RegistrationForm())
        actions.login(forms.RegistrationForm().email.data,
                                  forms.RegistrationForm().password.data)
        return redirect(url_for('hello_world'))

    # If there is a login request
    if forms.LoginForm().validate_on_submit():
        actions.login(forms.RegistrationForm().email.data,
                                  forms.RegistrationForm().password.data)
        return redirect(url_for('hello_world'))

    # If there is a request to logout the current user
    if (request.method == "POST") & (request.form.get('post_header') == 'log out'):
        logout_user()
        return redirect(url_for('hello_world'))

    # if there is a request to create or update a note
    if forms.NoteForm().validate_on_submit():
        if request.form.get('post_header') == 'update note':
            update.note(forms.NoteForm())
        else:
            create.note(forms.NoteForm())
        return redirect(url_for('hello_world'))

    # If there is a request to delete a note
    if (request.method == "POST") & (request.form.get('post_header') == 'delete note'):
        delete.note(request.form.get('note_to_delete'))
        return redirect(url_for('hello_world'))

    # Getting all needed database objects
    if current_user.is_authenticated:
        print("Logged In")
        notes = Note.query.filter_by(username = current_user.username).all()
    else:
        print("Not Logged in")
        notes = []

    return render_template('index.html',
                           notes = notes,
                           login_form = forms.LoginForm(),
                           register_form = forms.RegistrationForm(),
                           csrf_form = forms.csrf_form(),
                           note_form = forms.NoteForm())


class User(UserMixin):
    def __init__(self, email, password):
        self.id = email
        self.password = password



@login_manager.user_loader
def user_loader(id):
    return users.get(id)

users = {"leafstorm": User("leafstorm", "secret")}
@app.get("/login")
def loginpage():
    return """<form method=post>
      Email: <input name="email"><br>
      Password: <input name="password" type=password><br>
      <button>Log In</button>
    </form>"""

@app.post("/login")
def login():
    user = users.get(request.form["email"])

    if user is None or user.password != request.form["password"]:
        return redirect(url_for("login"))

    login_user(user)
    return redirect(url_for("protected"))

@app.route("/protected")
@login_required
def protected():
    return render_template_string(
        "Logged in as: {{ user.id }}",
        user=current_user
    )

@app.route("/logout")
def logout():
    logout_user()
    return "Logged out"