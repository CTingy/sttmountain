import datetime
from flask_wtf import FlaskForm
from wtforms import ValidationError, IntegerField, StringField, SelectField, PasswordField, validators

from sttapp.members.models import Member
from sttapp.base.enums import EventType
from .models import Proposal


class ProposalForm(FlaskForm):
    title = StringField("隊伍名稱", validators=[validators.DataRequired("此為必填欄位")])
    start_date = StringField(
        "出發日期(含交通天)(YYYY/MM/DD)", validators=[validators.DataRequired("此為必填欄位")])
    days = StringField("預計天數(含交通天)")
    leader = StringField("領隊", validators=[validators.DataRequired("此為必填欄位")])
    guide = StringField("嚮導")
    attendees = StringField("成員")
    supporter = StringField("留守")
    event_type = SelectField("隊伍類型", choices=EventType.get_choices())
    return_plan = StringField("撤退計畫")
    buffer_days = StringField("預備天(預設1天)")
    approach_way = StringField("交通方式")
    radio = StringField("無線電頻率/台號")
    satellite_telephone = StringField("衛星電話")
    gathering_point = StringField("集合地點")
    gathering_time = StringField("集合時間(YYYY/MM/DD hh:mm)")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.start_date_dt = None
        self.gathering_time_dt = None
        self.leader_id = None
        self.guide_id = None
        self.attendees_ids = None

    def _get_member_id(self, data):    
        try:
            name = data.split("|")[0]
            security_number = data.split("|")[1]
        except Exception:
            raise ValidationError("格式錯誤，應為：姓名|身份證字號")
        
        try:
            member = Member.objects.get(security_number=security_number)
        except Member.DoesNotExist:
            raise ValidationError("{}不存在".format(name))
        return member.id
    
    def _validate_date(self, field, has_time=False):

        if not field.data:
            raise ValidationError('缺少必填欄位')

        dt_pattern = "%Y/%m/%d"
        dt_example = "2020/04/09"

        if has_time:
            dt_pattern += " %H:%M"
            dt_example += " 19:15"

        try:
            dt = datetime.datetime.strptime(field.data, dt_pattern)
        except ValueError:
            raise ValidationError('格式錯誤，正確範例為{}'.format(dt_example))
        # if dt < datetime.datetime.now():
        #     raise ValidationError('日期不合理')

        setattr(self, "{}_dt".format(field.id), dt)

    def _validate_int(self, field):
        try:
            int(field.data)
        except ValueError:
            raise ValidationError("格式錯誤，請填入數字")     

    def validate_start_date(self, field):
        return self._validate_date(field)

    def validate_days(self, field):
        return self._validate_int(field)

    def validate_leader(self, field):
        id_ = self._get_member_id(field.data)
        self.leader_id = id_
        return None

    def validate_guide(self, field):
        if not field.data:
            return None
        id_ = self._get_member_id(field.data)
        self.guide_id = id_
        return None

    def validate_attendees(self, field):
        if not field.data:
            return None
        data_list = field.data.split(', ')
        ids = []
        for data in data_list:
            data = data.strip()
            if not data:
                continue
            ids.append(self._get_member_id(data))
        
        ids.append(self.leader_id)
        ids.append(self.guide_id)
        self.attendees_ids = list(set(ids))
        return None

    def validate_event_type(self, field):
        types = [i[0] for i in EventType.get_choices()]
        if field.data not in types:
            raise ValidationError("隊伍類型錯誤")

    def validate_buffer_days(self, field):
        if not field.data:
            return None
        return self._validate_int(field)

    def validate_gathering_time(self, field):
        if not field.data:
            return None
        self._validate_date(field, True)
        if self.gathering_time_dt.date() > self.start_date_dt.date():
            self.gathering_time_dt = None
            raise ValidationError('集合時間不得晚於上山時間')


class ItineraryForm(FlaskForm):
    content = StringField("")
    water_info = StringField()
    communication_info = StringField()
