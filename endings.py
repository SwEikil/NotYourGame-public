from game_state import game_state

class Endings:
    @staticmethod
    def check_endings():
        karma = game_state.get_karma()
        choices = game_state.get_choices()
        
        # Визначення кінцівок
        endings = [
            {
                "id": "hero",
                "condition": lambda: karma >= 3 and 1 in choices,
                "title": "Геройська кінцівка",
                "message": "Ви стали героєм! Ваші добрі вчинки змінили світ на краще."
            },
            {
                "id": "villain",
                "condition": lambda: karma <= -3 and 2 in choices,
                "title": "Лиходійська кінцівка",
                "message": "Ви стали лиходієм... Ваші дії призвели до хаосу."
            },
            {
                "id": "neutral",
                "condition": lambda: -2 <= karma <= 2 and len(choices) >= 3,
                "title": "Нейтральна кінцівка",
                "message": "Життя триває. Ваші вибори збалансовані."
            },
            {
                "id": "mystery",
                "condition": lambda: len(choices) >= 5,
                "title": "Таємнича кінцівка",
                "message": "Істина залишається прихованою... Ваш шлях повний загадок."
            }
        ]
        
        # Перевірка кожної кінцівки
        for ending in endings:
            if ending["condition"]():
                return ending
        
        return None 