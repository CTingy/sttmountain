class Choice:
     
     @classmethod
     def get_choices(cls):
          choices = []
          for attr, v in cls.__dict__.items():
               if attr.startswith("__"):
                    continue
               choices.append((attr, v))
          return choices


class Group(Choice):
     bear = '小熊'
     star = '北極星'
     sansan = '三三'
     wolf = '野狼'
     goat = '山羊'


class Level(Choice):
     fresh = '新生'
     junior = '隊員'
     senior = '幹部'


class Position(Choice):
     president = '社長'
     education = '教學組'
     outfit = '裝備組'
     rock = '岩推組'
     tech = '技推組'
     info = '資訊組'
     medicine = '醫藥箱組'
     leader = '山防組長'
     leader_of_sr = '幹部群長'
     account = '總務'
