import datetime
from flask_wtf import FlaskForm
from wtforms import ValidationError, IntegerField, StringField, SelectField, PasswordField, validators

from sttapp.members.models import Member
from .models import Member
from .enums import Gender


class MemberForm(FlaskForm):
    name = StringField("真實姓名", validators=[validators.DataRequired()])
    nickname = StringField()
    security_number = StringField("身份證字號", validators=[validators.DataRequired()])
    birthday = StringField(validators=[validators.DataRequired()])
    cellphone_number = StringField(validators=[validators.DataRequired()])
    gender = StringField(validators=[validators.DataRequired()])

    # 進階資料
    # email = EmailField()
    drug_allergy = StringField()
    # home_address = StringField()
    blood_type = StringField()
    level = StringField(validators=[validators.DataRequired()])  # 新生、隊員、幹部等

    # 學校資訊
    student_id = StringField()
    department_and_grade = StringField(validators=[validators.DataRequired()])  # ex: 水利四 / ob / 物理所 / 校外

    # 最高資歷
    highest_difficulty = StringField()  # 級數
    highest_difficulty_experience = StringField()  # 手動輸入出隊資歷，ex: 哈崙鐵道

    # 緊急聯絡人
    emargency_contact = StringField(validators=[validators.DataRequired()])
    emargency_contact_phone = StringField(validators=[validators.DataRequired()])
    emargency_contact_relationship = StringField()  # ex: 父子、母子
