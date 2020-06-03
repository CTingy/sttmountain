class Choice:

    @classmethod
     def get_choices(cls):
         choices = [("na", "未填寫")]
          for attr, v in cls.__dict__.items():
              if attr.startswith("__"):
                   continue
               choices.append((attr, v))
          return choices


class FlashCategory:
    error = "danger"
    warn = "warning"
    info = "info"
    success = "success"
