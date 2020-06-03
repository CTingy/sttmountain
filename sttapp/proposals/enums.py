from sttapp.base.enums import Choice


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
