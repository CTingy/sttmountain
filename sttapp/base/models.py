import datetime
import pytz

from sttapp.db import db
from .utils import get_local_dt


class RecordModel(db.Document):

    # 系統紀錄
    created_by = db.ReferenceField('sttapp.users.models.SttUser')
    created_at = db.DateTimeField(default=datetime.datetime.utcnow)
    updated_by = db.ObjectIdField()
    updated_at = db.DateTimeField()
    
    meta = {'abstract': True, }

    def _dt_to_str(self, dt):
        tz_dt = get_local_dt(dt)
        return tz_dt.strftime("%Y/%m/%d %H:%M")

    def _d_to_str(self, dt):
        # 不可進行時區轉換
        return dt.strftime("%Y/%m/%d")

    @property
    def created_at_str(self):
        return self._dt_to_str(self.created_at)

    @property
    def updated_at_str(self):
        return self._dt_to_str(self.updated_at)
