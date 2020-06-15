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
    open_time=db.StringField()

    event = db.ReferenceField('sttapp.events.models.Event')
    is_back = db.BooleanField(default=False)

    meta = {'ordering': ['-created_at']}

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
        gender_dict = {display: 0 for field, display in Gender.get_choices(False)}
        for a in self.attendees:
            if not a.gender:
                continue
            gender_dict[a.gender] += 1
        return gender_dict

    @property
    def level_structure(self):
        level_dict = {field: 0 for field, display in Level.get_choices()}
        for a in self.attendees:
            if not getattr(a, 'level'):
                continue
            level_dict[getattr(a, 'level')] += 1
        return level_dict
    
    @property
    def difficulty(self):
        if self.days <= 3:
            return Difficulty.LEVEL_D
        if self.days <= 5:
            return Difficulty.LEVEL_C
        if self.days <= 8:
            return Difficulty.LEVEL_B
        else:
            return Difficulty.LEVEL_A

    def validate_for_publishing(self):
        required_fields = {
            "title": "隊伍名稱", 
            "start_date": "上山日期", 
            "days": "天數",
            "leader": "領隊", 
            "guide": "嚮導",          
            "supporter": "留守", 
            "buffer_days": "預備天數", 
            "attendees": "成員", 
            "return_plan": "撤退計畫",
            "approach_way": "交通方式", 
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
