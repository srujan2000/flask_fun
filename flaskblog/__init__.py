import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail

app = Flask(__name__)


app.config['SECRET_KEY'] = 'aewuuhwu112ii313'
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db = SQLAlchemy(app)
bycrpt = Bcrypt(app)
login_manager = LoginManager(app)

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = 'srujanreddy168@gmail.com'
app.config['MAIL_PASSWORD'] = 'ugxqczucgycfzzur'
mail = Mail(app)

from flaskblog import routes

