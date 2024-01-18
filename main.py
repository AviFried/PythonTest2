import random
from flask import Flask, render_template, request, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
app = Flask(__name__)


@app.route('/')
def index():
    num=random.randint(1,100)

    return render_template('index.html',num=num)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)