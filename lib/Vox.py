import platform
import re
import os
import requests
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import InvalidArgumentException
from bs4 import BeautifulSoup as bs
from pathlib import Path
from PIL import Image
from . import Color
from . import Menu
from . import Watermark

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
    COMMENTS_PER_IMAGE = 4
    VOXED_URL = 'https://www.voxed.net'

    def __init__(self, url):
        self.parsed = Vox._get_vox_html_code()

        self.options = Options()
        self.options.headless = True

        self.url = url

        self.driver = webdriver.Firefox(
            options=self.options,
            executable_path=DRIVER
        )

        try:
            self.driver.get(url)

        except InvalidArgumentException:
            text.print_error('URL is not valid. ')
            quit()

        # Deleting nav
        self.driver.execute_script("""
            let navElement = document.querySelector('nav');
            navElement.remove();
        """)

        # Export vox's image as
        self.vox_path = 'vox.png'
        self.comments_path = 'final_comments.jpg'

        # Getting properties
        self.title = self.driver.find_element_by_css_selector('h1')
        self.title = self.title.text

        self.content = self.driver.find_element_by_css_selector('section.voxData')

        self.description = self.driver.find_element_by_css_selector('#voxContent')
        self.description = self.description.text

        self.image_url = self.driver.find_element_by_css_selector('.voxImage img')
        self.image_url = self.image_url.get_attribute('src')

        self.comments = self._get_comments()
        self.total_comments = len(self.comments)

        if 'darkmode' in self.parsed.find('html').attrs.get('class'):
            self.darkmode = True
            self.watermark_color = 'white'

        else:
            self.darkmode = False
            self.watermark_color = 'black'

        text.print_success('got vox\'s complete information.')

    def make_image(self):
        print('Compositing image...')

        self.driver.save_screenshot(self.vox_path)

        location = self.content.location
        size = self.content.size

        x, y = location['x'], location['y']
        x2, y2 = location['x'] + size['width'], location['y'] + size['height']

        self.image = Image.open(self.vox_path)
        self.image = self.image.crop((x, y, x2, y2))

        self.image.save(self.vox_path)

        path = self.vox_path
        color = self.watermark_color

        watermark = Watermark(path, color, ('right', 'top'),  25)
        watermark.export(True)

        text.print_success('image composited successfully. ')

    def make_comments_image(self, comments: list) -> str:
        """Composites a comments image basing on the `comments` argument

        The `comments` parameter must be a list of comments, that must have
        the same form as `self.comments` (list of dicts each one with both
        comment text and its respective id key)

        Returns a string that represents the name of the file the image was
        exported as.
        """

        print('Compositing comments image...')

        comment_images = list()
        export_as = self.comments_path

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

            coords = {key: int(value) for key, value in coords.items()}

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

    def start_comments_menu(self) -> list:
        """Starts the select comments menu.

        Returns a list that represents the selected comments. This list has
        the same form as `self.comments` (list of dicts each one with both
        comment text and its respective id key)
        """

        comment_choices = list()
        comments_menu_max_per_page = 10

        index = 0
        max_per_page = comments_menu_max_per_page

        title = self.title
        total_comments = self.total_comments
        url = self.url

        for i in range(Vox.COMMENTS_PER_IMAGE):
            tc = text.get_changed(
                f'{[ c + 1 for c in comment_choices ]}',
                color='yellow',
                style='bright',
            )

            # Compositing the message that will appear above the menu all
            # the time
            t1 = f'Comments grabbed: {tc}'
            t2 = f'Vox: {title}, {total_comments} comments, url: {url}'
            t3 = f'Description: {self.description}'
            t4 = f'Image url: {self.image_url}'
            above_message = f'{t1}\n{t2}\n{t3}\n{t4}\n'

            menu = Menu(self.comments, {
                'above_message': above_message,
                'ask_message': f'Pick {Vox.COMMENTS_PER_IMAGE} comments',
                'max_per_page': comments_menu_max_per_page,
            }, 'comment', 'id')

            menu.index = index
            menu.in_screen = max_per_page

            chosen = menu.start()

            index = menu.index
            max_per_page = menu.in_screen

            comment_choices.append(chosen)

        comments_chosen = [self.comments[n] for n in comment_choices]

        return comments_chosen

    def _get_comments(self) -> list:
        """Returns a list of dicts, with keys `comment` and `id`
        """

        comments = list()

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

            comments.append({
                'comment': comment_text,
                'id': comment.get_attribute('id')
            })

        return comments

    def _parse_voxs_info(voxs):
        voxs_list = list()

        for vox in voxs:
            info = dict()

            css_selector = 'div.voxHeader div.voxComments.textShadon span'
            comments = vox.select_one(css_selector)

            if comments is None:
                continue

            url = Vox.VOXED_URL + vox.attrs.get('href')

            t = text.get_changed(vox.select_one('h4').getText(), style='bright')
            info['title'] = t
            info['comments'] = int(comments.getText())
            info['url'] = url

            voxs_list.append(info)

        return voxs_list

    def _get_vox_html_code():
        print('Getting vox\'s information...')

        response = requests.get(Vox.VOXED_URL)

        if not response.status_code == 200:
            m = 'couldnt request the voxed HTML code. Response status code: '
            text.print_error(m + str(response.status_code))
            exit()

        text.print_success('got voxed\'s HTML code')

        parsed = bs(response.text, 'html.parser')

        return parsed

    @classmethod
    def choose_vox(cls):
        parsed = Vox._get_vox_html_code()

        voxs = parsed.select('div#voxList a')

        voxs_list = Vox._parse_voxs_info(voxs)

        # Sorting by number of comments
        voxs_list = sorted(
            voxs_list,
            key=lambda x: x.get('comments'),
            reverse=True
        )

        menu = Menu(voxs_list, {
            'max_per_page': 20,
            'ask_message': 'Pick one kjj',
        }, 'title', 'comments')

        vox_chosen = menu.start()
        vox_chosen = voxs_list[vox_chosen]

        url = vox_chosen.get("url", "No url")

        return cls(url)

    def __del__(self):
        print('Quitting driver...')
        self.driver.quit()
        text.print_success('done')
