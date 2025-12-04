class GameState:
    def __init__(self):
        self.reset()
    
    def reset(self):
        self._karma = 0
        self._choices = []
        self._current_scene = "main_menu"
        self._current_chapter = 1
        self._revealed_truths = set()
        self._hidden_truths = set()
        self._manipulation_level = 0
    
    def update_karma(self, value):
        self._karma += value
        return self._karma
    
    def get_karma(self):
        return self._karma
    
    def log_choice(self, choice):
        self._choices.append(choice)
    
    def get_choices(self):
        return self._choices.copy()
    
    def set_scene(self, scene):
        self._current_scene = scene
    
    def get_scene(self):
        return self._current_scene
    
    def set_chapter(self, chapter):
        self._current_chapter = chapter
    
    def get_chapter(self):
        return self._current_chapter
    
    def reveal_truth(self, truth):
        self._revealed_truths.add(truth)
        if truth in self._hidden_truths:
            self._hidden_truths.remove(truth)
    
    def hide_truth(self, truth):
        self._hidden_truths.add(truth)
    
    def get_revealed_truths(self):
        return self._revealed_truths.copy()
    
    def get_hidden_truths(self):
        return self._hidden_truths.copy()
    
    def increase_manipulation(self):
        self._manipulation_level += 1
    
    def get_manipulation_level(self):
        return self._manipulation_level

# Глобальний екземпляр для використання в інших файлах
game_state = GameState() 