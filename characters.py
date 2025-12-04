# Файл characters.py - персонажі гри та їх дані

from PyQt6.QtGui import QColor

# Типи персонажів
CHARACTER_NARRATOR = "narrator"
CHARACTER_PLAYER = "player"
CHARACTER_GIRL = "girl"
CHARACTER_SYSTEM = "system"

# Дані персонажів
CHARACTER_DATA = {
    CHARACTER_NARRATOR: {
        "name": "Оповідач",
        "name_prefix": "Оповідач: ",
        "color": QColor(0, 255, 0)  # Зелений колір
    },
    CHARACTER_PLAYER: {
        "name": "Гравець",
        "name_prefix": "",  # У гравця немає префіксу
        "color": QColor(255, 255, 255)  # Білий колір
    },
    CHARACTER_GIRL: {
        "name": "Дівчина",
        "name_prefix": "Дівчина: ",
        "color": QColor(255, 100, 100)  # Рожево-червоний колір
    },
    CHARACTER_SYSTEM: {
        "name": "Система",
        "name_prefix": "Система: ",
        "color": QColor(200, 0, 0)  # Червоний колір
    }
}

# Функція для отримання даних персонажа
def get_character_data(character_id):
    return CHARACTER_DATA.get(character_id, CHARACTER_DATA[CHARACTER_PLAYER])

# Функція для отримання кольору тексту персонажа
def get_character_color(character_id):
    return get_character_data(character_id)["color"]

# Функція для отримання префіксу персонажа
def get_character_prefix(character_id):
    return get_character_data(character_id)["name_prefix"]

# Функція для визначення персонажа за текстом
def get_character_from_text(text):
    for char_id, char_data in CHARACTER_DATA.items():
        prefix = char_data["name_prefix"]
        if prefix and text.startswith(prefix):
            return char_id, text[len(prefix):]
    return CHARACTER_PLAYER, text

class Character:
    def __init__(self, name, description, is_alive=True, trust_level=0, hidden_traits=None):
        self.name = name
        self.description = description
        self.is_alive = is_alive
        self.trust_level = trust_level
        self.revealed_traits = []
        self.hidden_traits = hidden_traits if hidden_traits is not None else []

class Characters:
    def __init__(self):
        self.characters = {
            "koga": Character(
                "Коґа",
                "Цинік. Каже правду, бо не вірить, що хтось слухає.",
                hidden_traits=["правдолюб", "цинік", "самотній"]
            ),
            "ina": Character(
                "Іна",
                "Тиха дівчина, яка завжди просить довіритися.",
                hidden_traits=["маніпулятор", "самозбереження", "прихована жорстокість"]
            ),
            "lars": Character(
                "Ларс",
                "Жартівник, що прикриває страх гумором.",
                hidden_traits=["страх", "гумор", "вразливість"]
            ),
            "meilis": Character(
                "Мейліс",
                "Фальшива моральність. Завжди говорить про добро.",
                hidden_traits=["лицемірство", "маніпуляція", "влада"]
            ),
            "haru": Character(
                "Хару",
                "Мовчазний, завжди обирає опцію «вбити».",
                hidden_traits=["жорстокість", "ефективність", "холоднокровність"]
            ),
            "missing": Character(
                "Той, хто зник",
                "Гравець №7, якого всі вважали мертвим...",
                is_alive=False,
                hidden_traits=["таємниця", "виживання", "месник"]
            )
        }
    
    def get_character(self, name):
        return self.characters.get(name)
    
    def update_trust(self, name, value):
        if name in self.characters:
            self.characters[name].trust_level += value
    
    def reveal_trait(self, name, trait):
        if name in self.characters:
            char = self.characters[name]
            if trait in char.hidden_traits:
                char.hidden_traits.remove(trait)
                char.revealed_traits.append(trait)
    
    def kill_character(self, name):
        if name in self.characters:
            self.characters[name].is_alive = False
    
    def get_alive_characters(self):
        return {name: char for name, char in self.characters.items() if char.is_alive}

# Глобальний екземпляр для використання в інших файлах
characters = Characters() 