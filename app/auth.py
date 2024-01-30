# app.py

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from flask_login import login_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from .models import User

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember = True if request.form.get('remember') else False

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            login_user(user, remember=remember)
            return redirect(url_for('main.profile'))
        else:
            flash('Please check your login details and try again.')
            return redirect(url_for('auth.login'))

    return render_template('login.html')

@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form.get('email')
        name = request.form.get('name')
        password = request.form.get('password')

        existing_user = User.query.filter_by(email=email).first()

        if existing_user:
            flash('Username already taken. Please choose a different one.')
            return redirect(url_for('auth.signup'))

        # Hash the password before storing it in the database
        hashed_password = generate_password_hash(password, method='pbkdf2:sha1')

        # Create a new user
        new_user = User(email=email, password=hashed_password, name=name)

        # Add the new user to the database
        db.session.add(new_user)
        db.session.commit()

        flash('Account created successfully! You can now log in.')
        return redirect(url_for('auth.login'))

    return render_template('signup.html')

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))


