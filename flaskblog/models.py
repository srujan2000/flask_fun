from datetime import datetime
from flask import app
from flaskblog import db,login_manager
from flask_login import UserMixin
from flask import current_app
from itsdangerous import Serializer, TimedJSONWebSignatureSerializer as serializer

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model,UserMixin):
    id = db.Column(db.Integer , primary_key = True)
    username = db.Column(db.String(20),unique = True, nullable = False)
    email = db.Column(db.String(30),unique = True, nullable = False)
    password = db.Column(db.String(20), nullable = False)
    image = db.Column(db.String(20),nullable = False ,default = 'def.jpg')
    posts = db.relationship('Post',backref='author',lazy = True)

    def get_token(self,expires_sec = 900):
        s = serializer(current_app.config['SECRET_KEY'],expires_sec)
        return s.dumps({'user_id': self.id}).decode('utf-8')

    @staticmethod
    def check_token(token):
        s = serializer(current_app.config['SECRET_KEY'])
        try:
            user = s.loads(token)['user_id']
        except:
            return None
        return User.query.get(user)



    def __repr__(self):
        return f"User('{self.id}','{self.email}','{self.image}')"

class Post(db.Model):
    id = db.Column(db.Integer , primary_key = True)
    title = db.Column(db.String(100), nullable = False)
    date = db.Column(db.DateTime,default = datetime.utcnow)
    content = db.Column(db.Text, nullable = False)
    user_id = db.Column(db.Integer,db.ForeignKey('user.id'),nullable = False)

    def __repr__(self):
        return f"Post('{self.id}','{self.title}','{self.date}')"