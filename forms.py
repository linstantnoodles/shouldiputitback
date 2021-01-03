from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class BusinessForm(FlaskForm):
    name = StringField('name')

class UserForm(FlaskForm):
    email = StringField('email')
    name = StringField('name')

class FieldForm(FlaskForm):
    name = StringField('name', validators=[DataRequired()])
    # options, string, numeric - these should be mapped to mongo types
    type = String('type', validators=[DataRequired()])

class QuestionForm(FlaskForm):
    label = StringField('name')
    type = StringField('type')
    field = StringField('field')
    required = BooleanField('type')
    rank = IntegerField("rank")
