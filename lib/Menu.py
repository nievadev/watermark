import os, cursor, platform, time
from . import Color

PLATFORM = platform.system()

text = Color()

def clean_screen():
    if PLATFORM == 'Windows':
        os.system('cls')

    elif PLATFORM == 'Linux':
        os.system('clear')

class Menu:
    def __init__(self, options_list, options=dict()):
        self.options_list = options_list
        self.index = 0
        self.next_page = 'n'
        self.previous_page = 'b'
        self.keybinds = self.next_page, self.previous_page

        self.ask_message = options.get('ask_message', 'Choose one')
        self.max_per_page = options.get('max_per_page', 10)

        self.in_screen = self.max_per_page

        if len(self.options_list) < self.max_per_page:
            self.in_screen = len(self.options_list)
         
    def __del__(self):
        cursor.show()

    def _validate_input(self, chosen):
        if chosen in self.keybinds:
            return True, 'pressed key'

        elif not chosen.isdigit():
            return False, 'not valid option. Trying again... '

        elif not self.in_screen >= int(chosen) > self.index:
            return False, 'out of range'

        return True, 'validated input'

    def start(self):
        while True:
            clean_screen()

            cursor.hide()
        
            print()

            text.print_color('Menu: ', color='blue', style='bright', newline=True)

            for i in range(self.index, self.in_screen):
                vox = self.options_list[i]
                print(i + 1, '->', vox.get('title', 'notitle'), f'({vox.get("comments", "0")})')

            print('Press ' + self.next_page.upper() + ' to go to the next page.')
            print('Press ' + self.previous_page.upper() + ' to go to the previous page.')
            print()

            try:
                pressed_key = input(f'{self.ask_message} [{self.index + 1}/{self.in_screen}]: ').strip().lower()

            except KeyboardInterrupt:
                print()
                exit()

            print()

            success, reason = self._validate_input(pressed_key)

            if not success:
                text.print_error(reason)
                time.sleep(0.5)

                continue

            elif reason == 'pressed key':
                if pressed_key == 'n':
                    if self.in_screen == len(self.options_list):
                        continue

                    self.index += self.max_per_page

                    if self.in_screen + self.max_per_page > len(self.options_list):
                        self.in_screen = len(self.options_list)

                        continue

                    self.in_screen += self.max_per_page

                elif pressed_key == 'b':
                    if self.index - self.max_per_page < 0:
                        continue

                    self.index -= self.max_per_page
                
                    if self.in_screen == len(self.options_list):
                        self.in_screen = self.index + self.max_per_page

                        continue

                    self.in_screen -= self.max_per_page

                continue

            self.vox_chosen = int(pressed_key) - 1

            text.print_success(reason)
            cursor.show()

            break

        return self.vox_chosen
