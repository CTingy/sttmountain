import datetime
from flask_wtf import FlaskForm
from wtforms import ValidationError, IntegerField, StringField, SelectField, PasswordField, validators

from .models import Proposal


class ProposalForm(FlaskForm):
    title = StringField("隊伍名稱", validators=[validators.DataRequired()])
    start_date = StringField(
        "出發日期(含交通天)(YYYY/MM/DD)", validators=[validators.DataRequired()])
    days = IntegerField("預計天數", default=1, validators=[
                        validators.DataRequired()])
    leader = StringField("領隊")
    guide = StringField("嚮導")
    supporter = StringField("留守")
    return_plan = StringField("撤退計畫")
    buffer_days = IntegerField("預備天", default=1)
    approach_way = StringField("交通方式")
    radio = StringField("無線電頻率/台號")
    satellite_telephone = StringField("衛星電話")
    gathering_point = StringField("集合地點")
    gathering_time = StringField("集合時間(YYYY/MM/DD hh:mm)")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.start_date_dt = None
        self.end_date_dt = None
        self.gathering_at_dt = None

    def _validate_date(self, field, has_time=False):

        if not field.data:
            raise ValidationError('缺少必填欄位')

        dt_pattern = "%Y/%m/%d"
        dt_example = "2020/04/09"

        if has_time:
            dt_pattern += " %H:%M"
            example += " 19:15"

        try:
            dt = datetime.datetime.strptime(field.data, dt_pattern)
        except ValueError:
            raise ValidationError('格式錯誤，正確範例為{}'.format(example))
        # if dt < datetime.datetime.now():
        #     raise ValidationError('日期不合理')

        setattr(self, "{}_dt".format(field.id), dt)

    def validate_start_date(self, field):
        return self._validate_date(field)

    def validate_gathering_at(self, field):
        if not field.data:
            return None
        self._validate_date(field, True)
        if self.gathering_at_dt > self.start_date_dt:
            self.gathering_at_dt = None
            raise ValidationError('集合時間不得晚於上山時間')


class ItineraryForm(FlaskForm):
    content = StringField("")
    water_info = StringField()
    communication_info = StringField()
