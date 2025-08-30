import pygame
import keyboard
import threading
import time
import sys
import subprocess
import os
# ═══════════════════════════════════════════════════════════════════════════
# НАСТРОЙКИ УПРАВЛЕНИЯ - ИЗМЕНИТЕ ПОД ВАШИ НУЖДЫ
# ═══════════════════════════════════════════════════════════════════════════
AXIS_0_POS = "d"        # Левый стик ВПРАВО
AXIS_0_NEG = "a"        # Левый стик ВЛЕВО
AXIS_1_POS = "s"        # Левый стик ВНИЗ
AXIS_1_NEG = "w"        # Левый стик ВВЕРХ
AXIS_2_POS = "right"    # Правый стик ВПРАВО  
AXIS_2_NEG = "left"     # Правый стик ВЛЕВО
AXIS_3_POS = "down"     # Правый стик ВНИЗ
AXIS_3_NEG = "up"       # Правый стик ВВЕРХ
AXIS_4_POS = "q"        # LT (левый триггер)
AXIS_5_POS = "e"        # RT (правый триггер)
BUTTON_0 = "space"      # A
BUTTON_1 = "shift"      # B  
BUTTON_2 = "ctrl"       # X
BUTTON_3 = "tab"        # Y
BUTTON_4 = "r"          # LB (левый бампер)
BUTTON_5 = "t"          # RB (правый бампер)
BUTTON_6 = "esc"        # Back/View
BUTTON_7 = "enter"      # Start/Menu
BUTTON_8 = "f"          # Левый стик (нажатие)
BUTTON_9 = "g"          # Правый стик (нажатие)
DPAD_UP = "1"           # D-Pad ВВЕРХ
DPAD_DOWN = "2"         # D-Pad ВНИЗ
DPAD_LEFT = "3"         # D-Pad ВЛЕВО
DPAD_RIGHT = "4"        # D-Pad ВПРАВО
# ═══════════════════════════════════════════════════════════════════════════
# НАСТРОЙКИ ПОВЕДЕНИЯ
# ═══════════════════════════════════════════════════════════════════════════
AXIS_DEADZONE = 0.2     # Мёртвая зона для осей (от 0.0 до 1.0)
UPDATE_RATE = 120        # Частота обновления в Гц
# ═══════════════════════════════════════════════════════════════════════════
# НАСТРОЙКИ ЗАПУСКА ОСНОВНОЙ ПРОГРАММЫ
# ═══════════════════════════════════════════════════════════════════════════
MAIN_PROGRAM = "python key_display.py"  # ИЗМЕНИТЕ НА ВАШУ ПРОГРАММУ
STARTUP_DELAY = 2                       # Задержка перед запуском основной программы (в секундах)
# ═══════════════════════════════════════════════════════════════════════════
# ОСНОВНОЙ КОД - НЕ ИЗМЕНЯЙТЕ БЕЗ НЕОБХОДИМОСТИ
# ═══════════════════════════════════════════════════════════════════════════
class JoystickController:
    def __init__(self):
        self.running = False
        self.joystick = None
        self.pressed_keys = set()
        self.main_process = None
        self.axis_config = {
            0: {"pos": AXIS_0_POS, "neg": AXIS_0_NEG},
            1: {"pos": AXIS_1_POS, "neg": AXIS_1_NEG},
            2: {"pos": AXIS_2_POS, "neg": AXIS_2_NEG},
            3: {"pos": AXIS_3_POS, "neg": AXIS_3_NEG},
            4: {"pos": AXIS_4_POS, "neg": None},
            5: {"pos": AXIS_5_POS, "neg": None},
        }
        self.button_config = {
            0: BUTTON_0, 1: BUTTON_1, 2: BUTTON_2, 3: BUTTON_3, 4: BUTTON_4,
            5: BUTTON_5, 6: BUTTON_6, 7: BUTTON_7, 8: BUTTON_8, 9: BUTTON_9,
        }
        self.dpad_config = {
            (0, 1): DPAD_UP, (0, -1): DPAD_DOWN, (-1, 0): DPAD_LEFT, (1, 0): DPAD_RIGHT
        }
    def initialize_pygame(self):
        try:
            pygame.init()
            pygame.joystick.init()
            if pygame.joystick.get_count() == 0:
                print("Нет джойстика")
                return False
            self.joystick = pygame.joystick.Joystick(0)
            self.joystick.init()
            print(f"✅ Найден джойстик: {self.joystick.get_name()}")
            print(f"   Осей: {self.joystick.get_numaxes()}")
            print(f"   Кнопок: {self.joystick.get_numbuttons()}")
            print(f"   Шляпок (D-Pad): {self.joystick.get_numhats()}")
            return True
        except:
            return False
    def press_key(self, key):
        if key and key not in self.pressed_keys:
            try:
                keyboard.press(key)
                self.pressed_keys.add(key)
            except:
                pass
    def release_key(self, key):
        if key and key in self.pressed_keys:
            try:
                keyboard.release(key)
                self.pressed_keys.remove(key)
            except:
                pass
    def handle_axis(self, axis_num, value):
        if axis_num not in self.axis_config:
            return
        config = self.axis_config[axis_num]
        pos_key, neg_key = config["pos"], config["neg"]
        if abs(value) < AXIS_DEADZONE:
            self.release_key(pos_key)
            if neg_key: self.release_key(neg_key)
        elif value > AXIS_DEADZONE:
            self.press_key(pos_key)
            if neg_key: self.release_key(neg_key)
        elif value < -AXIS_DEADZONE and neg_key:
            self.press_key(neg_key)
            self.release_key(pos_key)
    def handle_button(self, button_num, pressed):
        if button_num in self.button_config:
            key = self.button_config[button_num]
            self.press_key(key) if pressed else self.release_key(key)
    def handle_dpad(self, hat_x, hat_y):
        for key in self.dpad_config.values():
            self.release_key(key)
        if (hat_x, hat_y) in self.dpad_config:
            self.press_key(self.dpad_config[(hat_x, hat_y)])
    def start_main_program(self):
        try:
            time.sleep(STARTUP_DELAY)
            if MAIN_PROGRAM.startswith("python "):
                script_name = MAIN_PROGRAM.split(" ", 1)[1]
                if not os.path.exists(script_name):
                    return
            if os.name == 'nt':
                if MAIN_PROGRAM.startswith("python "):
                    parts = MAIN_PROGRAM.split()
                    self.main_process = subprocess.Popen(parts, creationflags=subprocess.CREATE_NEW_CONSOLE)
                else:
                    self.main_process = subprocess.Popen(MAIN_PROGRAM, shell=True, creationflags=subprocess.CREATE_NEW_CONSOLE)
            else:
                self.main_process = subprocess.Popen(MAIN_PROGRAM.split())
        except:
            pass
    def monitor_main_program(self):
        if self.main_process:
            try:
                self.main_process.wait()
                self.running = False
            except:
                pass
    def main_loop(self):
        clock = pygame.time.Clock()
        while self.running:
            pygame.event.pump()
            try:
                for axis_num in range(min(6, self.joystick.get_numaxes())):
                    self.handle_axis(axis_num, self.joystick.get_axis(axis_num))
                for button_num in range(min(10, self.joystick.get_numbuttons())):
                    self.handle_button(button_num, self.joystick.get_button(button_num))
                if self.joystick.get_numhats() > 0:
                    hat = self.joystick.get_hat(0)
                    self.handle_dpad(hat[0], hat[1])
            except:
                break
            clock.tick(UPDATE_RATE)
    def start(self):
        if not self.initialize_pygame():
            return False
        self.running = True
        threading.Thread(target=self.start_main_program, daemon=True).start()
        if MAIN_PROGRAM.strip():
            threading.Thread(target=self.monitor_main_program, daemon=True).start()
        try:
            self.main_loop()
        except KeyboardInterrupt:
            pass
        finally:
            self.stop()
        return True
    def stop(self):
        self.running = False
        for key in list(self.pressed_keys):
            self.release_key(key)
        if self.main_process and self.main_process.poll() is None:
            try:
                self.main_process.terminate()
                time.sleep(1)
                if self.main_process.poll() is None:
                    self.main_process.kill()
            except:
                pass
        if self.joystick:
            self.joystick.quit()
        pygame.quit()
