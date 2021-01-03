from mongoengine import StringField, BooleanField, IntField, Document, DynamicDocument, FloatField
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

# In memory objects
class Business:
    def __init__(self, name):
        self.name = name

class User:
    def __init__(self, email, name, type):
        self.email = email
        self.name = name
        self.type = type

class Field:
    def __init__(self, name, type):
        self.name = name
        self.type = type

class Item:
    def __init__(self):
        pass

class Form:
    def __init__(self, type):
        self.type = type

    @property
    def questions(self):
        return [
             Question(label="Title", type="date", field="date_purchased"),
             Question(label="Cost", type="money", field="cost"),
             Question(label="Category", type="text", field="category"),
             Question(label="Brand", type="text", field="brand"),
             Question(label="Size", type="text", field="size"),
             Question(label="Style #", type="text", field="style_number"),
             Question(label="RN #", type="text", field="rn_number"),
             Question(label="Fabric", type="text", field="fabric"),
             Question(label="Care Instructions", type="text", field="care_instructions"),
             Question(label="Quantity", type="integer", field="quantity"),
             Question(label="Photos", type="textarea", field="photo_sources"),
             Question(label="Comps", type="textarea", field="comp_sources"),
             Question(label="Original Price", type="money", field="original_price"),
             Question(label="Description", type="textarea", field="description")
        ]

class Question:
    def __init__(self, label=None, type=None, field=None, required=False, rank=None):
        self.label = label
        self.type = type
        self.field = field
        self.required = required
        self.rank = rank

class BusinessRepository:
    def __init__(self):
        self.records = {}
        self.id = 1

    def create(self, name):
        obj = Business(name)
        self.records[self.id] = obj
        self.id += 1
        return obj

    def find_by_id(self, id):
        return self.records[id]

class FormRepository:
    def __init__(self):
        self.records = {}
        self.id = 1

    def create(self, name):
        pass

    def find_by_type(self, business_id, form_type):
        return Form("item");

class FieldRepository:
    def __init__(self):
        self.records = {}
        self.id = 1

    def create(self, name, type):
        x = Field(name, type)
        self.records[self.id] = x
        self.id += 1
        return x

class User(Document):
    email = StringField(required=True)
    username = StringField(max_length=50)
    password_hash = StringField(max_length=128)

    def set_password(self, password): 
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<User {}>'.format(self.username)

# class Business(Document):
#     name = StringField(required=True)

# class Item(DynamicDocument):
#     name = StringField(required=True)
#     quantity = IntField(required=True)
#     cost = FloatField(required=False)
# # embedded?
# class Field(Document):
#     name = StringField('name')
#     # options, string, numeric - these should be mapped to mongo types
#     type = StringField('type') 

# class Form(Document):
#     pass

# class Question(Document):
#     label = StringField('name')
#     q_type = StringField('type')
#     field = StringField('field')
#     required = BooleanField('type')
#     rank = IntField("rank")

# when rendering questions, you need to visit field to know what validation to serve. If it's a numeric field, show a numeric form
