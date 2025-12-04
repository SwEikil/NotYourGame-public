# Файл karma.py - система карми та відстеження дій гравця

# Типи карми
KARMA_RULES_LEARNED = "rules_learned"  # Гравець дізнався правила
KARMA_DEBT_INFO = "debt_info"  # Гравець дізнався про борг
KARMA_HELPLESSNESS = "helplessness"  # Гравець відчув безпорадність
KARMA_FEAR = "fear"  # Страх
KARMA_CONTROL = "control"  # Відчуття контролю
KARMA_VULNERABILITY = "vulnerability"  # Вразливість
KARMA_NEUTRAL_REACTION = "neutral_reaction"  # Нейтральна реакція
KARMA_TRUST = "trust"  # Довіра
KARMA_WORLD_HINT = "world_hint"  # Підказка про світ
KARMA_TENSION = "tension"  # Напруження
KARMA_SUSPICION = "suspicion"  # Підозра
KARMA_HUMANITY = "humanity"  # Гуманність
KARMA_SYMPATHY = "sympathy"  # Симпатія
KARMA_EMOTIONAL_TRUST = "emotional_trust"  # Емоційна довіра
KARMA_SOFT_PATH = "soft_path"  # М'який шлях у наступних розділах
KARMA_PASSIVE_BRANCH = "passive_branch"  # Пасивна гілка для тих, хто мовчить частіше
KARMA_RESPONSIBILITY = "responsibility"  # Відповідальність
KARMA_GAME_WILL_REMEMBER = "game_will_remember"  # Гра запам'ятає вибір
KARMA_GAME_PROVOCATION = "game_provocation"  # Гра провокує гравця
KARMA_KARMA_BALANCE = "karma_balance"  # Кармічний баланс
KARMA_TRUST_IN_RULES = "trust_in_rules"  # Довіра до правил гри
KARMA_FUTURE_CONSIDERATION = "future_consideration"  # Гра врахує вибір у майбутньому

# Початковий стан карми
DEFAULT_KARMA = {
    KARMA_RULES_LEARNED: False,
    KARMA_DEBT_INFO: False,
    KARMA_HELPLESSNESS: False,
    KARMA_FEAR: 0,
    KARMA_CONTROL: 0,
    KARMA_VULNERABILITY: 0,
    KARMA_NEUTRAL_REACTION: 0,
    KARMA_TRUST: 0,
    KARMA_WORLD_HINT: 0,
    KARMA_TENSION: 0,
    KARMA_SUSPICION: 0,
    KARMA_HUMANITY: 0,
    KARMA_SYMPATHY: 0,
    KARMA_EMOTIONAL_TRUST: 0,
    KARMA_SOFT_PATH: False,
    KARMA_PASSIVE_BRANCH: False,
    KARMA_RESPONSIBILITY: 0,
    KARMA_GAME_WILL_REMEMBER: 0,
    KARMA_GAME_PROVOCATION: 0,
    KARMA_KARMA_BALANCE: 0,
    KARMA_TRUST_IN_RULES: 0,
    KARMA_FUTURE_CONSIDERATION: 0
}

# Ефекти карми для різних виборів
KARMA_EFFECTS = {
    "awakening_choice_3": {  # Закрити очі
        KARMA_FEAR: 1,
        KARMA_CONTROL: -1,
        KARMA_VULNERABILITY: 1
    },
    "meeting_choice_1": {  # Хто ти?
        KARMA_NEUTRAL_REACTION: 1,
        KARMA_TRUST: -1,
        KARMA_WORLD_HINT: 1
    },
    "meeting_choice_2": {  # Чому твої руки в крові?
        KARMA_TENSION: 1,
        KARMA_SUSPICION: 1,
        KARMA_HUMANITY: -1
    },
    "meeting_choice_3": {  # Я... радий, що я не сам.
        KARMA_SYMPATHY: 1,
        KARMA_EMOTIONAL_TRUST: 1,
        KARMA_SOFT_PATH: True
    },
    "meeting_choice_4": {  # Промовчати й просто кивнути
        KARMA_TRUST: 1,
        KARMA_PASSIVE_BRANCH: True
    },
    "meeting_second_choice_1": {  # Я піду.
        KARMA_RESPONSIBILITY: 1,
        KARMA_GAME_WILL_REMEMBER: 1
    },
    "meeting_second_choice_2": {  # Йди ти.
        KARMA_TRUST: -1,
        KARMA_GAME_PROVOCATION: 1
    },
    "meeting_second_choice_3": {  # Ми йдемо разом.
        KARMA_KARMA_BALANCE: 1,
        KARMA_TRUST_IN_RULES: -1,
        KARMA_FUTURE_CONSIDERATION: 1
    }
}

