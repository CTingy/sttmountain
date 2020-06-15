import datetime
from flask_wtf import FlaskForm
from wtforms import ValidationError, IntegerField, TextAreaField ,StringField, SelectField, PasswordField, BooleanField, validators

from sttapp.members.models import Member
from sttapp.base.enums import EventType
from .models import Proposal


class ProposalForm(FlaskForm):
    title = StringField("隊伍名稱", validators=[validators.DataRequired("此為必填欄位")])
    start_date = StringField(
        "出發日期(含交通天)(YYYY/MM/DD)", validators=[validators.DataRequired("此為必填欄位")])
    days = StringField("預計天數(*不*含交通天)", validators=[validators.DataRequired("此為必填欄位")])
    has_d0 = BooleanField("是否有交通天", default=False)
    leader = StringField("領隊", validators=[validators.DataRequired("此為必填欄位")])
    guide = StringField("嚮導", validators=[validators.Optional()])
    attendees = StringField("成員")
    supporter = StringField("留守", validators=[validators.Optional()])
    event_type = StringField("隊伍類型", validators=[validators.Optional()])
    return_plan = TextAreaField("撤退計畫", validators=[validators.Optional()])
    buffer_days = StringField("預備天", validators=[validators.Optional()])
    approach_way = TextAreaField("交通方式", validators=[validators.Optional()])
    radio = StringField("無線電頻率/台號", validators=[
        validators.Optional(),
        validators.Regexp("^14[4-5].[0-9]{2}\/", message="格式錯誤")])
    satellite_telephone = StringField("衛星電話", validators=[
        validators.Optional(), 
        validators.Regexp("\+882[0-9]{10}$", message="電話格式錯誤，需為+882開頭，加上10碼數字")])
    open_time = StringField("開機時間(hh:mm)", validators=[validators.Optional()])

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.start_date_dt = None
        self.end_date_dt = None
        self.open_time_dt = None
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
    
    def _validate_date(self, field, for_date=True, for_time=False):

        if not field.data:
            raise ValidationError('缺少必填欄位')

        flags = []
        if for_date:
            flags.append(("%Y/%m/%d", "2020/04/09"))
        if for_time:
            flags.append(("%H:%M", "05:30"))

        dt_pattern = " ".join(i[0] for i in flags)
        dt_example = " ".join(i[1] for i in flags)

        try:
            dt = datetime.datetime.strptime(field.data, dt_pattern)
        except ValueError:
            raise ValidationError('格式錯誤，正確範例為{}'.format(dt_example))
        # if dt < datetime.datetime.now():
        #     raise ValidationError('日期不合理')

        setattr(self, "{}_dt".format(field.id), dt)

    def _validate_int(self, field):
        try:
            field.data = int(field.data)
        except ValueError:
            raise ValidationError("格式錯誤，請填入數字")

    def validate_start_date(self, field):
        return self._validate_date(field)

    def validate_end_date(self, field):
        return self._validate_date(field)

    def validate_days(self, field):
        return self._validate_int(field)

    def validate_leader(self, field):
        id_ = self._get_member_id(field.data)
        self.leader_id = id_
        return None

    def validate_guide(self, field):
        id_ = self._get_member_id(field.data)
        self.guide_id = id_
        return None

    def validate_attendees(self, field):
        data_list = field.data.split(', ')
        ids = [self.leader_id]
        if self.guide_id:
            ids.append(self.guide_id)
        for data in data_list:
            data = data.strip()
            if not data:
                continue
            ids.append(self._get_member_id(data))
        self.attendees_ids = list(set(ids))
        return None

    def validate_event_type(self, field):
        keys = EventType.get_map(False).keys()
        if field.data not in EventType.get_map(False).values():
            raise ValidationError("隊伍類型需為{}的其中一個".format("、".join(keys)))

    def validate_buffer_days(self, field):
        return self._validate_int(field)

    def validate_open_time(self, field):
        self._validate_date(field, False, True)


class ItineraryForm(FlaskForm):
    content = StringField()
    water_info = StringField()
    communication_info = StringField()
