import datetime
from flask_wtf import FlaskForm
from wtforms.fields.html5 import EmailField
from wtforms import ValidationError, StringField, SelectField, PasswordField, validators

from sttapp.users.models import SttUser
from sttapp.users.enums import Group, Level, Position


class InvitationForm(FlaskForm):

    email = EmailField('Email', validators=[validators.DataRequired("此為必填欄位")])

    def validate_email(self, field):
        if SttUser.objects(email=field.data):
            raise ValidationError('此email已經有人使用，請重新輸入')


class SignupForm(FlaskForm):
    username = StringField(
        "* 綽號", 
        validators=[
            validators.DataRequired("此為必填欄位"), 
            validators.Length(max=10, message="太長了呦，最多10個字")
        ]
    )
    name = StringField(
        "真實姓名（隱藏）", 
        validators=[validators.Length(max=10, message="太長了呦，最多10個字")]
    )
    birthday = StringField("生日（隱藏）")
    cellphone_number = StringField("手機（隱藏）")
    department = StringField("系所")
    graduation_year = StringField("畢業年份")
    group = SelectField("嚮導隊", choices=Group.get_choices())
    position = SelectField("工作組", choices=Position.get_choices())
    level = SelectField("最高位階", choices=Level.get_choices())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.birthday_dt = None
    
    def validate_username(self, field):
        field.data = field.data.strip()
    
    def validate_birthday(self, field):
        if not field.data:
            return None
        try:
            dt = datetime.datetime.strptime(field.data, "%Y/%m/%d")
        except ValueError:
            raise ValidationError('格式錯誤，正確範例為1985/01/05')
        
        if dt > datetime.datetime.now() or dt < datetime.datetime(1910, 1, 1):
            raise ValidationError('日期不合理')
        
        self.birthday_dt = dt

    def validate_cellphone_number(self, field):
        if not field.data:
            return None
        if not field.data.startswith("09"):
            raise ValidationError('手機號碼必須為09開頭')
        if len(field.data) != 10:
            raise ValidationError('手機號碼必須為10碼')

    def validate_graduation_year(self, field):
        
        if not field.data:
            return None
        max_graduation_year = datetime.datetime.now().year-1903
        try:
            field.data = int(field.data)
        except TypeError:
            raise ValidationError('畢業年份需為數字')

        if field.data > max_graduation_year or field.data < 40:
            raise ValidationError('需介於40至{}之間'.format(max_graduation_year))


class SttSignupForm(SignupForm):
    password = PasswordField("* 密碼（長度6至20）", validators=[
        validators.DataRequired("此為必填欄位"), 
        validators.Length(min=6, max=20, message="長度6至20")])
    confirm = PasswordField("* 請重複輸入密碼", validators=[
        validators.DataRequired("此為必填欄位"),
        validators.EqualTo("password", "密碼輸入不一致")
    ])


class PostSignupForm(SignupForm):
    pass


class LoginForm(FlaskForm):

    email = EmailField('Email', validators=[validators.DataRequired("此為必填欄位")])
    password = PasswordField("密碼", validators=[validators.DataRequired("此為必填欄位")])

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user_in_db = None

    def validate_email(self, field):
        try:
            self.user_in_db = SttUser.objects.get(email=field.data)
        except SttUser.DoesNotExist:
            raise ValidationError('該email不存在，請重新輸入，或申請註冊帳號')

    def validate_password(self, field):
        if self.user_in_db and not self.user_in_db.check_password(field.data):
            raise ValidationError('密碼錯誤，請重新輸入')
