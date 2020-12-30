import mongoengine as me
from app import login
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin, me.Document):
    email = me.StringField(required=True)
    username = me.StringField(max_length=50)
    password_hash = me.StringField(max_length=128)

    def set_password(self, password): 
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<User {}>'.format(self.username)

@login.user_loader
def load_user(user_id):
    return User.objects(pk=user_id).first()
