from sttapp.base.enums import Choice


class Group(Choice):
    bear = '小熊'
    star = '北極星'
    sansan = '三三'
    wolf = '野狼'
    goat = '山羊'


class Level(Choice):
    newbie = '新生'
    medium = '隊員'
    cadre = '幹部'


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
