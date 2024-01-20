# init.py
from flask import Flask, render_template, flash, redirect, url_for, request
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import json
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import platform
import os
app = Flask(__name__)
app.config['SECRET_KEY'] = '9OLWxND4o83j4K4iuopO'

if platform.system() == 'Linux':
  mongoUser = os.environ['mongoUser']
  mongoPass = os.environ['mongoPassword']
else:
  with open("passwords.json", "rb") as f:
      passwords = json.load(f)
      mongoUser = passwords['mongoUser']
      mongoPass = passwords['mongoPassword']
uri = "mongodb+srv://"+mongoUser+":"+mongoPass+"@cluster0.udbes1y.mongodb.net/?retryWrites=true&w=majority"

# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))
db = client.totalData
users_collection = db.users

login_manager = LoginManager(app)
login_manager.login_view = 'login'

class User(UserMixin):
    def __init__(self, username, password, name):
        self.username = username
        self.password = password
        self.name = name

    def get_id(self):
        return self.username


@login_manager.user_loader
def load_user(username):
    user_data = users_collection.find_one({'username': username})
    if user_data:
        return User(username=user_data['username'], password=user_data['password'], name=user_data['name'])
    return None



@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('email')
        password = request.form.get('password')
        remember = True if request.form.get('remember') else False

        user_data = users_collection.find_one({'username': username})

        if user_data and check_password_hash(user_data['password'], password):
            user = User(username=user_data['username'], password=user_data['password'], name=user_data['name'])
            login_user(user, remember=remember)
            return redirect(url_for('main.profile'))
        else:
            flash('Please check your login details and try again.')
            return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('email')
        name = request.form.get('name')
        password = request.form.get('password')

        existing_user = users_collection.find_one({'username': username})

        if existing_user:
            flash('Username already taken. Please choose a different one.')
            return redirect(url_for('signup'))

        # Hash the password before storing it in the database
        hashed_password = generate_password_hash(password, method='pbkdf2:sha1')

        # Create a new user document
        new_user = {'username': username, 'password': hashed_password}

        # Insert the new user into the 'users' collection in MongoDB
        users_collection.insert_one(new_user)

        flash('Account created successfully! You can now log in.')
        return redirect(url_for('login'))

    return render_template('signup.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))

# blueprint for non-auth parts of app
from main import main as main_blueprint
app.register_blueprint(main_blueprint)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
