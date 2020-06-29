import datetime

from sttapp.db import db
from sttapp.base.models import RecordModel
from sttapp.proposals.models import Itinerary
from sttapp.base.enums import Difficulty, EventType, EventStatus


class Event(RecordModel):
    
    proposal = db.ReferenceField('sttapp.proposals.models.Proposal', unique=True)
    img_url = db.URLField()
    real_title = db.StringField()
    real_itinerary_list = db.EmbeddedDocumentListField(Itinerary)
    real_days = db.IntField()
    feedback = db.StringField()
    gathering_time = db.DateTimeField()
    gathering_point = db.StringField()
    status = db.StringField(choices=EventStatus.get_choices(False), 
                            default=EventStatus.get_map()[EventStatus.NORM])

    meta = {'ordering': ['-created_at']}

    @property
    def gathering_time_str(self):
        return self.gathering_time.strftime("%Y/%m/%d %H:%M")

    @property
    def itinerary_same_check(self):
        if self.status == EventStatus.get_map()[EventStatus.BACK] and not self.real_itinerary_list:
            return True
        return False

    @property
    def title(self):
        return self.real_title or self.proposal.title
