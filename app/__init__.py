from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from app.config import DevelopmentConfig

db = SQLAlchemy()


def create_app(config_class=DevelopmentConfig):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config_class)

    db.init_app(app)
    with app.app_context():
        from app import views
        db.create_all()

    app.register_blueprint(views.bp)

    return app
