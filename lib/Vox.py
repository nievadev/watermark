import platform
import re
import time
import os
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
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

        js = """
        let navElement = document.querySelector('nav');
        navElement.remove();"""

        self.driver.execute_script(js)

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

            try:
                op = comment.find_element_by_css_selector('.op')

            except NoSuchElementException:
                op = ''

            else:
                t = text.get_changed('op', style='bright', color='green')
                op = '(' + t + ') '

            comment_text = op + comment_text

            self.comments.append({
                'comment': comment_text,
                'id': comment.get_attribute('id')
            })

        self.description = self.driver.find_element_by_css_selector('#voxContent').text
        self.image_url = self.driver.find_element_by_css_selector('.voxImage img').get_attribute('src')

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

    def make_comments_image(self, comments):
        print('Compositing comments image...')

        actions = ActionChains(self.driver)
        comment_images = list()
        export_as = 'final_comments.jpg'

        for i, comment in enumerate(comments):
            filename = 'comment' + str(i) + '.png'
            id_ = comment.get('id', '')

            element = self.driver.find_element_by_css_selector(
                'div[id="' + id_ + '"]'
            )

            y = element.location.get('y', 0)

            coords = self.driver.execute_script(f'''
            window.scrollTo(0, {y});

            let element = document.getElementById("{id_}");
            return element.getBoundingClientRect();
            ''')

            coords = { key: int(value) for key, value in coords.items() }

            x = coords.get('x')
            y = 0 if coords.get('y', 0) <= 0 else coords.get('y', 0)
            w = element.size.get('width')
            h = element.size.get('height')

            self.driver.save_screenshot(filename)

            img = Image.open(filename)
            img = img.crop((x, y, x + w, y + h))
            img = img.convert('RGB')

            comment_images.append(img)

            os.remove(filename)

        widths, heights = zip(*(im.size for im in comment_images))

        image_h = sum(heights)
        image_w = max(widths)

        image_to_export = Image.new('RGB', (image_w, image_h))

        y_offset = 0

        for im in comment_images:
            image_to_export.paste(im, (0, y_offset))
            y_offset += im.size[1]

        image_to_export.save(export_as)

        return export_as

    def __del__(self):
        print('Quitting driver...')
        self.driver.quit()
        text.print_success('done')
