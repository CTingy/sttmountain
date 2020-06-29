import datetime

from sttapp.db import db
from sttapp.base.models import RecordModel
from sttapp.base.enums import Level, Gender, Difficulty, Group
from sttapp.base.utils import get_local_dt


CHOICES = {
    "group": Group.get_choices(), 
    "difficulty": Difficulty.get_choices(),
    "level": Level.get_choices(),
}


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
    level = db.StringField(choices=CHOICES["level"])  # 新生、隊員、幹部等
    group = db.StringField(choices=CHOICES["group"])

    # 學校資訊
    student_id = db.StringField()
    department_and_grade = db.StringField()  # ex: 水利四 / ob / 物理所 / 校外

    # 最高資歷
    highest_difficulty = db.StringField(choices=CHOICES["difficulty"])  # 級數
    highest_difficulty_experience = db.StringField()  # 手動輸入出隊資歷，ex: 哈崙鐵道

    # 緊急聯絡人
    emergency_contact = db.StringField()
    emergency_contact_phone = db.StringField()
    emergency_contact_relationship = db.StringField()  # ex: 父子、母子

    user_id = db.ObjectIdField()
    event_ids = db.ListField(db.ObjectIdField(), default=list)

    @property
    def display_name(self):
        return self.nickname or self.name

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
        return self.birthday.strftime("%Y/%m/%d")

    @property
    def is_adult(self):
        today = get_local_dt(datetime.datetime.utcnow()).date()
        return today.replace(year=today.year-20) >= self.birthday.date()

    @property
    def attendee_display(self):
        return "{}({}{})".format(
            self.display_name,
            self.get_level_display()[0] if self.level else "",
            "、{}".format(self.get_group_display()[-1]) if self.group else ""
        )
