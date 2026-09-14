from flask import Flask
from .database import db
from .routes import notes_bp


def create_app(config=None):
    app = Flask(__name__)

    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///notes.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SECRET_KEY"] = "dev-secret-key-change-in-production"

    if config:
        app.config.update(config)

    db.init_app(app)

    app.register_blueprint(notes_bp, url_prefix="/api")

    with app.app_context():
        db.create_all()

    return app
