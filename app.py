# Nicholas J Uhlhorn
# November 2025

from flask import Flask
import os
from extensions import db
from routes import main_bp

DB_DIR  = os.path.join(os.getcwd(), 'db_data')
DB_PATH = os.path.join(DB_DIR, 'database.db')

def create_app():
    app = Flask(__name__)
    basedir = os.path.abspath(os.path.dirname(__file__))
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + DB_PATH
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    app.register_blueprint(main_bp)

    import models

    return app

# Main guard (keep at EOF)
if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        db.create_all()

    app.run(host='0.0.0.0', port=5000)
