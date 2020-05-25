from flask_wtf import FlaskForm
from wtforms.fields.html5 import EmailField
from wtforms import StringField, PasswordField, SubmitField, ValidationError, validators

from sttapp.users.models import SttUser


class InvitationForm(FlaskForm):

    email = EmailField('Email', validators=[validators.DataRequired()])

    def validate_email(self, field):
        if SttUser.objects(email=field.data):
            raise ValidationError('此email已經有人使用，請重新輸入')


class SignupForm(FlaskForm):
    username = StringField(
        "*綽號(用於網站顯示名稱，中英文皆可)", 
        validators=[
            validators.DataRequired(), 
            validators.Length(max=10, message="太長了呦，最多10個字")
        ]
    )
    password = PasswordField("*密碼(長度6至20)", validators=[
        validators.DataRequired(), 
        validators.Length(min=6, max=20, message="長度6至20")])
    confirm = PasswordField("*請重複輸入密碼", validators=[
        validators.DataRequired(),
        validators.EqualTo("password", "密碼輸入不一致")
    ])


class LoginForm(FlaskForm):

    email = EmailField('Email', validators=[validators.DataRequired()])
    password = PasswordField("密碼", validators=[validators.DataRequired()])

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