def print_configuration():
    print("🎮 КОНФИГУРАЦИЯ УПРАВЛЕНИЯ:")
    print("="*50)
    print(f"Левый стик:  ↑ {AXIS_1_NEG} ↓ {AXIS_1_POS} ← {AXIS_0_NEG} → {AXIS_0_POS}")
    print(f"Правый стик: ↑ {AXIS_3_NEG} ↓ {AXIS_3_POS} ← {AXIS_2_NEG} → {AXIS_2_POS}")
    print(f"Триггеры:    LT= {AXIS_4_POS} RT={AXIS_5_POS}")
    print(f"Кнопки:      A= {BUTTON_0} B= {BUTTON_1} X= {BUTTON_2} Y= {BUTTON_3}")
    print(f"Бамперы:     LB= {BUTTON_4} RB= {BUTTON_5}")
    print(f"Система:     Back= {BUTTON_6} Start= {BUTTON_7}")
    print(f"Стики:       L3= {BUTTON_8} R3= {BUTTON_9}")
    print(f"D-Pad:       ↑ {DPAD_UP} ↓ {DPAD_DOWN} ← {DPAD_LEFT} → {DPAD_RIGHT}")
    print("="*50)
def main():
    print_configuration()
    JoystickController().start()
if __name__ == "__main__":
    try:
        main()
    except:
        sys.exit(1)