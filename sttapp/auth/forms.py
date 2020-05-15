from flask_wtf import FlaskForm
from wtforms.fields.html5 import EmailField
from wtforms import StringField, PasswordField, SubmitField
from wtforms import validators


class SignupForm(FlaskForm):
    username = StringField(
        "*綽號(用於網站顯示名稱，中英文皆可)", 
        validators=[
            validators.DataRequired(), 
            validators.Length(max=10, message="太長了呦，最多10個字")
        ]
    )
    # email = EmailField('Email', validators=[validators.DataRequired()])
    password = PasswordField("*密碼(長度6至20)", validators=[
        validators.DataRequired(), 
        validators.Length(min=6, max=20, message="長度6至20")])
    confirm = PasswordField("*請重複輸入密碼", validators=[
        validators.DataRequired(),
        validators.EqualTo("password", "密碼輸入不一致")
    ])

    def validate_email(self, field):
        if UserReister.query.filter_by(email=field.data).first():
            raise ValidationError('Email already register by somebody')

