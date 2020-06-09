import datetime
import pytz

from sttapp.db import db


class RecordModel(db.Document):

    # 系統紀錄
    created_by = db.ReferenceField('sttapp.users.models.SttUser')
    created_at = db.DateTimeField(default=datetime.datetime.utcnow)
    updated_by = db.ReferenceField('sttapp.users.models.SttUser')
    updated_at = db.DateTimeField()
    
    meta = {'abstract': True, }

    def _dt_to_str(self, dt):
        tz = pytz.timezone('Asia/Taipei')
        utc = pytz.timezone('UTC')
        utc_dt = utc.localize(dt)
        tz_dt = utc_dt.astimezone(tz)
        return tz_dt.strftime("%Y/%m/%d %H:%M")

    @property
    def created_at_str(self):
        return self._dt_to_str(self.created_at)

    @property
    def updated_at_str(self):
        return self._dt_to_str(self.updated_at)
