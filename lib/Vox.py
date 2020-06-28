import platform
import re
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from pathlib import Path
from PIL import Image
from . import Color

text = Color()

SYSTEM = platform.system()
DRIVER = Path('.').resolve()

if SYSTEM == 'Windows':
    DRIVER = str(DRIVER / 'lib' / 'geckodriver.exe')

elif SYSTEM == 'Linux':
    DRIVER = str(DRIVER / 'lib' / 'geckodriver')

else:
    text.print_error('didnt recognize the system you are in. Aborting.')
    quit()


class Vox:
    def __init__(self, url):
        print('Getting vox\'s information...')
        self.options = Options()
        self.options.headless = True

        self.url = url

        self.driver = webdriver.Firefox(
            options=self.options,
            executable_path=DRIVER
        )

        self.driver.get(url)
        self.content = self.driver.find_element_by_css_selector(
            'section.voxData'
        )

        self.comments = list()

        for comment in self.driver.find_elements_by_css_selector('.comment'):
            selector = '.commentContent'
            comment_text = comment.find_element_by_css_selector(selector).text
            regex = re.findall(r'(>>[A-Z\d]{7})\n*', comment_text)

            for match in regex:
                comment_text = comment_text.replace(match, '')

            comment_text = comment_text.strip()

            if len(comment_text) <= 0:
                continue

            self.comments.append({
                'comment': comment_text,
                'id': text.get_changed(
                    comment.get_attribute('id'),
                    style='bright',
                    color='yellow'
                )
            })

        text.print_success('got vox\'s complete information.')

    def make_image(self, path='final_result.png'):
        self.path = path

        print('Compositing image...')
        self.driver.save_screenshot(self.path)

        location = self.content.location
        size = self.content.size

        x, y = location['x'], location['y']
        x2, y2 = location['x'] + size['width'], location['y'] + size['height']

        self.image = Image.open(self.path)
        self.image = self.image.crop((x, y, x2, y2))

        self.image.save(self.path)

        text.print_success('image composited successfully. ')

    def make_comments_image(self):
        return

    def __del__(self):
        print('Quitting driver...')
        self.driver.quit()
        text.print_success('done')
