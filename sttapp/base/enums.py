class FlashCategory:
    ERROR = "danger"
    WARNING = "warning"
    INFO = "info"
    SUCCESS = "success"


class Choice:

    @classmethod
    def get_choices(cls, include_na=True):
        if include_na:
            choices = [("", "未填寫")]
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


class Identity(Choice):

    OB = "OB"
    IN_NCKU = "在校生"
    OUT_NCKU = "校外" 


class Difficulty(Choice):

    LEVEL_A = "A"
    LEVEL_B = "B"
    LEVEL_C = "C"
    LEVEL_D = "D"


class EventType(Choice):

    EXPORATION = "探勘"
    GENERAL = "活動"
    RIVER_TRACING = "溯溪"
    SNOW = "雪地"
    OTHERS = "其他"


class Gender(Choice):

    FEMALE = '女'
    MALE = '男'


class Group(Choice):
    BEAR = '小熊'
    STAR = '北極星'
    SANSAN = '三三'
    WOLF = '野狼'
    GOAT = '山羊'


class Level(Choice):
    NEWBIE = '新生'
    MEDIUM = '隊員'
    CADRE = '幹部'


class Position(Choice):
    PRESIDENT = '社長'
    EDUCATION = '教學組'
    EQUIPMENT = '裝備組'
    ROCK = '岩推組'
    TECH = '技推組'
    IT = '資料組'
    MEDICINE = '醫藥箱組'
    CHIEF = '山防組長'
    CADRE_LEAD = '幹部群長'
    ACCOUNT = '總務'


class EventStatus(Choice):
    BACK = "已下山"  # 包含撤退，就是會有re出隊文的情況
    CANCEL = "已倒隊"
    NORM = "出隊"
