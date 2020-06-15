import datetime

from sttapp.db import db
from sttapp.base.models import RecordModel
from sttapp.base.enums import Level, Gender, Difficulty, Group


class Member(RecordModel):

    # 基本資料
    name = db.StringField()
    nickname = db.StringField()
    security_number = db.StringField(unique=True)
    birthday = db.DateTimeField()
    cellphone_number = db.StringField()

    # 進階資料
    # email = db.EmailField()
    drug_allergy = db.StringField(default="NKDA")
    # home_address = db.StringField()
    blood_type = db.StringField()
    level = db.StringField(choices=Level.get_choices())  # 新生、隊員、幹部等
    group = db.StringField(choices=Group.get_choices())

    # 學校資訊
    student_id = db.StringField()
    department_and_grade = db.StringField()  # ex: 水利四 / ob / 物理所 / 校外

    # 最高資歷
    highest_difficulty = db.StringField(choices=Difficulty.get_choices())  # 級數
    highest_difficulty_experience = db.StringField()  # 手動輸入出隊資歷，ex: 哈崙鐵道

    # 緊急聯絡人
    emergency_contact = db.StringField()
    emergency_contact_phone = db.StringField()
    emergency_contact_relationship = db.StringField()  # ex: 父子、母子

    @property
    def display_name(self):
        if self.nickname:
            return nickname
        else:
            return self.name

    @property
    def selected_name(self):
        return "{}|{}".format(self.name, self.security_number)

    @property
    def gender(self):
        if self.security_number[1] == "1":
            return Gender.MALE
        elif self.security_number[1] == "2":
            return Gender.FEMALE
        else:
            return ""
    
    @property
    def birthday_str(self):
        if not self.birthday:
            return ""
        if type(self.birthday) == datetime.datetime:
            return self.birthday.strftime("%Y/%m/%d")
        # not save to DB yet, return the birthday directly
        return str(self.birthday)

    @property
    def is_adult(self):
        today = (datetime.datetime.utcnow() + datetime.timedelta(hours=8)).date()
        return today.replace(year=today.year-20) >= self.birthday.date()
