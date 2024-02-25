from enum import Enum


class Passion(str, Enum):
    trips = "Путешествия"
    photo = "Фотография"
    music = "Музыка"


class Gender(str, Enum):
    male = "Male"
    female = "Female"


class Goal(str, Enum):
    relationships = "Серьезные отношения"
    flirts = "Флирт"
    friendship = "Дружба"
    for_one_day = "Ha одну ночь"
    open_relationship = "Открытые отношения"
    new_experience = "Новый опыт"
    nothing_serious = "Ничего серьезного"
    communication = "Общение"


class SmokingType(str, Enum):
    positive = "Курю"
    normal = "Нормально"
    negative = "Негативно"


class AlcoholType(str, Enum):
    often = "Пью часто"
    sometimes = "Иногда выпиваю"
    negative = "He пью"
    hate = "Негативно"


class SportType(str, Enum):
    often = "Часто занимаюсь"
    sometimes = "Иногда занимаюсь"
    negative = "He занимаюсь"
    hate = "He люблю спорт"


class BodyType(str, Enum):
    skinny = "Худое"
    full_physique = "Полное"
    athletic = "Спортивное"
    average = "Среднее"
