from game_state import game_state
from characters import characters

class GameEngine:
    def __init__(self):
        self.manipulation_level = 0
        self.revealed_truths = set()
        self.hidden_truths = set()
        self.comments = {
            "trust": [
                "Довіра? Цікавий вибір...",
                "Ви дійсно думаєте, що можете довіряти?",
                "Довіра — це слабкість."
            ],
            "betray": [
                "Зрада? Очікувано...",
                "Ви вже починаєте розуміти правила?",
                "Зрада — це сила."
            ],
            "sacrifice": [
                "Жертва? Як благородно...",
                "Ви готові пожертвувати собою?",
                "Жертва — це слабкість."
            ],
            "lie": [
                "Брехня? Розумний вибір...",
                "Ви вчитесь грати по-справжньому.",
                "Брехня — це сила."
            ]
        }
    
    def get_comment(self, choice_type):
        import random
        return random.choice(self.comments.get(choice_type, ["Цікавий вибір..."]))
    
    def manipulate_truth(self, truth, is_hidden=True):
        if is_hidden:
            self.hidden_truths.add(truth)
        else:
            self.revealed_truths.add(truth)
            if truth in self.hidden_truths:
                self.hidden_truths.remove(truth)
    
    def get_manipulated_truth(self, truth):
        # Тут можна додати логіку маніпуляції істиною
        return truth if truth not in self.hidden_truths else "Маніпульована істина"
    
    def increase_manipulation(self):
        self.manipulation_level += 1
    
    def get_manipulation_level(self):
        return self.manipulation_level

# Глобальний екземпляр для використання в інших файлах
game_engine = GameEngine() 