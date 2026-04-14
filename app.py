import os
from flask import Flask
from config import Config
from extensions import db, jwt

from blueprints.auth import auth_bp
from blueprints.upload import upload_bp
from blueprints.dashboard import dashboard_bp
from blueprints.view import view_bp
from blueprints.clean import clean_bp
from blueprints.transform import transform_bp
from blueprints.visualize import visualize_bp
from blueprints.report import report_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    db.init_app(app)
    jwt.init_app(app)

    app.register_blueprint(auth_bp)
    app.register_blueprint(upload_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(view_bp)
    app.register_blueprint(clean_bp)
    app.register_blueprint(transform_bp)
    app.register_blueprint(visualize_bp)
    app.register_blueprint(report_bp)

    # with app.app_context():
    #     db.create_all()

    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)