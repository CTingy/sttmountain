import datetime

from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

from sttapp.db import db
from sttapp.login import login_manager
from sttapp.base.enums import Group, Position, Level
from sttapp.base.models import RecordModel


class InvitationInfo(db.EmbeddedDocument):

    invited_by = db.ReferenceField('sttapp.members.models.SttUser')
    invited_at = db.DateTimeField()
    email = db.EmailField()
    token = db.StringField()


class User(UserMixin, RecordModel):

    username = db.StringField()  # 網站顯示的綽號
    email = db.EmailField(unique=True)  # 登入帳號

    last_login_at = db.DateTimeField()
    social_login_with = db.StringField()
    social_login_id = db.StringField()
    profile_img = db.URLField()

    meta = {'abstract': True, }


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
    position = db.StringField(choices=Position.get_choices())  # 工作組，總務、教學
    level = db.StringField(choices=Level.get_choices())  # 新生、隊員、幹部等
    member_info = db.ReferenceField('sttapp.members.models.Member')
    # experiences_list =
    # stt_experiences_list =

    # 系統紀錄
    updated_at = db.DateTimeField()
    invitation_info = db.EmbeddedDocumentField(InvitationInfo)

    @property
    def birthday_str(self):
        if self.birthday:
            return self.birthday.strftime("%Y/%m/%d")
        return ""
    
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


@login_manager.user_loader
def load_user(user_id):
    try:
        return SttUser.objects.get(id=user_id)
    except SttUser.DoesNotExist:
        return None
