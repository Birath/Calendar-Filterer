from flask import Flask


def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object('config.DevelopmentConfig')
    app.config.from_pyfile('config.py', silent=True)
    from app.blueprints import calendar_filterer
    from app.blueprints import oauth
    app.register_blueprint(calendar_filterer.bp)
    app.register_blueprint(oauth.bp)

    return app

