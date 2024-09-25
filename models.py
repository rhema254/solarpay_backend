""" To avoid relative imports, create a new file exts.py and import sqlalchemy class there and 
    create a db instance. Do not specify the db variable so that it becomes a global variable
    so that it can be accessed from other parts in the code.
"""

from exts import db
import datetime

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=False, autoincrement=True, unique=True)
    phone_number = db.Column(db.String(10), primary_key=True)
    name = db.Column(db.String(50))
    county = db.Column(db.String(19))
    town = db.Column(db.String(25))
    created_at = db.Column(db.DateTime, default=db.func.now())

    def __repr__(self):
        return f'<User {self.phone_number}>'
    

    