from flask_wtf import Form
from wtforms import StringField
from wtforms.validators import DataRequired


class SignupForm(Form):

     username = StringField('姓名或綽號')
