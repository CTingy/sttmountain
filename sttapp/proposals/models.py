import datetime

from sttapp.db import db
from .enums import Difficulty, EventType


class Itinerary(db.EmbeddedDocument):

    day_number = db.IntField()
    content = db.StringField()
    water_info = db.StringField()
    communication_info = db.StringField()

    meta = {'ordering': ['-day_number']}


class BaseEvent(db.Document):
    title = db.StringField()
    difficulty = db.StringField(choices=Difficulty.get_choices())
    start_date = db.DateTimeField()
    end_date = db.DateTimeField()
    event_type = db.StringField(choices=EventType.get_choices())
    days = db.IntField(default=1)
    leader = db.ReferenceField('sttapp.members.models.Member')
    guide = db.ReferenceField('sttapp.members.models.Member')
    itinerary_list = db.EmbeddedDocumentListField(Itinerary)
    supporter = db.ReferenceField('sttapp.members.models.Member')
    return_plan = db.StringField()
    buffer_days = db.IntField(default=1)
    approach_way = db.StringField()
    radio = db.StringField()
    satellite_telephone = db.StringField()
    gathering_point = db.StringField()
    gathering_time = db.DateTimeField()

    members = db.ListField(db.ReferenceField('sttapp.members.models.Member'))

    created_at = db.DateTimeField(default=datetime.datetime.utcnow)
    created_by = db.ReferenceField('sttapp.users.models.SttUser')
    updated_at = db.DateTimeField()

    meta = {'abstract': True, }


class Proposal(BaseEvent):

    gathering_point = db.StringField()
    gathering_time = db.DateTimeField()

    published_at = db.DateTimeField()

    meta = {'ordering': ['-start_date']}
