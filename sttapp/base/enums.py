class Choice:

    @classmethod
    def get_choices(cls, include_na=True):
        if include_na:
            choices = [("NA", "未填寫")]
        else:
            choices = []
        for attr, v in cls.__dict__.items():
            if attr.startswith("__"):
                continue
            choices.append((attr, v))
        return choices

    @classmethod
    def get_map(cls, include_na=True):
        return {
            display: value for value, display in cls.get_choices(include_na)
        }


class FlashCategory:
    error = "danger"
    warn = "warning"
    info = "info"
    success = "success"
