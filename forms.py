from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField
from wtforms.validators import DataRequired, Email, Length, email_validator

class LoginForm(FlaskForm):

    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[Length(min=6)])

class SignupForm(FlaskForm):

    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[Length(min=6)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    image = StringField('Profile Image')

class PostForm(FlaskForm):

    media = StringField('Post Content', validators=[DataRequired()])
    caption = StringField('Caption')
   