class KarmaSystem:
    def __init__(self):
        # Ініціалізуємо карму зі значеннями за замовчуванням
        self.karma = DEFAULT_KARMA.copy()
        # Лічильник для відстеження всіх виборів гравця
        self.choices_made = {}
        # Загальний рахунок карми
        self.karma_score = 0
        
    def record_choice(self, scene_id, choice_id):
        """Записує вибір гравця у конкретній сцені та застосовує ефекти карми"""
        if scene_id not in self.choices_made:
            self.choices_made[scene_id] = []
        self.choices_made[scene_id].append(choice_id)
        
        # Застосовуємо ефекти карми, якщо вони є
        choice_key = f"{scene_id}_choice_{choice_id}"
        if choice_key in KARMA_EFFECTS:
            for karma_type, value in KARMA_EFFECTS[choice_key].items():
                current_value = self.karma.get(karma_type, 0)
                self.karma[karma_type] = current_value + value
                
    def update_karma(self, karma_type, value=True):
        """Оновлює значення конкретного типу карми"""
        if karma_type in self.karma:
            old_value = self.karma[karma_type]
            self.karma[karma_type] = value
            
            # Оновлюємо загальний рахунок, якщо значення змінилося
            if old_value != value:
                self.calculate_karma_score()
                
    def get_karma(self, karma_type):
        """Отримує значення конкретного типу карми"""
        return self.karma.get(karma_type, False)
    
    def calculate_karma_score(self):
        """Розраховує загальний рахунок карми"""
        score = 0
        # Різні типи карми можуть мати різну вагу
        weights = {
            KARMA_RULES_LEARNED: 1,
            KARMA_DEBT_INFO: 2,
            KARMA_HELPLESSNESS: 3,
            KARMA_FEAR: 2,
            KARMA_CONTROL: 2,
            KARMA_VULNERABILITY: 2,
            KARMA_NEUTRAL_REACTION: 1,
            KARMA_TRUST: 3,
            KARMA_WORLD_HINT: 2,
            KARMA_TENSION: 2,
            KARMA_SUSPICION: 2,
            KARMA_HUMANITY: 3,
            KARMA_SYMPATHY: 2,
            KARMA_EMOTIONAL_TRUST: 3,
            KARMA_SOFT_PATH: 4,
            KARMA_PASSIVE_BRANCH: 4,
            KARMA_RESPONSIBILITY: 2,
            KARMA_GAME_WILL_REMEMBER: 2,
            KARMA_GAME_PROVOCATION: 2,
            KARMA_KARMA_BALANCE: 2,
            KARMA_TRUST_IN_RULES: 3,
            KARMA_FUTURE_CONSIDERATION: 3
        }
        
        for karma_type, value in self.karma.items():
            if isinstance(value, bool) and value:
                score += weights.get(karma_type, 1)
            elif isinstance(value, (int, float)):
                score += value * weights.get(karma_type, 1)
                
        self.karma_score = score
        return score
    
    def reset_karma(self):
        """Скидає карму до початкових значень"""
        self.karma = DEFAULT_KARMA.copy()
        self.choices_made = {}
        self.karma_score = 0

# Створюємо глобальний екземпляр системи карми
karma_system = KarmaSystem() 