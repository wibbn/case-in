from werkzeug.security import generate_password_hash, check_password_hash
from application import db
from mongoengine import StringField, EmailField, BooleanField, ReferenceField, ListField
from flask_fs.mongo import ImageField
from application import storages


class User(db.Document):
    email = EmailField(required=True, unique=True)
    first_name = StringField(required=True)
    last_name = StringField()
    password_hash = StringField(required=True)
    avatar = ImageField(fs=storages["avatars"], max_size=200)
    is_active = BooleanField(default=True)
    is_admin = BooleanField(default=False)

    def __init__(self, *args, **kwargs):
        if "password" in kwargs.keys():
            password = kwargs.pop("password")
            super().__init__(*args, **kwargs)
            self.password = password
        else:
            super().__init__(*args, **kwargs)

    def update(self, *args, **kwargs):
        if "password" in kwargs.keys():
            password = kwargs.pop("password")
            self.update(password_hash=generate_password_hash(password))
        if kwargs:
            super().update(*args, **kwargs)

    @property
    def password(self):
        raise AttributeError("Error: Password is not readable attribute")

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)
