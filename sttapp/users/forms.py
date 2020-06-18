import datetime
import re


class MyHistoryForm():

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
        for k, v in self.__dict__:
            if not v:
                continue
            func = getattr(self, "validate_{}".format(k))
            err = func(v)
            if err:
                validation_errors[k] = err
        return validation_errors

    def validate_start_date(self):
        try:
            dt = datetime.datetime.strptime(self.start_date, "%Y/%m/%d")
        except ValueError:
            return "開始日期格式錯誤"
        self.start_date = dt
