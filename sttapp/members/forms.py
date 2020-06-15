import datetime
import re
from flask_wtf import FlaskForm
from wtforms import ValidationError, IntegerField, StringField, SelectField, PasswordField, validators

from sttapp.members.models import Member
from sttapp.base.enums import Level, Gender, Difficulty, Group
from .models import Member


class MemberForm(FlaskForm):
    name = StringField("真實姓名", validators=[validators.DataRequired("此為必填欄位")])
    nickname = StringField("綽號")
    security_number = StringField("身份證字號", validators=[
        validators.DataRequired("此為必填欄位"),
        validators.Regexp("^[A-Z]\d{9}$", message="身份證字號格式需為：首字大寫加9碼數字")])
    birthday = StringField("生日", validators=[validators.DataRequired("此為必填欄位")])
    cellphone_number = StringField("手機號碼", validators=[
        validators.DataRequired("此為必填欄位"), 
        validators.Regexp("09[0-9]{8}$", message="電話格式錯誤，需為09開頭之數字共10碼")])
    group = StringField("嚮導隊", validators=[validators.Optional()])

    # 進階資料
    # email = EmailField()
    drug_allergy = StringField("藥物過敏")
    # home_address = StringField()
    blood_type = StringField("血型")
    level = StringField("山協等級", validators=[validators.DataRequired("此為必填欄位")])  # 新生、隊員、幹部等

    # 學校資訊
    student_id = StringField("學號", validators=[
        validators.Optional(), validators.Regexp("[A-Z]\d{8}$", message="學號格式錯誤")])
    department_and_grade = StringField("系級/OB/校外", validators=[validators.DataRequired("此為必填欄位")])  # ex: 水利四 / ob / 物理所 / 校外

    # 最高資歷
    highest_difficulty = StringField("最高資歷級數")  # 級數
    highest_difficulty_experience = StringField("最高資歷路線")  # 手動輸入出隊資歷，ex: 哈崙鐵道

    # 緊急聯絡人
    emergency_contact = StringField("緊急聯絡人", validators=[validators.DataRequired("此為必填欄位")])
    emergency_contact_phone = StringField("聯絡人電話", validators=[
        validators.DataRequired("此為必填欄位"), 
        validators.Regexp("09[0-9]{8}$", message="電話格式錯誤，需為09開頭之數字共10碼")])
    emergency_contact_relationship = StringField("與聯絡人關係")  # ex: 父子、母子

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.birthday_dt = None

    def validate_birthday(self, field):
        try:
            dt = datetime.datetime.strptime(field.data, "%Y/%m/%d")
            self.birthday_dt = dt
        except ValueError:
            raise ValidationError("出生日期格式錯誤，應為：YYYY/MM/DD")

    def validate_group(self, field):
        keys = Group.get_map(False).keys()
        if field.data not in Group.get_map(False).values():
            raise ValidationError("嚮導隊需為{}的其中一個，或是不填寫".format("、".join(keys)))
       
    def validate_level(self, field):
        keys = Level.get_map(False).keys()
        if field.data not in Level.get_map(False).values():
            raise ValidationError("等級需為{}的其中一個".format("、".join(keys)))

    def validate_highest_difficulty(self, field):
        if not field.data:
            return None
        keys = Difficulty.get_map(False).keys()
        if field.data not in Difficulty.get_map(False).values():
            raise ValidationError("最高級數需為{}的其中一個".format("、".join(keys)))
