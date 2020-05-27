import datetime

from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

from sttapp.db import db
from sttapp.login import login_manager
from .enums import Group, Position, Level


class MemberInfo(db.EmbeddedDocument):

    # 進階資料
    security_number = db.StringField()
    gender = db.StringField()
    drug_allergy = db.StringField()
    home_address = db.StringField()

    # 學校資訊
    student_id = db.StringField()
    department_and_grade = db.StringField()  # ex: 水利四 / ob / 物理所 / 校外

    # 最高資歷
    highest_difficulty = db.StringField()  # 級數（A, B, C, D）
    highest_difficulty_experience = db.StringField()  # 手動輸入出隊資歷，ex: 哈崙鐵道

    # 緊急聯絡人
    emargency_contact = db.StringField()
    emargency_contact_phone = db.StringField()
    emargency_contact_relationship = db.StringField()


class InvitationInfo(db.EmbeddedDocument):

    invited_by = db.ReferenceField('SttUser')
    invited_at = db.DateTimeField()
    email = db.EmailField()
    token = db.StringField()


class User(UserMixin, db.Document):

    username = db.StringField()  # 網站顯示的綽號
    email = db.EmailField(unique=True)  # 登入帳號
    created_at = db.DateTimeField()
    last_login_at = db.DateTimeField()
    social_login_with = db.StringField()
    social_login_id = db.StringField()
    profile_img = db.URLField()

    meta = {'abstract': True,}


class SttUser(User):

    # 基本資料
    name = db.StringField()  # 真實姓名
    password_hash = db.StringField()
    birthday = db.DateTimeField()
    cellphone_number = db.StringField()
    introduction = db.StringField()

    # 學校資料
    department = db.StringField()  # 系所，例如：物理、水利
    graduation_year = db.IntField()  # 畢業年，例如：102

    # 社團相關資料
    group = db.StringField(choices=Group.get_choices())  # 嚮導隊
    position = db.StringField(choices=Position.get_choices())  # 工作組，例如：岩推、總務、教學
    level = db.StringField(choices=Level.get_choices())  # 新生、隊員、幹部等
    member_info = db.EmbeddedDocumentField(MemberInfo)
    # experiences_list = 

    # 系統紀錄
    updated_at = db.DateTimeField()
    invitation_info = db.EmbeddedDocumentField(InvitationInfo)

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


class TempUser(db.Document):
    """給領隊暫時建出隊資料用的，使用者一旦註冊了SttUser，就使用姓名與手機搜尋此物件
    將此物件資料匯入SttUser後，刪除此物件
    """

    # 基本資料
    name = db.StringField()  # 真實姓名
    email = db.EmailField()

    birthday = db.DateTimeField()
    cellphone_number = db.StringField()

    member_info = db.EmbeddedDocumentField(MemberInfo)

    # 系統紀錄
    created_by = db.ReferenceField('SttUser')
    created_at = db.DateTimeField(default=datetime.datetime.utcnow)
    updated_by = db.ReferenceField('SttUser')
    updated_at = db.DateTimeField()
    # experiences_list = 


@login_manager.user_loader  
def load_user(user_id):
    try:
        return SttUser.objects.get(id=user_id)
    except SttUser.DoesNotExist:
        return None
