import datetime

from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

from sttapp.db import db
from sttapp.users.enums import Level
from .enums import Difficulty, EventType


class Itinerary(db.EmbeddedDocument):

    day_number = db.IntField()
    content = db.StringField()
    water_info = db.StringField()
    communication_info = db.StringField()

    meta = {'ordering': ['-day_number']}


class Proposal(db.Document):

    # basic info
    title = db.StringField()
    difficulty = db.StringField(choices=Difficulty.get_choices())
    start_date = db.DateTimeField()
    end_date = db.DateTimeField()
    event_type = db.StringField(choices=EventType.get_choices())
    days = db.IntField(default=1)
    leader = db.ReferenceField('Member')
    guide = db.ReferenceField('Member')
    itinerary_list = db.EmbeddedDocumentListField(Itinerary)
    supporter = db.ReferenceField('Member')
    return_plan = db.StringField()
    buffer_days = db.IntField(default=1)
    approach_way = db.StringField()
    radio = db.StringField()
    satellite_telephone = db.StringField()
    gathering_point = db.StringField()
    gathering_time = db.DateTimeField()

    members = db.ListField(db.ReferenceField('Member'))

    published_at = db.DateTimeField()
    created_at = db.DateTimeField(default=datetime.datetime.utcnow)
    created_by = db.ReferenceField('sttapp.users.models.SttUser')
    updated_at = db.DateTimeField()

    meta = {'ordering': ['-start_date']}


class Member(db.Document):

    # 基本資料
    name = db.StringField()
    security_number = db.StringField()
    birthday = db.DateTimeField()
    cellphone_number = db.StringField()
    gender = db.StringField()

    # 進階資料
    email = db.EmailField()
    drug_allergy = db.StringField(default="NKDA")
    home_address = db.StringField()
    blood_type = db.StringField()
    level = db.StringField(choices=Level.get_choices())  # 新生、隊員、幹部等

    # 學校資訊
    student_id = db.StringField()
    department_and_grade = db.StringField()  # ex: 水利四 / ob / 物理所 / 校外

    # 最高資歷
    highest_difficulty = db.StringField(choices=Difficulty.get_choices())  # 級數
    highest_difficulty_experience = db.StringField()  # 手動輸入出隊資歷，ex: 哈崙鐵道

    # 緊急聯絡人
    emargency_contact = db.StringField()
    emargency_contact_phone = db.StringField()
    emargency_contact_relationship = db.StringField()

    # 系統紀錄
    created_by = db.ReferenceField('SttUser')
    created_at = db.DateTimeField(default=datetime.datetime.utcnow)
    updated_by = db.ReferenceField('SttUser')
    updated_at = db.DateTimeField()
    # events_history =
