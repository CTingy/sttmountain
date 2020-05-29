import datetime

from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

from sttapp.db import db
from sttapp.users.models import SttUser


class Itinerary(db.EmbeddedDocument):

    content = db.StringField()
    water_info = db.StringField()
    communication_info = db.StringField()


class Proposal(db.Document):

    # basic info
    title = db.StringField()
    start_date = db.DateTimeField()
    end_date = db.DateTimeField()
    leader = db.ReferenceField('sttapp.users.models.SttUser')
    guide = db.ReferenceField('sttapp.users.models.SttUser')
    itinerary = db.EmbeddedDocumentField(Itinerary)
    supporter = db.ReferenceField('sttapp.users.models.SttUser')
    return_plan = db.StringField()
    buffer_days = db.IntField(default=1)
    approach_way = db.StringField()
    radio = db.StringField()
    satellite_telephone = db.StringField()
    gathering_at = db.StringField()

    # reference model為已經建立網站帳號的人
    members_stt = db.ListField(ReferenceField('sttapp.users.models.SttUser'))
    
    # reference model為尚未建立網站帳號的人，可能是新生、校外、或是單純沒建帳號的人
    members_temp = db.ListField(ReferenceField('sttapp.users.models.TempUser'))

    has_published = db.BooleanField(default=False)
    created_at = db.DateTimeField()
    updated_at = db.DateTimeField()

    # insurance_start_at = db.DateTimeField()
    # insurance_start_at = db.DateTimeField()


class Event(db.Document):
    pass

