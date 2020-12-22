from flaskblog.models import User
from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed,FileField
from flask_login import current_user
from wtforms import StringField,PasswordField,SubmitField
from wtforms.validators import DataRequired,Length,Email,EqualTo,ValidationError

class RegisterForm(FlaskForm):
    username =  StringField('Username',validators = [DataRequired(),Length(min=5,max=20)])
    email = StringField('Email', validators = [DataRequired(),Email()])
    password = PasswordField('Password', validators = [DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators = [DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self,username):
        user = User.query.filter_by(username = username.data).first()
        if user:
            raise ValidationError("This Username is already taken")
    
    def validate_email(self,email):
        user = User.query.filter_by(email = email.data).first()
        if user:
            raise ValidationError("This Email is already taken")


class LoginForm(FlaskForm):
    email = StringField('Email', validators = [DataRequired(),Email()])
    password = PasswordField('Password', validators = [DataRequired()])
    submit = SubmitField('Login')

    def validate_email(self,email):
        user = User.query.filter_by(email =  email.data).first()
        if user  == None:
            raise ValidationError('User with this email does not exist')

class PostForm(FlaskForm):
    title = StringField('Title', validators = [DataRequired()])
    content = StringField('Content', validators = [DataRequired()])
    submit = SubmitField('Post')

class AccountForm(FlaskForm):
    username =  StringField('Username',validators = [DataRequired(),Length(min=5,max=20)])
    email = StringField('Email', validators = [DataRequired(),Email()])
    picture = FileField('Update Profile Picture', validators = [FileAllowed(['jpg','png'])])
    submit = SubmitField('Update')

    def validate_username(self,username):
        if username.data != current_user.username:
            user = User.query.filter_by(username = username.data).first()
            if user:
                raise ValidationError("This Username is already taken")

    def validate_email(self,email):
        if email.data != current_user.email:
            user = User.query.filter_by(email = email.data).first()
            if user:
                raise ValidationError("This Email is already taken")

class ChangePasswordForm(FlaskForm):
    current_password = PasswordField('Current Password', validators = [DataRequired()])
    new_password = PasswordField('New Password', validators = [DataRequired()])
    new_password_confirm = PasswordField('Confirm New Password', validators = [DataRequired(),EqualTo('new_password')])
    submit = SubmitField('Update Password')

class PasswordResetToken(FlaskForm):
    email = StringField('Email', validators = [DataRequired(),Email()])
    submit = SubmitField('Send Token')

    def validate_email(self,email):
        user = User.query.filter_by(email =  email.data).first()
        if user  == None:
            raise ValidationError('User with this email does not exist')


class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password',validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(),EqualTo('password')])
    submit = SubmitField('Reset Password')




