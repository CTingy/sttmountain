import datetime

from werkzeug.security import generate_password_hash, check_password_hash

from sttapp.db import db
from .enums import Group, Position, SttDepartment


class MemberInfo(db.EmbeddedDocument):

    # 進階資料
    security_number = db.StringField(require=True, unique=True)
    gender = db.StringField(require=True)
    drug_allergy = db.StringField(require=True, default="NA")

    # 學校資訊
    student_id = db.StringField()
    department_and_grade = db.StringField()  # ex: 水利四 / ob / 物理所 / 校外

    # 最高資歷
    highest_level = db.StringField()  # 級數（A, B, C, D）
    highest_level_experience = db.StringField()  # 手動輸入出隊資歷，ex: 哈崙鐵道

    # 緊急聯絡人
    emargency_contact = db.StringField(require=True)
    emargency_contact_phone = db.StringField(require=True)
    emargency_contact_relationship = db.StringField(require=True)


class User(db.Document):

    username = db.StringField(required=True)  # 網站顯示的綽號
    # email = db.EmailField(required=True, unique=True)  # 登入帳號
    email = db.EmailField(required=True)
    signup_at = db.DateTimeField()
    last_login_at = db.DateTimeField()

    meta = {'abstract': True,}


class SttUser(User):

    # 基本資料
    name = db.StringField()  # 真實姓名
    password_hash = db.StringField(require=True)
    birthday = db.DateTimeField()
    cellphone_number = db.StringField()
    introduction = db.StringField()

    # 學校資料
    department = db.StringField()  # 系所，例如：物理、水利
    graduation_year = db.IntField()  # 畢業年，例如：102

    # 社團相關資料
    group = db.StringField(choices=Group.get_choices())  # 嚮導隊
    stt_departments = db.ListField(choices=SttDepartment.get_choices())  # 工作組，例如：岩推、總務、教學
    position = db.StringField(choices=Position.get_choices())  # 新生、隊員、幹部等
    member_info = db.EmbeddedDocumentField(MemberInfo)
    # experiences_list = 

    # 邀請信相關
    invitation_sent_at = db.DateTimeField()
    invitation_sent_by = db.ReferenceField('self')
    invitation_email = db.EmailField()  # 邀請信信箱

    created_by = db.ReferenceField('self')

    # 系統紀錄
    updated_at = db.DateTimeField()

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class GuestUser(User):
    pass
