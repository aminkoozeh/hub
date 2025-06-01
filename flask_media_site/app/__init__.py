from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import Config
import os

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'main.login'
login_manager.login_message = 'برای دسترسی به این صفحه باید وارد شوید.'

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)

    from app.routes import main
    app.register_blueprint(main)

    # ساخت پوشه uploads اگر وجود نداشت
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    return app
