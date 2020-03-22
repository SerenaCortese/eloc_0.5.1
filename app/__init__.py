from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_uploads import configure_uploads, UploadSet, IMAGES

from config import config  # it is a dictionary config_mode_string:config_function

db = SQLAlchemy()

login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'auth.login'

images = UploadSet('images', IMAGES)


def create_app(config_name):# the argument is the config_mode_string

    app = Flask(__name__)

    app.config.from_object(config[config_name])

    configure_uploads(app, images)

    db.init_app(app)
    with app.app_context():
        db.create_all()

    login_manager.init_app(app)

    #BLUEPRINTS
    from main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')

    from .errors import err as err_blueprint
    app.register_blueprint(err_blueprint)

    from .users_bp import users_bp as user_blueprint
    app.register_blueprint(user_blueprint)
    #############

    return app

