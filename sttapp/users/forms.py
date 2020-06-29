import datetime

from mongoengine import URLField, ValidationError


class MyHistoryForm:

    def __init__(self, form):
        self.start_date = form.get("start_date")
        self.end_date = form.get("end_date")
        self.order = form.get("order")
        self.title = form.get("title")
        self.days = form.get("days")
        self.event_type = form.get("event_type")
        self.link = form.get("link")

    def validate(self):
        validation_errors = dict()
        for k, v in self.__dict__.items():
            func = getattr(self, "validate_{}".format(k))
            err = func()
            if err:
                validation_errors[k] = err
        if validation_errors:
            return validation_errors
        return None

    def validate_start_date(self):
        try:
            self.start_date = datetime.datetime.strptime(self.start_date, "%Y/%m/%d")
        except ValueError:
            return "開始日期格式錯誤，需為YYYY/MM/DD。 "

    def validate_end_date(self):
        try:
            self.end_date = datetime.datetime.strptime(self.end_date, "%Y/%m/%d")
        except ValueError:
            return "結束日期格式錯誤，需為YYYY/MM/DD"

    def validate_order(self):
        try:
            self.order = int(self.order)
        except ValueError:
            return "排序格式錯誤，需為數字"
    
    def validate_title(self):
        if len(self.title) > 30:
            return "標題太長囉，最多30個字"
    
    def validate_days(self):
        try:
            self.days = int(self.days)
        except ValueError:
            return "天數格式錯誤，需為數字"

    def validate_event_type(self):  # not required field
        if not self.event_type:
            self.event_type = None
            return
        if len(self.event_type) > 8:
            return "隊伍類型太長囉，最多8個字"

    def validate_link(self):  # not required field
        if not self.link:
            self.link = None
            return 
        u = URLField()
        try:
            u.validate(self.link)
        except ValidationError:
            return "連結格式錯誤，需為有效網址"
