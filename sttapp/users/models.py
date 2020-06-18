import datetime

from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

from sttapp.db import db
from sttapp.login import login_manager
from sttapp.base.enums import Group, Position, Level, Identity, Difficulty
from sttapp.base.models import RecordModel


class InvitationInfo(db.EmbeddedDocument):

    invited_by = db.ObjectIdField()
    invited_at = db.DateTimeField()
    email = db.EmailField()
    token = db.StringField()


class MyHistory(RecordModel):
    
    order = db.IntField()
    title = db.StringField()
    start_date = db.DateTimeField()
    end_date = db.DateTimeField()
    days = db.IntField()
    event_type = db.StringField()
    link = db.URLField()

    meta = {'ordering': ['order']}

    @property
    def start_date_str(self):
        if self.start_date:
            return super()._d_to_str(self.start_date)
        return ""

    @property
    def end_date_str(self):
        if self.end_date:
            return super()._d_to_str(self.end_date)
        return ""

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


class User(UserMixin, RecordModel):

    username = db.StringField()  # 網站顯示的綽號
    email = db.EmailField(unique=True)  # 登入帳號

    last_login_at = db.DateTimeField()
    social_login_with = db.StringField()
    social_login_id = db.StringField()
    profile_img = db.URLField()

    meta = {'abstract': True, }

    @property
    def last_login_at_str(self):
        return super()._dt_to_str(self.last_login_at)


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
    member_id = db.ObjectIdField()
    identity = db.StringField(choices=Identity.get_choices())  # 在校狀態

    # 系統紀錄
    updated_at = db.DateTimeField()
    invitation_info = db.EmbeddedDocumentField(InvitationInfo)
    my_history_ids = db.ListField(db.ObjectIdField(), default=list)

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
