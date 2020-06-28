import requests
import os
from . import Color

text = Color()


class File:
    def __init__(self, file_url):
        self.file_url = file_url

        self.filename = os.path.basename(self.file_url)

        self.name, self.extension = os.path.splitext(self.filename)

        self.response = requests.get(self.file_url)

        if not self.response.status_code == 200:
            m = 'cant get file, got status code '
            text.print_error(m + str(self.response.status_code))

            exit()

        text.print_success('got file without issues')

    def export(self, export_as='default'):
        self.export_filename = export_as + self.extension

        if os.path.isfile(self.export_filename):
            while True:
                m = f'the file {self.export_filename} already exists. '
                text.print_warning(m + 'Overwrite? [y/n]: ', end='')
                answer = input().lower().strip()

                if answer == 'n':
                    print('Aborting. ')

                    exit()

                elif answer == 'y':
                    print('Alright, overwriting... ', end='')

                    break

                else:
                    text.print_error('not valid response. Trying again... ')

        with open(self.export_filename, 'wb') as f:
            for chunk in self.response:
                f.write(chunk)

        text.print_success('downloaded file with no issues')
        return self.export_filename


f = File('https://upload.voxed.net/SmF9oeVRnrH98KQKfShq.jpg')
f.export()
