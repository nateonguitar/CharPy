from abc import ABC, abstractmethod
import datetime
import time


from charpy.console_printer import ConsolePrinter
from charpy.input_controller import InputController
from charpy.screen import Screen

class Game(ABC):
    # Convenient reference to the Game object
    instance = None

def clamp(value, lower, upper):
    return lower if value < lower else upper if value > upper else value


class Game(ABC):
    def __init__(self, fps=60):
        Game.instance = self
        self.stopped = False
        self.show_debug_info = False
        self.debug_size = {
            "key": 0,
            "value": 0,
        }
        self.debug_info = {
            "FPS": 0,
            "FPS Target": 0,
            "Chars Replaced": 0,
        }
        self.screen = Screen()
        self.printer = None
        self.input_controller = None
        self.timer_thread = None
        self.printer = ConsolePrinter()
        self.input_controller = InputController(self)
        self.input_controller.start_watching_key_presses()
        self.printer.clear_screen()
        self.clear_set_empty_screen()

        # FPS and timming
        self.fps_target: int = fps
        self.fps_avg: float = self.fps_target
        self.fps_samples: int = self.fps_target * 2
        self.time_adjustment: float = 0
        self.last_loop_start_time: float = time.time() - 1 / self.fps_target

    def clear_set_empty_screen(self):
        self.screen = self.printer.get_empty_screen()

    @abstractmethod
    def update(self, deltatime: datetime.timedelta):
        pass

    @abstractmethod
    def draw(self):
        # The Strategy:
        # Every draw cycle will print to every position in the console.
        # We need to build a 2D array of what should be printed.
        # So we create a "screen" 2D array that is filled with spaces,
        # then replace values at certain positions.
        # Then we only do a print cycle once everything is in place.

        if self.show_debug_info:
            for key in self.debug_info:
                value = self.debug_info[key]
                key_width = len(str(key))
                if key_width > self.debug_size["key"]:
                    self.debug_size["key"] = key_width
                val_width = len(str(value)) if value is not None else 0
                if val_width > self.debug_size["value"]:
                    self.debug_size["value"] = val_width
            # + 2 for the colon + space we will use
            key_value_width = self.debug_size["key"] + self.debug_size["value"] + 2
            i = 0
            screen_width = self.printer.terminal_size.columns
            for key in self.debug_info:
                value = self.debug_info[key]
                _key = str(key).rjust(self.debug_size["key"])
                _value = str(value if value is not None else " ").ljust(self.debug_size["value"])
                key_value = f"{_key}: {_value}"
                self.screen.set(screen_width - key_value_width, i, key_value)
                i += 1

        self.printer.draw_screen(self.screen)
        self.clear_set_empty_screen()

    def start_game(self):
        """
        Called to start a game loop
        """
        # First Loop Setup
        self.last_loop_start_time = time.time() - 1 / self.fps_target  # Set the last loop_start time, expected value

        # Loop forever
        while True:

            # Record loop time data
            loop_start_time = time.time()
            loop_delta_time = loop_start_time - self.last_loop_start_time
            self.last_loop_start_time = loop_start_time

            if self.stopped:
                return

            self.game_loop(loop_delta_time)
            if self.show_debug_info:
                self.calculate_debug(loop_delta_time)

            # Calculate the "Cumulative Moving Average" with fixed n
            # https://en.wikipedia.org/wiki/Moving_average#Cumulative_moving_average
            avg = self.fps_avg
            samples = self.fps_samples
            self.fps_avg = (avg * samples + (1.0 / loop_delta_time)) / (samples + 1)

            # Time after game_loop is end
            loop_end_time = time.time()

            frame_time = 1.0 / self.fps_target  # How long a frame should take
            loop_used = loop_end_time - loop_start_time  # How much time the current loop took.

            if self.fps_target > self.fps_avg:
                self.time_adjustment = self.time_adjustment + 0.000001
            if self.fps_target + 0.1 < self.fps_avg:
                self.time_adjustment = self.time_adjustment - 0.000001
            self.time_adjustment = clamp(self.time_adjustment, -0.01, 0.01)

            real_wait_time = frame_time - loop_used - self.time_adjustment
            real_wait_time = clamp(real_wait_time, 0, 1 / 60)
            time.sleep(real_wait_time)

    def game_loop(self, loop_delta_time: float):
        """[summary]

        Args:
            loop_delta_time (float): Time elapsed since last game_loop (seconds)
        """
        if self.show_debug_info:
            self.calculate_debug(loop_delta_time)

        self.update(loop_delta_time)
        self.draw()

    def calculate_debug(self, loop_delta_time: float):
        self.debug_info["FPS"] = round(self.fps_avg, 1)
        self.debug_info["FPS Target"] = self.fps_target
        self.debug_info["Chars Replaced"] = ConsolePrinter.replaced

    def end_game(self):
        self.printer.clear_screen()
        self.stopped = True
        self.input_controller.stop_watching_key_presses()

    def set_on_keydown(self, func):
        self.input_controller.set_on_keydown(func)

    def set_on_keyup(self, func):
        self.input_controller.set_on_keyup(func)
