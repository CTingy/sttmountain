import datetime

from sttapp.db import db
from sttapp.base.models import RecordModel
from .enums import Difficulty, EventType


class Itinerary(db.EmbeddedDocument):

    day_number = db.IntField()
    content = db.StringField()
    water_info = db.StringField()
    communication_info = db.StringField()

    meta = {'ordering': ['-day_number']}


class Proposal(RecordModel):
    title = db.StringField()
    difficulty = db.StringField(choices=Difficulty.get_choices())
    start_date = db.DateTimeField()
    end_date = db.DateTimeField()
    event_type = db.StringField(choices=EventType.get_choices())
    days = db.IntField(default=1)
    leader = db.ReferenceField('sttapp.members.models.Member')
    guide = db.ReferenceField('sttapp.members.models.Member')
    itinerary_list = db.EmbeddedDocumentListField(Itinerary)
    supporter = db.StringField()
    return_plan = db.StringField()
    buffer_days = db.IntField(default=1)
    approach_way = db.StringField()
    radio = db.StringField()
    satellite_telephone = db.StringField()
    attendees = db.ListField(db.ReferenceField('sttapp.members.models.Member'))
    gathering_point = db.StringField()
    gathering_time = db.DateTimeField()

    published_at = db.DateTimeField()
    is_back = db.BooleanField(default=False)

    meta = {'ordering': ['-start_date']}

    @property
    def start_date_str(self):
        return self.start_date.strftime("%Y/%m/%d")

    @property
    def end_date_str(self):
        return self.end_date.strftime("%Y/%m/%d")

    @property
    def gathering_time_str(self):
        return self._dt_to_str(self.gathering_time)

    def validate_for_publishing(self):
        required_fields = (
            "title", "start_date", "days", "leader", "guide", "supporter",
            "return_plan", "buffer_days", "approach_way", "radio", 
            "satellite_telephone", "attendees", "gathering_point", 
            "gathering_time"
        )
        for field in required_fields:
            if not getattr(self, field):
                return False
        return True
