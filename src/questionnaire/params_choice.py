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


class BodyType(str, Enum):
    skinny = "Худое"
    full_physique = "Полное"
    athletic = "Спортивное"
    average = "Среднее"
