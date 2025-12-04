# Not Your Game - Text Adventure (Graphical Version)

from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QLabel
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QPointF, QRectF, QPoint
from PyQt6.QtGui import QPainter, QColor, QFont, QRadialGradient, QBrush, QTextDocument, QPixmap, QFontDatabase
import sys
import math
import random
from game_state import game_state
from ui_style import UIStyle
from game_engine import game_engine
# Імпорт нових модулів
from scenes import get_scene_data, SCENE_PROLOGUE, SCENE_AWAKENING, SCENE_MEETING
from characters import get_character_from_text, CHARACTER_NARRATOR, CHARACTER_GIRL
from karma import karma_system, KARMA_RULES_LEARNED, KARMA_DEBT_INFO, KARMA_HELPLESSNESS

class PrologueWidget(QWidget):
    finished = pyqtSignal()

    def __init__(self, on_complete):
        super().__init__()
        self.on_complete = on_complete
        self.setStyleSheet("background: black;")
        
        # Отримуємо дані для прологу з модуля scenes
        scene_data = get_scene_data(SCENE_PROLOGUE)
        self.texts = scene_data["texts"]
        
        self.current_text_index = 0
        self.displayed_text = ""
        self.text_index = 0
        self.typewriter_timer = QTimer(self)
        self.typewriter_timer.timeout.connect(self.update_typewriter)
        self.pulse_phase = 0.0
        self.pulse_timer = QTimer(self)
        self.pulse_timer.timeout.connect(self.update_pulse)
        self.pulse_active = False
        self.pulse_strength = 0.0  # 0..1
        self.pulse_target = 0.0
        
        # Параметри для glitch-ефекту
        self.is_glitching = False
        self.glitch_intensity = 0.0
        self.glitch_target = 0.0
        self.text_copies = []  # Копії тексту для ефекту множення
        self.char_colors = []  # Кольори для кожної букви
        self.fade_to_black = 0.0  # Затемнення екрану (0-1)
        
        # Підказка про пропуск
        self.skip_hint = "Натисніть K щоб пропустити"
        self.show_skip_hint = True
        
        self.setMinimumSize(800, 600)
        self.finished.connect(self.on_complete)
        self.after_text_timer = None
        self.start_typewriter()
        
        # Встановлюємо фокус, щоб віджет отримував події клавіатури
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setFocus()

    def start_typewriter(self):
        self.displayed_text = ""
        self.text_index = 0
        self.typewriter_timer.start(20)  # Faster typing speed
        
        # Ініціалізувати кольори букв (білий для звичайного тексту)
        self.char_colors = []
        for i in range(len(self.texts[self.current_text_index])):
            self.char_colors.append(QColor("white"))

    def update_typewriter(self):
        text = self.texts[self.current_text_index]
        if self.text_index < len(text):
            self.displayed_text += text[self.text_index]
            self.text_index += 1
            self.update()
        else:
            self.typewriter_timer.stop()
            if self.current_text_index == 0:
                self.after_text_timer = QTimer(self)
                self.after_text_timer.setSingleShot(True)
                self.after_text_timer.timeout.connect(self.next_text)
                self.after_text_timer.start(2000)
            elif self.current_text_index == 1:
                # Другий текст: показати на 3 сек, потім очистити
                self.after_text_timer = QTimer(self)
                self.after_text_timer.setSingleShot(True)
                self.after_text_timer.timeout.connect(self.clear_second_text)
                self.after_text_timer.start(3000)
            else:
                # Текст "Починаємо..." повністю з'явився - починаємо глітч
                self.after_text_timer = QTimer(self)
                self.after_text_timer.setSingleShot(True)
                self.after_text_timer.timeout.connect(self.start_glitch)
                self.after_text_timer.start(500)

    def next_text(self):
        self.current_text_index += 1
        self.start_typewriter()
        
    def clear_second_text(self):
        # Очистити другий текст
        self.displayed_text = ""
        self.update()
        # Почати пульсацію через короткий проміжок після зникнення тексту
        self.after_text_timer = QTimer(self)
        self.after_text_timer.setSingleShot(True)
        self.after_text_timer.timeout.connect(self.start_pulse)
        self.after_text_timer.start(500)  # невелика пауза перед пульсацією

    def start_pulse(self):
        # Запустити пульс із плавним наростанням
        self.pulse_active = True
        self.pulse_strength = 0.0
        self.pulse_target = 1.0
        self.pulse_timer.start(30)
        # Після 4 секунд чистої пульсації - показати "Починаємо..."
        self.after_text_timer = QTimer(self)
        self.after_text_timer.setSingleShot(True)
        self.after_text_timer.timeout.connect(self.show_final_text)
        self.after_text_timer.start(4000)

    def show_final_text(self):
        # Посилити пульс, але зберегти характер віньєтки
        self.pulse_target = 1.2  # менше посилення, щоб не змінювати вигляд
        self.current_text_index = 2
        self.start_typewriter()
        self.update()
        
    def start_glitch(self):
        # Починаємо glitch ефект, посилюємо пульсацію
        self.is_glitching = True
        self.pulse_target = 1.5  # Сильніша пульсація
        self.glitch_intensity = 0.0
        self.glitch_target = 1.0
        
        # Створюємо 20 копій тексту для множення по всьому екрану
        self.text_copies = []
        for i in range(20):  # Збільшуємо до 20 копій
            self.text_copies.append({
                'text': self.displayed_text,
                'offset_x': 0,
                'offset_y': 0,
                'alpha': 0,
                'scale': random.uniform(0.7, 1.3),  # Різні розміри тексту
                'color': QColor("white")  # Починаємо з білого кольору
            })
            
        # Збільшуємо час глітчу до 7 секунд, щоб встигло почервоніти
        self.after_text_timer = QTimer(self)
        self.after_text_timer.setSingleShot(True)
        self.after_text_timer.timeout.connect(self.instant_fade_to_black)
        self.after_text_timer.start(7000)
    
    def instant_fade_to_black(self):
        # Миттєве затемнення
        self.fade_to_black = 1.0
        # Після короткої затримки переходимо до гри
        self.after_text_timer = QTimer(self)
        self.after_text_timer.setSingleShot(True)
        self.after_text_timer.timeout.connect(self.finish_prologue)
        self.after_text_timer.start(800)

    def finish_prologue(self):
        self.finished.emit()

    def update_pulse(self):
        # Оновлення пульсації без автоматичного вимкнення
        self.pulse_phase += 0.07
        step = 0.03
        if self.pulse_strength < self.pulse_target:
            self.pulse_strength = min(self.pulse_strength + step, self.pulse_target)
        elif self.pulse_strength > self.pulse_target:
            self.pulse_strength = max(self.pulse_strength - step, self.pulse_target)
            
        # Оновлення glitch-ефекту, якщо активний
        if self.is_glitching:
            # Поступово збільшуємо інтенсивність глітчу
            if self.glitch_intensity < self.glitch_target:
                self.glitch_intensity = min(self.glitch_intensity + 0.02, self.glitch_target)
                
            # Тремтіння та рандомне розміщення копій тексту по всьому екрану
            w, h = self.width(), self.height()
            for copy in self.text_copies:
                # Повністю рандомні позиції по всьому екрану
                copy['offset_x'] = random.randint(-w//2, w//2)
                copy['offset_y'] = random.randint(-h//2, h//2)
                copy['alpha'] = random.randint(40, 200) / 255.0
                
            # Поступово червоніємо букви - ПРИСКОРЮЄМО ЕФЕКТ
            for i in range(len(self.char_colors)):
                if random.random() < 0.15 * self.glitch_intensity:  # Збільшили ймовірність з 0.05 до 0.15
                    r = min(255, self.char_colors[i].red() + random.randint(10, 30))  # Збільшили швидкість червоніння
                    g = max(0, self.char_colors[i].green() - random.randint(10, 30))
                    b = max(0, self.char_colors[i].blue() - random.randint(10, 30))
                    self.char_colors[i] = QColor(r, g, b)
            
            # Також червонимо копії тексту
            for copy in self.text_copies:
                if random.random() < 0.2:  # 20% шанс зміни кольору за цикл
                    r = min(255, copy['color'].red() + random.randint(10, 30))
                    g = max(0, copy['color'].green() - random.randint(10, 30))
                    b = max(0, copy['color'].blue() - random.randint(10, 30))
                    copy['color'] = QColor(r, g, b)
        
        # Затемнення екрану, якщо активно
        if self.fade_to_black > 0:
            self.fade_to_black = min(1.0, self.fade_to_black + 0.02)
            
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        w, h = self.width(), self.height()
        painter.fillRect(0, 0, w, h, QColor(0, 0, 0))
        
        # Малюємо червону віньєтку
        if self.pulse_strength > 0.0:
            # Обмежуємо альфа-канал до 230, щоб уникнути перенасичення
            pulse_factor = 0.7 + 0.3 * (math.sin(self.pulse_phase) + 1) / 2
            max_alpha = min(230, int(200 * self.pulse_strength * pulse_factor))
            radius = int(math.sqrt(w * w + h * h) / 2)
            grad = QRadialGradient(w//2, h//2, radius)
            grad.setColorAt(0.0, QColor(255, 0, 0, 0))
            grad.setColorAt(0.6, QColor(255, 0, 0, int(max_alpha * 0.3)))
            grad.setColorAt(0.8, QColor(255, 0, 0, int(max_alpha * 0.7)))
            grad.setColorAt(1.0, QColor(255, 0, 0, max_alpha))
            painter.setBrush(grad)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRect(0, 0, w, h)
        
        # Малюємо текст
        if not self.is_glitching:
            # Звичайний текст
            painter.setPen(QColor("white"))
            font = QFont("Consolas", 28, QFont.Weight.Bold)
            painter.setFont(font)
            lines = self.displayed_text.split('\n')
            metrics = painter.fontMetrics()
            total_height = len(lines) * metrics.height()
            y = h//2 - total_height//2
            for line in lines:
                line_width = metrics.horizontalAdvance(line)
                painter.drawText(w//2 - line_width//2, y, line)
                y += metrics.height()
        else:
            # Глітч-ефект: малюємо копії тексту в рандомних місцях
            w, h = self.width(), self.height()
            for copy in self.text_copies:
                painter.setOpacity(copy['alpha'])
                painter.setPen(copy['color'])  # Використовуємо власний колір кожної копії
                size = int(28 * copy['scale'])
                font = QFont("Consolas", size, QFont.Weight.Bold)
                painter.setFont(font)
                
                # Малюємо рандомно розміщений текст
                x = w//2 + copy['offset_x']
                y = h//2 + copy['offset_y']
                
                # Переконуємося, що текст не виходить за межі екрану
                if x > 0 and x < w and y > 0 and y < h:
                    painter.drawText(int(x), int(y), self.displayed_text)
            
            # Додатково малюємо основний текст з червоніючими літерами
            painter.setOpacity(1.0)
            font = QFont("Consolas", 28, QFont.Weight.Bold)
            font.setLetterSpacing(QFont.SpacingType.AbsoluteSpacing, random.randint(-2, 2) * self.glitch_intensity)
            painter.setFont(font)
            lines = self.displayed_text.split('\n')
            metrics = painter.fontMetrics()
            total_height = len(lines) * metrics.height()
            y = h//2 - total_height//2
            
            # Додаємо невеликий зсув для тремтіння
            main_x_offset = random.randint(-5, 5) * self.glitch_intensity
            main_y_offset = random.randint(-5, 5) * self.glitch_intensity
            
            # Малюємо текст по буквах
            char_index = 0
            for line in lines:
                x = int(w//2 - metrics.horizontalAdvance(line) / 2 + main_x_offset)
                for char in line:
                    # Малюємо кожну букву окремо зі своїм кольором
                    if char_index < len(self.char_colors):
                        painter.setPen(self.char_colors[char_index])
                        width = metrics.horizontalAdvance(char)
                        painter.drawText(int(x), int(y + main_y_offset), char)
                        x += width
                    char_index += 1
                y += metrics.height()
        
        # Затемнення екрану, якщо активно
        if self.fade_to_black > 0:
            painter.setBrush(QColor(0, 0, 0, int(255 * self.fade_to_black)))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRect(0, 0, w, h)
            
        # Малюємо підказку про пропуск з ripple ефектом
        if self.show_skip_hint:
            # Ripple effect
            ripple_opacity = int(255 * (0.7 - (self.pulse_phase / 10)))
            ripple_color = QColor(255, 255, 255, ripple_opacity)
            painter.setBrush(ripple_color)
            painter.setPen(Qt.PenStyle.NoPen)
            ripple_radius = 10 + (self.pulse_phase * 5)
            ripple_x = w - 40 - ripple_radius
            ripple_y = h - 40 - ripple_radius
            painter.drawEllipse(QPointF(ripple_x + ripple_radius, ripple_y + ripple_radius), ripple_radius, ripple_radius)
            
            # Draw hint text
            painter.setPen(QColor(150, 150, 150, ripple_opacity))
            font = QFont("Consolas", 10)
            painter.setFont(font)
            hint_rect = QRectF(w - 200, h - 40, 180, 20)
            painter.drawText(hint_rect, Qt.AlignmentFlag.AlignRight, self.skip_hint)

    def keyPressEvent(self, event):
        print(f"Key pressed in prologue: {event.key()}")  # Додаємо для діагностики
        
        # Перевіряємо, чи натиснута клавіша K (може бути як англійською так і кирилицею)
        # Qt.Key.Key_K = 75, латинська K
        # Кирилична К також має свій код
        key = event.key()
        if key == Qt.Key.Key_K or key == 1050:  # 1050 - код для кириличної 'К'
            print("K key detected, skipping prologue")  # Додаємо для діагностики
            
            # Зупиняємо всі таймери
            if self.after_text_timer and self.after_text_timer.isActive():
                self.after_text_timer.stop()
            
            if self.typewriter_timer.isActive():
                self.typewriter_timer.stop()
                
            if self.pulse_timer.isActive():
                self.pulse_timer.stop()
            
            # Зупиняємо всі анімації та переходимо до наступної сцени
            self.fade_to_black = 1.0
            self.update()
            
            # Викликаємо фініш з затримкою для відображення затемнення
            QTimer.singleShot(300, self.finish_prologue)
        else:
            # Виклик батьківської реалізації для інших клавіш
            super().keyPressEvent(event)

class AwakeningWidget(QWidget):
    def __init__(self, on_complete):
        super().__init__()
        self.on_complete = on_complete
        self.setStyleSheet("background: black;")
        
        # Отримуємо дані для сцени пробудження з модуля scenes
        scene_data = get_scene_data(SCENE_AWAKENING)
        self.texts = scene_data["texts"]
        self.italic_texts = scene_data["italic_texts"]
        self.choice_texts = scene_data["choice_texts"]
        self.choice_italic_texts = scene_data.get("choice_italic_texts", {})
        self.graffiti_texts = scene_data.get("graffiti_texts", {})
        self.jumping_red_texts = scene_data.get("jumping_red_texts", {})
        self.choice_aftermath_texts = scene_data.get("choice_aftermath_texts", {})
        self.terminal_text = scene_data["terminal_text"]
        self.final_texts = scene_data.get("final_texts", [])  # Використовуємо пустий список як значення за замовчуванням
        self.awakening_title_time = scene_data["awakening_title_time"]
        self.karma_effects = scene_data.get("karma_effects", {})
        self.special_font_texts = scene_data.get("special_font_texts", {})
        
        # Отримуємо шрифт Blackraft з головного вікна
        main_window = QApplication.activeWindow()
        self.blackraft_font_family = main_window.blackraft_font_family if hasattr(main_window, 'blackraft_font_family') else None
        
        self.current_text_index = 0
        self.displayed_text = ""
        self.text_index = 0
        self.typewriter_timer = QTimer(self)
        self.typewriter_timer.timeout.connect(self.update_typewriter)
        self.ripple_active = False
        self.ripple_timer = QTimer(self)
        self.ripple_timer.timeout.connect(self.update_ripple)
        self.ripple_phase = 0
        
        # Choice buttons
        self.choice_buttons = []
        self.show_choices = False
        self.choice_made = None
        
        # Додаткові прапорці для нових елементів сцени
        self.showing_choice_italic = False
        self.showing_choice_special = False
        self.showing_choice_aftermath = False
        
        # Ефекти для спеціального тексту
        self.special_text_letters = []  # Зберігатиме параметри для кожної літери
        
        # Terminal mode
        self.terminal_mode = False
        self.terminal_text_displayed = ""
        self.terminal_text_index = 0
        
        # Final scene
        self.final_scene = False
        self.final_text_index = 0
        
        # Використовуємо карму з модуля karma
        self.karma = {
            KARMA_RULES_LEARNED: False,
            KARMA_DEBT_INFO: False,
            KARMA_HELPLESSNESS: False
        }
        
        self.setMinimumSize(800, 600)
        self.start_typewriter()

    def create_choice_buttons(self):
        # Create choice buttons
        self.choice_buttons = []
        
        # Отримуємо варіанти вибору з модуля scenes
        choices = get_scene_data(SCENE_AWAKENING)["choices"]
        
        button_height = 60
        button_width = 500
        start_y = (self.height() - (len(choices) * button_height + (len(choices) - 1) * 20)) // 2
        
        for i, choice_text in enumerate(choices):
            button = QPushButton(choice_text, self)
            button.setStyleSheet("""
                QPushButton {
                    background-color: #111;
                    color: white;
                    border: 1px solid #444;
                    padding: 10px;
                    font-size: 18px;
                    font-family: Consolas;
                }
                QPushButton:hover {
                    background-color: #333;
                    border: 1px solid #666;
                }
                QPushButton:pressed {
                    background-color: #555;
                }
            """)
            button.setGeometry((self.width() - button_width) // 2, 
                               start_y + i * (button_height + 20), 
                               button_width, button_height)
            button.clicked.connect(lambda checked, choice=i+1: self.make_choice(choice))
            self.choice_buttons.append(button)
            button.show()

    def make_choice(self, choice):
        # Hide all buttons
        for button in self.choice_buttons:
            button.hide()
        
        self.choice_made = choice
        self.show_choices = False
        self.ripple_active = False  # Reset ripple when making a choice
        
        # Start showing the choice result
        self.displayed_text = self.choice_texts[choice]
        self.update()
        
        # Записуємо ефекти карми, якщо є
        if choice in self.karma_effects:
            for effect, value in self.karma_effects[choice].items():
                print(f"Karma effect: {effect} = {value}")
        
        # Показуємо ripple для кліку
        self.show_ripple()

    def handle_after_choice_click(self):
        # Перевіряємо, чи є текст "aftermath" для вибору
        if self.choice_made in self.choice_aftermath_texts and not self.showing_choice_aftermath:
            self.showing_choice_aftermath = True
            self.displayed_text = self.choice_aftermath_texts[self.choice_made]
            self.update()
            self.show_ripple()
            return True
            
        # Перевіряємо, чи є курсивний текст для вибору
        elif self.choice_made in self.choice_italic_texts and not self.showing_choice_italic and self.showing_choice_aftermath:
            self.showing_choice_italic = True
            self.displayed_text = self.choice_italic_texts[self.choice_made]
            self.update()
            self.show_ripple()
            return True
            
        # Перевіряємо, чи є текст з ефектом стрибання для вибору
        elif self.choice_made in self.jumping_red_texts and not self.showing_choice_special and self.showing_choice_italic:
            self.showing_choice_special = True
            self.prepare_special_text(self.jumping_red_texts[self.choice_made])
            self.update()
            self.show_ripple()
            return True
            
        # Якщо всі тексти показано, переходимо до терміналу
        elif self.showing_choice_aftermath and self.showing_choice_italic:
            self.start_terminal()
            return True
            
        return False

    def prepare_special_text(self, text):
        self.displayed_text = text
        self.special_text_letters = []
        
        # Для кожної літери встановлюємо параметри
        for i in range(len(text)):
            self.special_text_letters.append({
                'offset_y': 0,
                'direction': random.choice([-1, 1]),
                'speed': random.uniform(0.2, 0.8)
            })
        
        # Запускаємо таймер для анімації тексту
        self.special_text_timer = QTimer(self)
        self.special_text_timer.timeout.connect(self.update_special_text)
        self.special_text_timer.start(50)  # Оновлюємо кожні 50 мс

    def update_special_text(self):
        # Оновлюємо параметри для кожної літери
        for letter in self.special_text_letters:
            # Змінюємо зсув з урахуванням напрямку та швидкості
            letter['offset_y'] += letter['direction'] * letter['speed']
            
            # Якщо зсув став занадто великим, міняємо напрямок
            if abs(letter['offset_y']) > 5:
                letter['direction'] *= -1
                
            # Іноді випадково міняємо напрямок
            if random.random() < 0.05:
                letter['direction'] *= -1
        
        self.update()  # Перемальовуємо віджет

    def start_terminal(self):
        # Зупиняємо таймер анімації спеціального тексту, якщо він активний
        if hasattr(self, 'special_text_timer') and self.special_text_timer.isActive():
            self.special_text_timer.stop()
        
        self.terminal_mode = True
        self.ripple_active = False
        self.ripple_timer.stop()
        self.terminal_text_displayed = ""
        self.terminal_text_index = 0
        
        # Start typewriter effect for terminal
        self.typewriter_timer.start(30)  # Faster typing for terminal
        self.update()

    def show_final_scene(self):
        # Оскільки final_texts тепер в іншій сцені, просто переходимо до наступної сцени
        self.on_complete()

    def start_final_typewriter(self):
        self.displayed_text = ""
        self.text_index = 0
        self.typewriter_timer.start(20)
        self.update()

    def update_typewriter(self):
        if self.terminal_mode:
            # Typewriter effect for terminal text
            terminal_text = self.terminal_text[self.choice_made]
            if self.terminal_text_index < len(terminal_text):
                self.terminal_text_displayed += terminal_text[self.terminal_text_index]
                self.terminal_text_index += 1
                self.update()
            else:
                self.typewriter_timer.stop()
                # Show ripple for user to click after terminal text is displayed
                self.show_ripple()
        elif self.final_scene:
            # Typewriter effect for final texts
            current_final_text = self.final_texts[self.final_text_index]
            if self.text_index < len(current_final_text):
                self.displayed_text += current_final_text[self.text_index]
                self.text_index += 1
                self.update()
            else:
                self.typewriter_timer.stop()
                # Show ripple for user to click
                self.show_ripple()
        else:
            # Normal text typewriter effect
            text = self.texts[self.current_text_index]
            if self.text_index < len(text):
                self.displayed_text += text[self.text_index]
                self.text_index += 1
                self.update()
            else:
                self.typewriter_timer.stop()
                if self.current_text_index == 0:
                    # For "Пробудження" text, clear it after 2 seconds and move to next
                    QTimer.singleShot(2000, self.clear_awakening_title)
                else:
                    # Show ripple immediately for other texts
                    self.show_ripple()

    def clear_awakening_title(self):
        # Clear the "Пробудження" title and move to next text
        self.displayed_text = ""
        self.update()
        self.current_text_index += 1
        self.start_typewriter()

    def displaying_italic_after_choice(self):
        return (self.choice_made in self.choice_italic_texts and 
                self.displayed_text == self.choice_italic_texts[self.choice_made])

    def mousePressEvent(self, event):
        if self.ripple_active and event.button() == Qt.MouseButton.LeftButton and not self.show_choices:
            self.ripple_timer.stop()  # Stop the current ripple animation
            self.ripple_active = False
            
            if self.terminal_mode:
                # After terminal text and click, go to final scene
                self.show_final_scene()
            elif self.final_scene:
                if self.final_text_index < len(self.final_texts) - 1:
                    self.final_text_index += 1
                    self.start_final_typewriter()
                else:
                    self.on_complete()
            elif self.choice_made:
                # Перевіряємо, чи потрібно показати додаткові тексти після вибору
                if not self.handle_after_choice_click():
                    # Якщо всі додаткові тексти показані, переходимо до терміналу
                    self.start_terminal()
            elif self.current_text_index < len(self.texts) - 1:
                self.current_text_index += 1
                self.start_typewriter()
            else:
                # Show choices when we reach the end of initial texts and click
                self.show_choice_buttons()

    def start_typewriter(self):
        self.displayed_text = ""
        self.text_index = 0
        self.typewriter_timer.start(20)  # Fast typing for all texts

    def keyPressEvent(self, event):
        # Handle key presses
        super().keyPressEvent(event)
        
        # Space to advance text when ripple is active
        if self.ripple_active and event.key() == Qt.Key.Key_Space:
            # Замість передачі None створюємо власну обробку без перевірки event.button()
            if self.terminal_mode:
                # After terminal text and click, go to final scene
                self.show_final_scene()
            elif self.final_scene:
                if self.final_text_index < len(self.final_texts) - 1:
                    self.final_text_index += 1
                    self.start_final_typewriter()
                else:
                    self.on_complete()
            elif self.choice_made:
                # Перевіряємо, чи потрібно показати додаткові тексти після вибору
                if not self.handle_after_choice_click():
                    # Якщо всі тексти показані, переходимо до терміналу
                    self.start_terminal()
            elif self.current_text_index < len(self.texts) - 1:
                self.current_text_index += 1
                self.start_typewriter()
            else:
                # Show choices when we reach the end of initial texts and click
                self.show_choice_buttons()

    def flash_terminal(self):
        # Flash the terminal screen and then show ripple for user to click
        self.update()
        self.show_ripple()

    def show_choice_buttons(self):
        # Clear displayed text before showing choices
        self.displayed_text = ""
        self.show_choices = True
        self.create_choice_buttons()
        self.update()

    def show_ripple(self):
        self.ripple_active = True
        self.ripple_timer.start(200)  # Update ripple every 200ms
        self.update()

    def update_ripple(self):
        self.ripple_phase = (self.ripple_phase % 5) + 1
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        w, h = self.width(), self.height()
        
        # Set background color
        if self.terminal_mode:
            # Terminal background (black)
            painter.fillRect(0, 0, w, h, QColor(0, 0, 0))
        else:
            # Regular background (black)
            painter.fillRect(0, 0, w, h, QColor(0, 0, 0))

        # Calculate maximum text width
        max_text_width = w - 60  # 30px padding on each side
        
        if self.terminal_mode:
            # Draw terminal text (green text on black)
            painter.setPen(QColor(0, 255, 0))  # Green terminal text
            font = QFont("Consolas", 20)
            painter.setFont(font)
            
            # Create text block for terminal text
            text_rect = QRectF(40, 40, w - 80, h - 80)
            painter.drawText(text_rect, Qt.AlignmentFlag.AlignLeft | Qt.TextFlag.TextWordWrap, self.terminal_text_displayed)
            
            # Draw blinking cursor at the end of text
            if int(self.ripple_phase) % 2 == 0:  # Blink effect
                metrics = painter.fontMetrics()
                last_line = self.terminal_text_displayed.split('\n')[-1]
                cursor_x = 40 + metrics.horizontalAdvance(last_line)
                cursor_y = 40 + (self.terminal_text_displayed.count('\n') * metrics.height())
                painter.drawText(cursor_x, cursor_y, "_")
        else:
            # Draw normal text
            if self.current_text_index == 0 and not self.final_scene and not self.choice_made:
                # Title - use larger font
                painter.setPen(QColor("white"))
                font = QFont("Consolas", 32, QFont.Weight.Bold)
                painter.setFont(font)
                text_rect = QRectF(30, 30, max_text_width, h - 60)
                painter.drawText(text_rect, Qt.AlignmentFlag.AlignCenter, self.displayed_text)
            else:
                # Визначаємо, чи потрібно малювати текст з ефектом стрибання букв
                is_jumping_text = (self.choice_made in self.jumping_red_texts and 
                                 self.displayed_text == self.jumping_red_texts[self.choice_made])
                
                # Визначаємо, чи потрібно малювати графіті
                is_graffiti = (self.choice_made in self.graffiti_texts and 
                              self.displayed_text == self.choice_texts[self.choice_made])
                
                text_to_display = self.displayed_text
                
                # Визначаємо персонажа за текстом
                character_id, clean_text = get_character_from_text(text_to_display)
                
                if is_jumping_text:
                    # Малюємо текст, що стрибає, червоним кольором
                    painter.setPen(QColor(255, 50, 50))  # Червоний колір
                    font = QFont("Consolas", 24)
                    painter.setFont(font)
                    
                    # Розбиваємо текст на слова
                    words = self.displayed_text.split()
                    metrics = painter.fontMetrics()
                    max_width = w - 80  # Відступи по 40 пікселів з боків
                    
                    # Формуємо рядки тексту
                    current_line = []
                    current_width = 0
                    x = 40  # Початковий відступ зліва
                    y = h // 2  # Вертикальне центрування
                    
                    for word in words:
                        word_width = metrics.horizontalAdvance(word + " ")
                        if current_width + word_width > max_width:
                            # Малюємо поточний рядок
                            line_text = " ".join(current_line)
                            line_width = metrics.horizontalAdvance(line_text)
                            text_x = (w - line_width) // 2
                            
                            for i, char in enumerate(line_text):
                                if i < len(self.special_text_letters):
                                    letter_y = int(y + self.special_text_letters[i]['offset_y'])
                                    char_width = metrics.horizontalAdvance(char)
                                    painter.drawText(text_x, letter_y, char)
                                    text_x += char_width
                            
                            # Переходимо на новий рядок
                            y += metrics.height()
                            current_line = [word]
                            current_width = word_width
                        else:
                            current_line.append(word)
                            current_width += word_width
                    
                    # Малюємо останній рядок
                    if current_line:
                        line_text = " ".join(current_line)
                        line_width = metrics.horizontalAdvance(line_text)
                        text_x = (w - line_width) // 2
                        
                        for i, char in enumerate(line_text):
                            if i < len(self.special_text_letters):
                                letter_y = int(y + self.special_text_letters[i]['offset_y'])
                                char_width = metrics.horizontalAdvance(char)
                                painter.drawText(text_x, letter_y, char)
                                text_x += char_width
                
                elif is_graffiti:
                    # Малюємо текст оповідача
                    painter.setPen(QColor("white"))
                    font = QFont("Consolas", 24)
                    if self.displaying_italic_after_choice():
                        font.setItalic(True)
                    painter.setFont(font)
                    
                    # Розділяємо текст оповідача на частини до і після згадки про графіті
                    narrator_text = "Оповідач: Ти обводиш поглядом кімнату. Прямокутне приміщення, приблизно 6 на 6 метрів. Камери в кутках. Дверей немає."
                    graffiti_mention = "На стіні - графіті: щось подряпане нігтями."
                    
                    # Малюємо першу частину тексту оповідача
                    text_rect = QRectF(30, 30, max_text_width, h/2 - 60)
                    painter.drawText(text_rect, Qt.AlignmentFlag.AlignCenter | Qt.TextFlag.TextWordWrap, narrator_text)
                    
                    # Малюємо графіті шрифтом Blackraft
                    if self.blackraft_font_family:
                        graffiti_font = QFont(self.blackraft_font_family, 72)  # Збільшуємо розмір шрифту
                        painter.setFont(graffiti_font)
                        painter.setPen(QColor(200, 0, 0))  # Червоний колір для графіті
                    else:
                        graffiti_font = QFont("Consolas", 72, QFont.Weight.Bold)
                        painter.setFont(graffiti_font)
                    
                    graffiti_text = self.graffiti_texts[self.choice_made]
                    graffiti_width = painter.fontMetrics().horizontalAdvance(graffiti_text)
                    painter.drawText(QPoint((w - graffiti_width) // 2, int(h/2) + 20), graffiti_text)
                    
                    # Малюємо другу частину тексту оповідача
                    painter.setPen(QColor("white"))
                    font = QFont("Consolas", 24)
                    painter.setFont(font)
                    text_rect = QRectF(30, int(h/2) + 80, max_text_width, int(h/2) - 60)
                    painter.drawText(text_rect, Qt.AlignmentFlag.AlignCenter | Qt.TextFlag.TextWordWrap, graffiti_mention)
                elif character_id == CHARACTER_NARRATOR or character_id == CHARACTER_GIRL:
                    # Знаходимо дані персонажа
                    prefix = ""
                    prefix_color = QColor(255, 255, 255)  # Білий за замовчуванням
                    
                    if character_id == CHARACTER_NARRATOR:
                        prefix = "Оповідач: "
                        prefix_color = QColor(0, 255, 0)  # Зелений
                    elif character_id == CHARACTER_GIRL:
                        prefix = "Дівчина: "
                        prefix_color = QColor(255, 100, 100)  # Рожево-червоний
                    
                    # Малюємо текст з префіксом у кольорі
                    formatted_text = f"<span style='color:{prefix_color.name()};'>{prefix}</span>{clean_text}"
                    
                    # Налаштовуємо шрифт
                    font = QFont("Consolas", 24)
                    if self.displaying_italic_after_choice():
                        font.setItalic(True)
                    
                    # Використовуємо rich text для відображення тексту з префіксом
                    document = QTextDocument()
                    document.setDefaultFont(font)
                    document.setHtml(formatted_text)
                    document.setTextWidth(max_text_width)
                    
                    # Центруємо текст
                    painter.save()
                    painter.translate((w - document.idealWidth()) / 2, 30)
                    document.drawContents(painter)
                    painter.restore()
                else:
                    # Звичайний текст без префіксу
                    painter.setPen(QColor("white"))
                    font = QFont("Consolas", 24)
                    if self.displaying_italic_after_choice():
                        font.setItalic(True)
                    painter.setFont(font)
                    text_rect = QRectF(30, 30, max_text_width, h - 60)
                    painter.drawText(text_rect, Qt.AlignmentFlag.AlignCenter | Qt.TextFlag.TextWordWrap, text_to_display)

        # Draw ripple effect
        if self.ripple_active and not self.show_choices:
            # Ripple effect to indicate user can click to continue
            painter.setPen(Qt.PenStyle.NoPen)
            ripple_opacity = int(255 * (0.7 - (self.ripple_phase / 10)))
            ripple_color = QColor(255, 255, 255, ripple_opacity)
            painter.setBrush(ripple_color)
            ripple_radius = 10 + (self.ripple_phase * 5)
            ripple_x = w - 40 - ripple_radius
            ripple_y = h - 40 - ripple_radius
            painter.drawEllipse(ripple_x, ripple_y, ripple_radius * 2, ripple_radius * 2)
            
            # Draw hint text
            hint_text = "Клацніть, щоб продовжити..."
            painter.setPen(QColor(150, 150, 150, ripple_opacity))
            font = QFont("Consolas", 10)
            painter.setFont(font)
            hint_rect = QRectF(w - 200, h - 40, 180, 20)
            painter.drawText(hint_rect, Qt.AlignmentFlag.AlignRight, hint_text)

class GlitchTitleLabel(QWidget):
    def __init__(self, parent=None, custom_font_family=None):
        super().__init__(parent)
        self.setText("NOT YOUR GAME")
        self.glitch_timer = QTimer(self)
        self.glitch_timer.timeout.connect(self.update_glitch)
        self.glitch_timer.start(50)  # Оновлення кожні 50 мс
        self.glitch_intensity = 0.0
        self.glitch_direction = 0.02
        self.glitch_offset_x = 0
        self.glitch_offset_y = 0
        self.lines = []  # Горизонтальні лінії для ефекту перешкод
        self.setMinimumHeight(240)  # Збільшена висота для більшого тексту
        self.char_noise = {}  # Шум для кожної літери
        self.update_char_noise()  # Ініціалізуємо шум для літер
        self.custom_font_family = custom_font_family
        
    def setText(self, text):
        self.text = text
        self.update_char_noise()
        self.update()
        
    def update_char_noise(self):
        # Створюємо випадковий шум для кожної літери тексту
        self.char_noise = {}
        for i in range(len(self.text)):
            # Кожна літера має свою текстуру з "цифрового шуму"
            noise_pattern = []
            for _ in range(20):  # 20 точок шуму на літеру
                x = random.random()  # Відносна позиція X в літері (0-1)
                y = random.random()  # Відносна позиція Y в літері (0-1)
                alpha = random.randint(50, 150)  # Прозорість
                noise_pattern.append((x, y, alpha))
            self.char_noise[i] = noise_pattern
        
    def update_glitch(self):
        # Змінюємо інтенсивність глітчу
        self.glitch_intensity += self.glitch_direction
        if self.glitch_intensity > 0.4:
            self.glitch_direction = -0.02
        elif self.glitch_intensity < 0.05:
            self.glitch_direction = 0.02
            
        # Рандомні зсуви для тексту
        self.glitch_offset_x = random.randint(-3, 3) if random.random() < self.glitch_intensity * 0.5 else 0
        self.glitch_offset_y = random.randint(-2, 2) if random.random() < self.glitch_intensity * 0.5 else 0
        
        # Генеруємо нові лінії для ефекту перешкод
        self.lines = []
        num_lines = int(10 * self.glitch_intensity)
        height = self.height()
        for _ in range(num_lines):
            y = random.randint(0, height)
            width = random.randint(10, self.width() // 2)
            x = random.randint(0, self.width() - width)
            alpha = random.randint(40, 160)
            self.lines.append((x, y, width, alpha))
            
        # Періодично оновлюємо шум для символів
        if random.random() < 0.1:  # 10% шанс оновити шум
            self.update_char_noise()
            
        self.update()
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        w, h = self.width(), self.height()
        
        # Фон - чорний
        painter.fillRect(0, 0, w, h, QColor(0, 0, 0))
        
        # Малюємо лінії перешкод (горизонтальні лінії)
        for x, y, width, alpha in self.lines:
            painter.fillRect(x, y, width, 1, QColor(0, 255, 0, alpha))
            
        # Налаштовуємо шрифт (збільшуємо розмір)
        if self.custom_font_family:
            # Використовуємо власний шрифт, якщо він доступний
            font = QFont(self.custom_font_family, 60, QFont.Weight.Normal)  # Збільшений розмір, нормальна жирність
        else:
            # Використовуємо стандартний шрифт як запасний варіант
            font = QFont("Consolas", 60, QFont.Weight.Normal)  # Збільшений розмір, нормальна жирність
            
        font.setLetterSpacing(QFont.SpacingType.AbsoluteSpacing, 2)  # Збільшуємо відстань між символами
        painter.setFont(font)
        
        # Додаємо цифровий шум (вертикальні лінії для ефекту екрану)
        for i in range(0, w, 2):
            if random.random() < 0.05:
                alpha = random.randint(5, 20)
                painter.fillRect(i, 0, 1, h, QColor(0, 255, 0, alpha))
        
        # Отримуємо розміри тексту для центрування
        fm = painter.fontMetrics()
        text_width = fm.horizontalAdvance(self.text)
        text_height = fm.height()
        text_x = (w - text_width) // 2
        text_y = (h - text_height) // 2 + fm.ascent()
        
        # Визначаємо центр тексту для радіального розсіювання
        text_center_x = text_x + text_width / 2
        text_center_y = text_y - text_height / 2
        
        # Ефект світіння (glow) для тексту
        glow_steps = 4
        for i in range(glow_steps):
            alpha = 40 - i * 10  # Зменшуємо прозорість для зовнішніх шарів
            offset = int(i * 1.5)  # Збільшуємо зсув для зовнішніх шарів, перетворюємо у int
            
            # Рендеримо текст з ефектом розмиття
            glow_color = QColor(0, 255, 0, alpha)
            painter.setPen(glow_color)
            
            # Малюємо кілька копій тексту зі зсувами для ефекту світіння
            # Переконуємось, що координати цілі числа (int)
            painter.drawText(int(text_x - offset), int(text_y), self.text)
            painter.drawText(int(text_x + offset), int(text_y), self.text)
            painter.drawText(int(text_x), int(text_y - offset), self.text)
            painter.drawText(int(text_x), int(text_y + offset), self.text)
        
        # Малюємо текст з ефектом глітчу та хроматичної аберації
        # Додаємо зсуви у різні боки для ефекту неправильного відображення
        for i in range(3):
            if i == 0:
                offset_x, offset_y = -2, 0
                color = QColor(255, 0, 0, 60)  # Червоний канал
            elif i == 1:
                offset_x, offset_y = 2, 0
                color = QColor(0, 0, 255, 60)  # Синій канал
            else:
                offset_x, offset_y = self.glitch_offset_x, self.glitch_offset_y
                color = QColor(150, 255, 150, 230)  # Основний колір - світло-зелений
                
            painter.setPen(color)
            
            # Малюємо текст посимвольно для додавання шуму/текстури
            for j, char in enumerate(self.text):
                char_width = fm.horizontalAdvance(char)
                # Перетворюємо координати у int
                char_x = int(text_x + fm.horizontalAdvance(self.text[:j]) + offset_x)
                char_y = int(text_y + offset_y)
                
                # Малюємо літеру
                painter.drawText(char_x, char_y, char)
                
                # Додаємо текстуру/шум до літери
                if j in self.char_noise:
                    for x_rel, y_rel, alpha in self.char_noise[j]:
                        # Перетворюємо координати у int
                        noise_x = int(char_x + x_rel * char_width)
                        noise_y = int(char_y - text_height + y_rel * text_height)
                        painter.setPen(QColor(200, 255, 200, alpha))
                        painter.drawPoint(noise_x, noise_y)
                
                # Випадково додаємо дефекти до деяких літер
                if random.random() < 0.2 * self.glitch_intensity:
                    defect_height = random.randint(1, 3)
                    defect_y = int(char_y - random.randint(0, text_height))
                    painter.setPen(QColor(0, 255, 0, 120))
                    painter.drawLine(char_x, defect_y, char_x + char_width, defect_y)
            
        # Додаємо горизонтальні скан-лінії для ефекту старого екрану
        for y in range(0, h, 2):
            painter.fillRect(0, y, w, 1, QColor(0, 0, 0, 30))
            
        # Додаємо стриманий радіальний ефект розсіювання
        # Ефект круговий - частинки розходяться по колу на однакову відстань від центру
        pixel_count = 200  # Зменшуємо кількість частинок
        
        # Визначаємо максимальний радіус кола розсіювання
        max_radius = min(text_width, text_height) * 0.7  # Радіус кола
        
        # Малюємо кілька кіл з частинками
        circle_counts = [80, 60, 40, 20]  # Кількість частинок на кожному колі
        circle_radii = [max_radius * 0.4, max_radius * 0.6, max_radius * 0.8, max_radius]  # Радіуси кіл
        
        for radius, count in zip(circle_radii, circle_counts):
            # Для кожного кола рівномірно розміщуємо точки
            for i in range(count):
                # Рівномірне розміщення по колу
                angle = 2 * math.pi * i / count
                
                # Додаємо невелику випадкову варіацію
                angle_variation = random.uniform(-0.05, 0.05)
                radius_variation = random.uniform(-2, 2)
                
                # Обчислюємо координати частинки на колі
                x = text_center_x + (radius + radius_variation) * math.cos(angle + angle_variation)
                y = text_center_y + (radius + radius_variation) * math.sin(angle + angle_variation)
                
                # Прозорість залежить від радіуса - чим далі, тим прозоріша
                alpha = max(20, int(100 - (radius / max_radius) * 80))
                
                # Колір - зелений з варіаціями
                green = random.randint(180, 255)
                color = QColor(20, green, 40, alpha)
                
                # Розмір частинки - маленькі точки
                size = 1 if random.random() < 0.7 else 2
                
                # Малюємо частинку
                painter.setPen(color)
                if size == 1:
                    painter.drawPoint(int(x), int(y))
                else:
                    painter.drawEllipse(int(x) - 1, int(y) - 1, 2, 2)

class GlitchBackgroundWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.glitch_timer = QTimer(self)
        self.glitch_timer.timeout.connect(self.update_glitch)
        self.glitch_timer.start(50)  # Оновлення кожні 50 мс
        self.glitch_intensity = 0.0
        self.glitch_direction = 0.02
        self.lines = []  # Горизонтальні лінії для ефекту перешкод
        self.vertical_lines = []  # Вертикальні лінії
        self.flicker_alpha = 255  # Альфа-канал для ефекту мерехтіння
        
    def update_glitch(self):
        # Змінюємо інтенсивність глітчу
        self.glitch_intensity += self.glitch_direction
        if self.glitch_intensity > 0.4:
            self.glitch_direction = -0.02
        elif self.glitch_intensity < 0.05:
            self.glitch_direction = 0.02
            
        # Генеруємо нові лінії для ефекту перешкод
        self.lines = []
        num_lines = int(15 * self.glitch_intensity)
        height = self.height()
        width = self.width()
        
        for _ in range(num_lines):
            y = random.randint(0, height)
            line_width = random.randint(10, width // 2)
            x = random.randint(0, width - line_width)
            alpha = random.randint(20, 120)
            self.lines.append((x, y, line_width, alpha))
            
        # Генеруємо вертикальні лінії
        self.vertical_lines = []
        num_vlines = int(10 * self.glitch_intensity)
        
        for _ in range(num_vlines):
            x = random.randint(0, width)
            line_height = random.randint(10, height // 3)
            y = random.randint(0, height - line_height)
            alpha = random.randint(20, 100)
            self.vertical_lines.append((x, y, line_height, alpha))
            
        # Ефект мерехтіння (рідкісне миготіння екрану)
        if random.random() < 0.03:  # 3% шанс на миготіння
            self.flicker_alpha = random.randint(200, 255)
        else:
            self.flicker_alpha = 255
            
        self.update()
        
    def paintEvent(self, event):
        painter = QPainter(self)
        
        w, h = self.width(), self.height()
        
        # Фон - чорний з ефектом миготіння
        painter.fillRect(0, 0, w, h, QColor(0, 0, 0, self.flicker_alpha))
        
        # Малюємо горизонтальні лінії перешкод
        for x, y, width, alpha in self.lines:
            painter.fillRect(x, y, width, 1, QColor(0, 255, 0, alpha))
            
        # Малюємо вертикальні лінії перешкод
        for x, y, height, alpha in self.vertical_lines:
            painter.fillRect(x, y, 1, height, QColor(0, 255, 0, alpha))
            
        # Додаємо скан-лінії для ефекту ЕПТ-монітора
        for y in range(0, h, 4):
            painter.fillRect(0, y, w, 1, QColor(0, 0, 0, 20))
            
        # Додаємо цифровий шум (вертикальні лінії для ефекту екрану)
        for i in range(0, w, 3):
            if random.random() < 0.03:
                alpha = random.randint(5, 15)
                painter.fillRect(i, 0, 1, h, QColor(0, 255, 0, alpha))

class MeetingWidget(QWidget):
    def __init__(self, on_complete):
        super().__init__()
        self.on_complete = on_complete
        self.setStyleSheet("background: black;")
        
        # Отримуємо дані для сцени зустрічі з модуля scenes
        scene_data = get_scene_data(SCENE_MEETING)
        self.texts = scene_data["texts"]
        self.italic_texts = scene_data.get("italic_texts", [])
        self.choice_texts = scene_data.get("choice_texts", {})
        self.choice_aftermath_texts = scene_data.get("choice_aftermath_texts", {})
        self.choices = scene_data.get("choices", [])
        self.karma_effects = scene_data.get("karma_effects", {})
        self.terminal_texts = scene_data.get("terminal_text", {})
        self.second_choices = scene_data.get("second_choices", [])
        self.second_choice_texts = scene_data.get("second_choice_texts", {})
        self.second_choice_aftermath_texts = scene_data.get("second_choice_aftermath_texts", {})
        
        # Отримуємо шрифт Blackraft з головного вікна
        main_window = QApplication.activeWindow()
        self.blackraft_font_family = main_window.blackraft_font_family if hasattr(main_window, 'blackraft_font_family') else None
        
        self.current_text_index = 0
        self.displayed_text = ""
        self.text_index = 0
        self.typewriter_timer = QTimer(self)
        self.typewriter_timer.timeout.connect(self.update_typewriter)
        self.ripple_active = False
        self.ripple_timer = QTimer(self)
        self.ripple_timer.timeout.connect(self.update_ripple)
        self.ripple_phase = 0
        
        # Choice buttons
        self.choice_buttons = []
        self.show_choices = False
        self.choice_made = None
        self.second_choice_buttons = []
        self.showing_second_choices = False
        self.second_choice_made = None
        self.second_phase_started = False
        self.awaiting_second_choice_prompt_ack = False
        self.second_choice_aftermath_shown = False
        
        # Додаткові прапорці для нових елементів сцени
        self.showing_choice_aftermath = False
        
        self.setMinimumSize(800, 600)
        self.start_typewriter()

    def create_choice_buttons(self):
        # Create choice buttons
        self.choice_buttons = []
        
        button_height = 60
        button_width = 500
        start_y = (self.height() - (len(self.choices) * button_height + (len(self.choices) - 1) * 20)) // 2
        
        for i, choice_text in enumerate(self.choices):
            button = QPushButton(choice_text, self)
            button.setStyleSheet("""
                QPushButton {
                    background-color: #111;
                    color: white;
                    border: 1px solid #444;
                    padding: 10px;
                    font-size: 18px;
                    font-family: Consolas;
                }
                QPushButton:hover {
                    background-color: #333;
                    border: 1px solid #666;
                }
                QPushButton:pressed {
                    background-color: #555;
                }
            """)
            button.setGeometry((self.width() - button_width) // 2, 
                               start_y + i * (button_height + 20), 
                               button_width, button_height)
            button.clicked.connect(lambda checked, choice=i+1: self.make_choice(choice))
            self.choice_buttons.append(button)
            button.show()

    def create_second_choice_buttons(self):
        # Create buttons for the second dialogue stage
        self.second_choice_buttons = []
        
        if not self.second_choices:
            return
        
        button_height = 60
        button_width = 500
        start_y = (self.height() - (len(self.second_choices) * button_height + (len(self.second_choices) - 1) * 20)) // 2
        
        for i, choice_text in enumerate(self.second_choices):
            button = QPushButton(choice_text, self)
            button.setStyleSheet("""
                QPushButton {
                    background-color: #111;
                    color: white;
                    border: 1px solid #444;
                    padding: 10px;
                    font-size: 18px;
                    font-family: Consolas;
                }
                QPushButton:hover {
                    background-color: #333;
                    border: 1px solid #666;
                }
                QPushButton:pressed {
                    background-color: #555;
                }
            """)
            button.setGeometry((self.width() - button_width) // 2, 
                               start_y + i * (button_height + 20), 
                               button_width, button_height)
            button.clicked.connect(lambda checked, choice=i+1: self.make_second_choice(choice))
            self.second_choice_buttons.append(button)
            button.show()

    def make_choice(self, choice):
        # Hide all buttons
        for button in self.choice_buttons:
            button.hide()
        
        self.choice_made = choice
        self.show_choices = False
        self.ripple_active = False  # Reset ripple when making a choice
        
        # Start showing the choice result
        self.displayed_text = self.choice_texts[choice]
        self.update()
        
        # Записуємо вибір до karma_system
        karma_system.record_choice(SCENE_MEETING, choice)
        
        # Показуємо ripple для кліку
        self.show_ripple()

    def make_second_choice(self, choice):
        for button in self.second_choice_buttons:
            button.hide()
        
        self.second_choice_buttons = []
        self.showing_second_choices = False
        self.second_choice_made = choice
        self.second_choice_aftermath_shown = False
        
        self.displayed_text = self.second_choice_texts.get(choice, "")
        self.update()
        
        karma_system.record_choice(f"{SCENE_MEETING}_second", choice)
        
        self.show_ripple()

    def handle_after_choice_click(self):
        # Перевіряємо, чи є текст "aftermath" для вибору
        if self.choice_made in self.choice_aftermath_texts and not self.showing_choice_aftermath:
            self.showing_choice_aftermath = True
            self.displayed_text = self.choice_aftermath_texts[self.choice_made]
            self.update()
            self.show_ripple()
            return True
            
        return False

    def handle_second_choice_after_click(self):
        if (
            self.second_choice_made in self.second_choice_aftermath_texts
            and not self.second_choice_aftermath_shown
        ):
            self.second_choice_aftermath_shown = True
            self.displayed_text = self.second_choice_aftermath_texts[self.second_choice_made]
            self.update()
            self.show_ripple()
            return True
        return False
    
    def start_second_phase(self):
        if self.second_phase_started:
            return
        
        self.second_phase_started = True
        self.choice_made = None  # Завершили перший набір виборів
        
        if not self.second_choices:
            self.finish_meeting()
            return
        
        prompt_text = self.terminal_texts.get("test_choice", "")
        if prompt_text:
            self.displayed_text = prompt_text
            self.awaiting_second_choice_prompt_ack = True
            self.show_ripple()
        else:
            self.show_second_choice_buttons()

    def mousePressEvent(self, event):
        if (
            self.ripple_active 
            and event.button() == Qt.MouseButton.LeftButton 
            and not self.show_choices
            and not self.showing_second_choices
        ):
            self.ripple_timer.stop()  # Stop the current ripple animation
            self.ripple_active = False
            self.advance_scene_flow()
        # Додаємо можливість миттєво показати весь текст при кліку під час друкування
        elif self.typewriter_timer.isActive() and event.button() == Qt.MouseButton.LeftButton:
            # Зупиняємо таймер друкування
            self.typewriter_timer.stop()
            
            # Відображаємо весь текст одразу
            self.displayed_text = self.texts[self.current_text_index]
            self.text_index = len(self.texts[self.current_text_index])
            
            self.update()
            
            # Показуємо ripple, щоб можна було продовжити
            if self.current_text_index == 0:
                # Для заголовка очищаємо його через 2 секунди і переходимо до наступного
                QTimer.singleShot(2000, self.clear_title)
            else:
                # Для інших текстів відразу показуємо ripple
                self.show_ripple()

    def start_typewriter(self):
        self.displayed_text = ""
        self.text_index = 0
        self.typewriter_timer.start(20)  # Fast typing for all texts

    def keyPressEvent(self, event):
        # Handle key presses
        super().keyPressEvent(event)
        
        # Space to advance text when ripple is active
        if (
            self.ripple_active 
            and event.key() == Qt.Key.Key_Space
            and not self.show_choices
            and not self.showing_second_choices
        ):
            self.ripple_timer.stop()
            self.ripple_active = False
            self.advance_scene_flow()

    def show_choice_buttons(self):
        # Clear displayed text before showing choices
        self.displayed_text = ""
        self.show_choices = True
        self.create_choice_buttons()
        self.update()
    
    def show_second_choice_buttons(self):
        self.displayed_text = ""
        self.show_choices = False
        self.showing_second_choices = True
        self.awaiting_second_choice_prompt_ack = False
        self.create_second_choice_buttons()
        self.update()

    def show_ripple(self):
        self.ripple_active = True
        self.ripple_timer.start(200)  # Update ripple every 200ms
        self.update()

    def update_ripple(self):
        self.ripple_phase = (self.ripple_phase % 5) + 1
        self.update()
    
    def finish_meeting(self):
        self.on_complete()

    def advance_scene_flow(self):
        if self.choice_made is not None:
            if not self.handle_after_choice_click():
                self.start_second_phase()
        elif self.second_choice_made is not None:
            if not self.handle_second_choice_after_click():
                self.finish_meeting()
        elif self.second_phase_started:
            if self.awaiting_second_choice_prompt_ack:
                self.awaiting_second_choice_prompt_ack = False
            self.show_second_choice_buttons()
        elif self.current_text_index < len(self.texts) - 1:
            self.current_text_index += 1
            self.start_typewriter()
        else:
            self.show_choice_buttons()

    def update_typewriter(self):
        # Normal text typewriter effect
        text = self.texts[self.current_text_index]
        if self.text_index < len(text):
            self.displayed_text += text[self.text_index]
            self.text_index += 1
            self.update()
        else:
            self.typewriter_timer.stop()
            if self.current_text_index == 0:
                # For title text, clear it after 2 seconds and move to next
                QTimer.singleShot(2000, self.clear_title)
            else:
                # Show ripple immediately for other texts
                self.show_ripple()

    def clear_title(self):
        # Clear the title and move to next text
        self.displayed_text = ""
        self.update()
        self.current_text_index += 1
        self.start_typewriter()

    def paintEvent(self, event):
        painter = QPainter(self)
        w, h = self.width(), self.height()
        
        # Set background color
        painter.fillRect(0, 0, w, h, QColor(0, 0, 0))

        # Calculate maximum text width
        max_text_width = w - 60  # 30px padding on each side
        
        # Draw normal text
        if self.current_text_index == 0 and not self.choice_made:
            # Title - use larger font
            painter.setPen(QColor("white"))
            font = QFont("Consolas", 32, QFont.Weight.Bold)
            painter.setFont(font)
            text_rect = QRectF(30, 30, max_text_width, h - 60)
            painter.drawText(text_rect, Qt.AlignmentFlag.AlignCenter, self.displayed_text)
        else:
            text_to_display = self.displayed_text
            
            # Визначаємо персонажа за текстом
            character_id, clean_text = get_character_from_text(text_to_display)
            
            # Перевіряємо чи текст має бути курсивом
            is_italic = text_to_display in self.italic_texts
            
            # Визначаємо колір та стиль тексту в залежності від персонажа
            if character_id == CHARACTER_NARRATOR or character_id == CHARACTER_GIRL:
                # Знаходимо дані персонажа
                prefix = ""
                prefix_color = QColor(255, 255, 255)  # Білий за замовчуванням
                
                if character_id == CHARACTER_NARRATOR:
                    prefix = "Оповідач: "
                    prefix_color = QColor(0, 255, 0)  # Зелений
                elif character_id == CHARACTER_GIRL:
                    prefix = "Дівчина: "
                    prefix_color = QColor(255, 100, 100)  # Рожево-червоний
                
                # Малюємо текст з префіксом у кольорі
                formatted_text = f"<span style='color:{prefix_color.name()};'>{prefix}</span>{clean_text}"
                
                # Налаштовуємо шрифт
                font = QFont("Consolas", 18)
                if is_italic:
                    font.setItalic(True)
                
                # Використовуємо rich text для відображення тексту з префіксом
                document = QTextDocument()
                document.setDefaultFont(font)
                document.setHtml(formatted_text)
                document.setTextWidth(max_text_width)
                
                # Центруємо текст
                painter.save()
                painter.translate((w - document.idealWidth()) / 2, 30)
                document.drawContents(painter)
                painter.restore()
            else:
                # Звичайний текст або курсив
                painter.setPen(QColor(200, 200, 200))
                font = QFont("Consolas", 18)
                font.setItalic(is_italic)
                painter.setFont(font)
                text_rect = QRectF(40, h // 2 - 100, max_text_width, 200)
                painter.drawText(text_rect, Qt.AlignmentFlag.AlignCenter | Qt.TextFlag.TextWordWrap, text_to_display)
        
        # Draw ripple if active
        if self.ripple_active:
            # Ripple effect to indicate user can click to continue
            painter.setPen(Qt.PenStyle.NoPen)
            ripple_opacity = int(255 * (0.7 - (self.ripple_phase / 10)))
            ripple_color = QColor(255, 255, 255, ripple_opacity)
            painter.setBrush(ripple_color)
            ripple_radius = 10 + (self.ripple_phase * 5)
            ripple_x = w - 40 - ripple_radius
            ripple_y = h - 40 - ripple_radius
            painter.drawEllipse(ripple_x, ripple_y, ripple_radius * 2, ripple_radius * 2)
            
            # Draw hint text
            hint_text = "Клацніть, щоб продовжити..."
            painter.setPen(QColor(150, 150, 150, ripple_opacity))
            font = QFont("Consolas", 10)
            painter.setFont(font)
            hint_rect = QRectF(w - 200, h - 40, 180, 20)
            painter.drawText(hint_rect, Qt.AlignmentFlag.AlignRight, hint_text)

class GameApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Not Your Game")
        self.setGeometry(100, 100, 800, 600)
        self.current_scene = None
        
        # Завантажуємо власні шрифти
        self.custom_font_id = None
        self.blackraft_font_id = None
        self.load_custom_fonts()
        
        self.show_main_menu()
        
        # Встановлюємо фокус для отримання подій клавіатури
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

    def load_custom_fonts(self):
        # Шлях до файлів шрифтів
        glitch_font_path = "assets/fonts/SDGlitch_Demo.ttf"
        blackraft_font_path = "assets/fonts/Blackraft.ttf"
        
        try:
            print(f"Спроба завантажити шрифти з:")
            print(f"Glitch: {glitch_font_path}")
            print(f"Blackraft: {blackraft_font_path}")
            
            # Завантажуємо glitch шрифт
            self.custom_font_id = QFontDatabase.addApplicationFont(glitch_font_path)
            if self.custom_font_id != -1:
                font_families = QFontDatabase.applicationFontFamilies(self.custom_font_id)
                if font_families:
                    self.custom_font_family = font_families[0]
                    print(f"Glitch шрифт успішно завантажено: {self.custom_font_family}")
                else:
                    print("Помилка: Не вдалось отримати назву glitch шрифту")
                    self.custom_font_family = None
            else:
                print(f"Помилка: Не вдалося завантажити glitch шрифт з {glitch_font_path}")
                self.custom_font_family = None

            # Завантажуємо Blackraft шрифт
            self.blackraft_font_id = QFontDatabase.addApplicationFont(blackraft_font_path)
            print(f"Blackraft font ID: {self.blackraft_font_id}")
            if self.blackraft_font_id != -1:
                font_families = QFontDatabase.applicationFontFamilies(self.blackraft_font_id)
                print(f"Доступні шрифти для Blackraft ID: {font_families}")
                if font_families:
                    self.blackraft_font_family = font_families[0]
                    print(f"Blackraft шрифт успішно завантажено: {self.blackraft_font_family}")
                else:
                    print("Помилка: Не вдалось отримати назву Blackraft шрифту")
                    self.blackraft_font_family = None
            else:
                print(f"Помилка: Не вдалося завантажити Blackraft шрифт з {blackraft_font_path}")
                self.blackraft_font_family = None

        except Exception as e:
            print(f"Виникла помилка при завантаженні шрифтів: {e}")
            self.custom_font_family = None
            self.blackraft_font_family = None

    def show_main_menu(self):
        # Створюємо основний віджет з глітч-фоном
        main_widget = GlitchBackgroundWidget()
        layout = QVBoxLayout(main_widget)
        
        # Додаємо заголовок з глітч-ефектом
        glitch_title = GlitchTitleLabel(custom_font_family=self.custom_font_family)
        layout.addWidget(glitch_title)
        
        # Оновлений стиль кнопок для відповідності стилю гри
        button_style = """
            QPushButton {
                background-color: rgba(17, 17, 17, 180);
                color: #00ff00;
                border: 1px solid #00ff00;
                padding: 15px;
                font-size: 22px;
                font-family: Consolas;
                min-width: 250px;
            }
            QPushButton:hover {
                background-color: rgba(0, 34, 0, 200);
                border: 1px solid #00ff00;
                color: #ffffff;
            }
            QPushButton:pressed {
                background-color: rgba(0, 51, 0, 220);
            }
        """
        
        new_game_btn = QPushButton("НОВА ГРА")
        new_game_btn.setStyleSheet(button_style)
        new_game_btn.clicked.connect(self.start_new_game)
        layout.addWidget(new_game_btn)
        
        exit_btn = QPushButton("ВИХІД")
        exit_btn.setStyleSheet(button_style)
        exit_btn.clicked.connect(self.close)
        layout.addWidget(exit_btn)
        
        layout.setSpacing(30)
        self.setCentralWidget(main_widget)
        self.current_scene = "main_menu"

    def start_new_game(self):
        self.show_prologue()

    def show_prologue(self):
        prologue = PrologueWidget(self.show_intro)
        self.setCentralWidget(prologue)
        prologue.setFocus()
        self.current_scene = "prologue"

    def show_intro(self):
        awakening = AwakeningWidget(self.show_meeting)
        self.setCentralWidget(awakening)
        awakening.setFocus()
        self.current_scene = "awakening"
        
    def show_meeting(self):
        # Використовуємо MeetingWidget для сцени зустрічі
        meeting = MeetingWidget(self.show_main_menu)  # Після завершення повертаємось до меню
        self.setCentralWidget(meeting)
        meeting.setFocus()
        self.current_scene = "meeting"
        
    def keyPressEvent(self, event):
        print(f"Key pressed in main app: {event.key()}")
        
        # Передаємо подію клавіатури до активного віджета
        if self.current_scene == "prologue":
            # Якщо поточна сцена - пролог, і натиснута клавіша K
            if event.key() == Qt.Key.Key_K or event.key() == 1050:  # Латинська K або кирилична К
                print("K key detected in main app, skipping prologue")
                prologue_widget = self.centralWidget()
                if isinstance(prologue_widget, PrologueWidget):
                    # Зупиняємо всі таймери
                    if prologue_widget.after_text_timer and prologue_widget.after_text_timer.isActive():
                        prologue_widget.after_text_timer.stop()
                    
                    if prologue_widget.typewriter_timer.isActive():
                        prologue_widget.typewriter_timer.stop()
                        
                    if prologue_widget.pulse_timer.isActive():
                        prologue_widget.pulse_timer.stop()
                    
                    # Зупиняємо всі анімації та переходимо до наступної сцени
                    prologue_widget.fade_to_black = 1.0
                    prologue_widget.update()
                    
                    # Викликаємо фініш з затримкою для відображення затемнення
                    QTimer.singleShot(300, prologue_widget.finish_prologue)
            
        # Виклик батьківського обробника для інших клавіш
        super().keyPressEvent(event)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = GameApp()
    window.show()
    sys.exit(app.exec()) 