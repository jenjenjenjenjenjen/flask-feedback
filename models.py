
from builtins import classmethod
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

db = SQLAlchemy()

bcrypt = Bcrypt()

def connect_db(app):
    '''Connect to database'''

    db.app = app
    db.init_app(app)

class User(db.Model):
    '''Model for users'''

    __tablename__ = 'users'

    username = db.Column(db.VARCHAR(length=20), primary_key=True)
    password = db.Column(db.Text, nullable=False)
    email = db.Column(db.VARCHAR(length=50), nullable=False, unique=True)
    first_name = db.Column(db.VARCHAR(length=30), nullable=False)
    last_name = db.Column(db.VARCHAR(length=30), nullable=False)

    @classmethod
    def register(cls, username, password, email, first_name, last_name):
        '''Hash password for new user'''

        hashed = bcrypt.generate_password_hash(password)
        hashed_utf8 = hashed.decode("utf8")

        return cls(username=username, password=hashed_utf8, email=email, first_name=first_name, last_name=last_name)

    @classmethod 
    def authenticate(cls, username, password):
        '''Authenticate returning user'''

        u = User.query.filter_by(username=username).first()

        if u and bcrypt.check_password_hash(u.password, password):
            return u
        else:
            return False

class Feedback(db.Model):
    """Model for feedback"""

    __tablename__ = 'feedback'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.VARCHAR(length=100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    username = db.Column(db.Text, db.ForeignKey('users.username'))

    user = db.relationship('User', backref='feedback')