from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy()
migrate = Migrate()


def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object('config.DevelopmentConfig')
    # Grabs the secret key
    app.config.from_pyfile('config.py', silent=True)
    db.init_app(app)
    migrate.init_app(app, db)
    from app.blueprints import calendar_filterer
    from app.blueprints import oauth
    from app import models
    app.register_blueprint(calendar_filterer.bp)
    app.register_blueprint(oauth.bp)

    return app

