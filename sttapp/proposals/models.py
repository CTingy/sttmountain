import datetime

from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

from sttapp.db import db


class Itinerary(db.EmbeddedDocument):

    day_number = db.IntField()
    content = db.StringField()
    water_info = db.StringField()
    communication_info = db.StringField()

    meta = {'ordering': ['-day_number']}


class Proposal(db.Document):

    # basic info
    title = db.StringField()
    start_date = db.DateTimeField()
    end_date = db.DateTimeField()
    leader = db.ReferenceField('sttapp.users.models.SttUser')
    guide = db.ReferenceField('sttapp.users.models.SttUser')
    itinerary_list = db.EmbeddedDocumentListField(Itinerary)
    supporter = db.ReferenceField('sttapp.users.models.SttUser')
    return_plan = db.StringField()
    buffer_days = db.IntField(default=1)
    approach_way = db.StringField()
    radio = db.StringField()
    satellite_telephone = db.StringField()
    gathering_point = db.StringField()
    gathering_time = db.DateTimeField()

    # reference model為已經建立網站帳號的人
    members_stt = db.ListField(
        db.ReferenceField('sttapp.users.models.SttUser'))

    # reference model為尚未建立網站帳號的人，可能是新生、校外、或是單純沒建帳號的人
    members_temp = db.ListField(
        db.ReferenceField('sttapp.users.models.TempUser'))

    published_at = db.DateTimeField()
    created_at = db.DateTimeField(default=datetime.datetime.utcnow)
    created_by = db.ReferenceField('sttapp.users.models.SttUser')
    updated_at = db.DateTimeField()

    # insurance_start_at = db.DateTimeField()
    # insurance_start_at = db.DateTimeField()

    meta = {'ordering': ['-start_date']}
