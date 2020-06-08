class Choice:

    @classmethod
    def get_choices(cls):
        choices = [("NA", "未填寫")]
        for attr, v in cls.__dict__.items():
            if attr.startswith("__"):
                continue
            choices.append((attr, v))
        return choices

    @classmethod
    def get_map(cls):
        return {
            display: value for value, display in cls.get_choices()
        }


class FlashCategory:
    error = "danger"
    warn = "warning"
    info = "info"
    success = "success"
