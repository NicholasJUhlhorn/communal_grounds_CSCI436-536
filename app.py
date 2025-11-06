# Nicholas J Uhlhorn
# November 2025

from flask import g, Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
import os

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(os.getcwd(), '/data/database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = 'sqlite:///' + os.path.join(os.getcwd(), '/data/database.db')
db = SQLAlchemy(app)

def init_db():
    with app.app_context():
        db.create_all()

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p?>"

# Main guard (keep at EOF)
if __name__ == '__main__':
    # Import DB models 
    from models import *
    init_db()

    app.run(host='0.0.0.0', port=5000)
