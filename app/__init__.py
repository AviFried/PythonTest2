# __init__.py

from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy

# init SQLAlchemy so we can use it later in our models
db = SQLAlchemy()

def create_app():
    app = Flask(__name__)

    app.config['SECRET_KEY'] = '9OLWxND4o83j4K4iuopO'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'

    db.init_app(app)

    login_manager = LoginManager(app)
    login_manager.login_view = 'login'

    from app.models import User

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, user_id)

    # blueprint for non-auth parts of app
    from app.main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    # blueprint for non-auth parts of app
    from app.auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)


    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=8000, debug=True)
