import datetime

from sttapp.db import db
from sttapp.base.models import RecordModel
from sttapp.proposals.models import Itinerary
from sttapp.base.enums import Difficulty, EventType, EventStatus


class Event(RecordModel):
    
    proposal = db.ReferenceField('sttapp.proposals.models.Proposal', unique=True)
    img_url = db.URLField()
    real_itinerary_list = db.EmbeddedDocumentListField(Itinerary)
    feedback = db.StringField()
    gathering_time = db.DateTimeField()
    gathering_point = db.StringField()
    status = db.StringField(choices=EventStatus.get_choices(False), default="NORM")

    meta = {'ordering': ['-created_at']}
