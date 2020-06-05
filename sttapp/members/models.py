import datetime

from sttapp.db import db
from sttapp.users.enums import Level
from sttapp.proposals.enums import Difficulty


class Member(db.Document):

    # 基本資料
    name = db.StringField()
    username = db.StringField()
    security_number = db.StringField(unique=True)
    birthday = db.DateTimeField()
    cellphone_number = db.StringField()
    gender = db.StringField()

    # 進階資料
    # email = db.EmailField()
    drug_allergy = db.StringField(default="NKDA")
    # home_address = db.StringField()
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
    emargency_contact_relationship = db.StringField()  # ex: 父子、母子

    # 系統紀錄
    created_by = db.ReferenceField('sttapp.users.models.SttUser')
    created_at = db.DateTimeField(default=datetime.datetime.utcnow)
    updated_by = db.ReferenceField('sttapp.users.models.SttUser')
    updated_at = db.DateTimeField()
    # events_history =

    @property
    def display_name(self):
        if self.username:
            return username
        else:
            return self.name

    @property
    def selected_name(self):
        return "{}|{}".format(self.name, self.security_number)
