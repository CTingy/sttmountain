import datetime

from sttapp.db import db
from sttapp.base.models import RecordModel
from sttapp.base.enums import Difficulty, EventType, Gender, Level


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
    has_d0 = db.BooleanField(default=False)
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

    @property
    def total_number(self):
        return len(self.attendees)
    
    @property
    def gender_structure(self):
        gender_dict = {field: 0 for field, display in Gender.get_choices()}
        for a in self.attendees:
            if not getattr(a, 'gender'):
                continue
            gender_dict[getattr(a, 'gender')] += 1
        return gender_dict       

    @property
    def level_structure(self):
        level_dict = {field: 0 for field, display in Level.get_choices()}
        for a in self.attendees:
            if not getattr(a, 'level'):
                continue
            level_dict[getattr(a, 'level')] += 1
        return level_dict 

    def validate_for_publishing(self):
        required_fields = {
            "title": "隊伍名稱", 
            "start_date": "上山日期", 
            "days": "天數",
            "leader": "領隊", 
            "guide": "嚮導",          
            "supporter": "留守", 
            "buffer_days": "預備天數", 
            "gathering_time": "集合時間",
            "attendees": "成員", 
            "gathering_point": "集合地點",
            # "return_plan": "",  
            # "approach_way": "", 
        }
        failed_fields = []
        for field, name in required_fields.items():
            if not getattr(self, field):
                failed_fields.append(name)
        
        failed_itinerary = []
        for itinerary in self.itinerary_list:
            if not itinerary.content:
                failed_itinerary.append("D{}".format(itinerary.day_number))
        return failed_fields, failed_itinerary
