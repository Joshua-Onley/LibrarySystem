import os
import secrets

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] =  secrets.token_bytes(16)
login = LoginManager(app)
login.login_view = 'login'

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'data', 'data.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


from app import views
from app.models import *

@app.shell_context_processor
def make_shell_context():
    return dict(db=db, User=User, Student=Student, Loan=Loan, Device=Device, datetime=datetime, LoginManager=LoginManager,
                Book=Book, BookLoan=BookLoan, Author=Author)
