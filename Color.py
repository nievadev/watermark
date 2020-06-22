import colorama

class Color:
    def __init__(self):
        colorama.init()

    def print_color(self, text, color='white', style='normal', newline=False):
        self.set_color(color)
        self.set_style(style)
        end = '' if not newline else '\n'

        print(text, end=end)

        self.reset()

    def set_color(self, color):
        print(getattr(colorama.Fore, color.upper()), end='')

    def set_style(self, style):
        print(getattr(colorama.Style, style.upper()), end='')

    def reset(self):
        print(colorama.Style.RESET_ALL, end='')

    def print_error(self, text, **kwargs):
        self.print_color('Error: ', color='red', style='bright')
        print(text, **kwargs)

    def print_warning(self, text, **kwargs):
        self.print_color('Warning: ', color='yellow', style='bright')
        print(text, **kwargs)

    def print_success(self, text, **kwargs):
        self.print_color('Success: ', color='green', style='bright')
        print(text, **kwargs)

    def __del__(self):
        colorama.deinit()
