from faker import Faker


class Fake(Faker):
    """Класс генератор рандомных значений для создания фикстур"""

fake = Fake('ru-RU')