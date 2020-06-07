import datetime

from sttapp.db import db


class RecordModel(db.Document):

    # 系統紀錄
    created_by = db.ReferenceField('sttapp.users.models.SttUser')
    created_at = db.DateTimeField(default=datetime.datetime.utcnow)
    updated_by = db.ReferenceField('sttapp.users.models.SttUser')
    updated_at = db.DateTimeField()
    
    meta = {'abstract': True, }
