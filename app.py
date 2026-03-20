import os
from flask import Flask
from flask_session import Session
from config import Config

from blueprints.upload import upload_bp
from blueprints.dashboard import dashboard_bp
from blueprints.view import view_bp
from blueprints.clean import clean_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Create required folders if they don't exist
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['SESSION_FILE_DIR'], exist_ok=True)

    # Init server-side session
    Session(app)

    # Register blueprints
    app.register_blueprint(upload_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(view_bp)
    app.register_blueprint(clean_bp)

    return app


app = create_app()

if __name__ == '__main__':
    app.run(debug=True)