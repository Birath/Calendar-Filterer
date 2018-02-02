from flask import Flask


def create_app():
    app = Flask(__name__)
    app.config.from_object('config.DevelopmentConfig')

    from app.blueprints import calendar_filterer
    from app.blueprints import oauth
    app.register_blueprint(calendar_filterer.bp)
    app.register_blueprint(oauth.bp)

    return app

