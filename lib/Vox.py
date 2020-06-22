import sys
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from PIL import Image
from .Color import Color

text = Color()

class Vox:
    def __init__(self, url):
        print('Getting vox\'s information...')
        self.options = Options()
        self.options.headless = True

        self.url = url

        self.driver = webdriver.Firefox(options=self.options, executable_path='bin/geckodriver')

        self.driver.get(url)
        self.content = self.driver.find_element_by_css_selector('section.voxData')

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
        self.image = self.image.crop(( x, y, x2, y2 ))

        self.image.save(self.path)

        text.print_success('image composited successfully. ')
