import datetime
from flask_wtf import FlaskForm
from wtforms import ValidationError, IntegerField, StringField, SelectField, PasswordField, validators

from sttapp.members.models import Member
from .models import Member
from .enums import Gender


class MemberForm(FlaskForm):
    name = StringField("真實姓名", validators=[validators.DataRequired("此為必填欄位")])
    nickname = StringField()
    security_number = StringField("身份證字號", validators=[validators.DataRequired("此為必填欄位")])
    birthday = StringField(validators=[validators.DataRequired("此為必填欄位")])
    cellphone_number = StringField(validators=[validators.DataRequired("此為必填欄位")])
    gender = StringField(validators=[validators.DataRequired("此為必填欄位")])

    # 進階資料
    # email = EmailField()
    drug_allergy = StringField()
    # home_address = StringField()
    blood_type = StringField()
    level = StringField(validators=[validators.DataRequired("此為必填欄位")])  # 新生、隊員、幹部等

    # 學校資訊
    student_id = StringField()
    department_and_grade = StringField(validators=[validators.DataRequired("此為必填欄位")])  # ex: 水利四 / ob / 物理所 / 校外

    # 最高資歷
    highest_difficulty = StringField()  # 級數
    highest_difficulty_experience = StringField()  # 手動輸入出隊資歷，ex: 哈崙鐵道

    # 緊急聯絡人
    emergency_contact = StringField(validators=[validators.DataRequired("此為必填欄位")])
    emergency_contact_phone = StringField(validators=[validators.DataRequired("此為必填欄位")])
    emergency_contact_relationship = StringField()  # ex: 父子、母子

    def validate_security_number(self, field):
        if not field.data[0].isupper():
            raise ValidationError("")