from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from application import db
from mongoengine import StringField, ReferenceField, DateTimeField, FloatField, IntField
from flask_fs.mongo import ImageField
from application import storages


class MachineModel(db.Document):
    name=StringField(required=True)
    manufaturer=StringField(required=True)

class Machine(db.Document):
    name=StringField(required=True)
    model=ReferenceField(MachineModel, required=True)
    manufacture_date=DateTimeField(required=True)

class MachinePart(db.Document):
    name=StringField()
    model=ReferenceField(MachineModel, required=True)
    quantity=IntField()

class MachineMaintenance(db.Document):
    machine=ReferenceField(Machine, required=True)
    date=DateTimeField(required=True, default=datetime.utcnow)
    part=ReferenceField(MachinePart, required=True)

class MachineErrors(db.Document):
    machine=ReferenceField(Machine, required=True)
    error_type=StringField(required=True, choices=["error1", "error2", "error3", "error4", "error5"])
    date=DateTimeField(required=True, default=datetime.utcnow)

class MachineTelemetry(db.Document):
    machine=ReferenceField(Machine, required=True)
    date=DateTimeField(default=datetime.utcnow, required=True)
    voltage=FloatField()
    vibration=FloatField()
    pressure=FloatField()
    rotation=FloatField()

