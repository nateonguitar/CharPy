import os
import threading
from .input_controller import InputController
from .console_printer import ConsolePrinter


class Game():
    game_over = False
    current_speed = 0.5
    time_between_draws = 1 / 30
    printer = None
    input_controller = None
    timer_thread = None


    # TODO: delete this
    character_flipper = False
    def flip_test_char(self):
        self.character_flipper = not self.character_flipper


    def start(self):
        self.printer = ConsolePrinter()
        self.input_controller = InputController(self)
        self.input_controller.start_watching_key_presses()
        self.printer.clear_screen()
        self.game_loop()


    def update(self):
        pass


    def draw(self):
        # The Strategy:
        # Every draw cycle will print to every position in the console.
        # We need to build a 2D array of what should be printed.
        # So we create a "screen" 2D array that is filled with spaces,
        # then replace values at certain positions.
        # Then we only do a print cycle once everything is in place.

        # Create a representation of the screen
        screen = self.printer.get_empty_screen()

        # TODO: Replace this with real game object data,
        #       we can logically replace anything we want on the screen
        #       at this stage
        ch = 'X' if self.character_flipper else 'O'
        overrides = [
            ['press "A" to swap the character'],
            [' ', '╔', '═','═', '═', '╗',],
            [' ', '║', ' ', ch, ' ', '║',],
            [' ', '╚', '═','═', '═', '╝',],
        ]
        for line_number in range(0, len(overrides)):
            line = overrides[line_number]
            for column_number in range(0, len(line)):
                override_char = overrides[line_number][column_number]
                screen[line_number][column_number] = override_char

        self.printer.draw_screen(screen)


    def game_loop(self):
        self.update()
        self.draw()

        if self.game_over:
            # stop the game loop
            return

        # wait some time on a separate thread then run game_loop again
        # this avoids using a spin-lock
        self.timer_thread = threading.Timer(self.time_between_draws, self.game_loop)
        self.timer_thread.start()


    def end_game(self):
        self.input_controller.stop_watching_key_presses()
        self.timer_thread.cancel()
        self.printer.clear_screen()