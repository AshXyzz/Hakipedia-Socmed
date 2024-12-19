from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager, current_user

db = SQLAlchemy()
DB_NAME = "database.db" #change this to change the filename

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'asdfaskjdfgahet'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # Don't track database modifications
    app.config["SQLALCHEMY_DATABASE_URI"] = f'sqlite:///{DB_NAME}'
    db.init_app(app)

    @app.errorhandler(404) # error handler had to be in this file because it doesn't work in blueprint files for some reason beyond my understanding
    def not_found(e):
        return render_template('404.html', user=current_user)

    from .views import views # app creations from other python files i created
    from .auth import auth

    app.register_blueprint(views, url_prefix="/") # the url prefix could be useful for example a whole set of pages that start with website.com/prefix/specific-page
    app.register_blueprint(auth, url_prefix="/")

    from .models import User, Post

    create_database(app)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login_page'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id): 
        return User.query.get(int(id))

    return app

def create_database(app):
    if not path.exists("instance/" + DB_NAME):
        with app.app_context():
            db.create_all()
            print('CREATED DATABASE!')