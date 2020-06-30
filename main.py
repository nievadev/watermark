# TODO: implement url argument

import requests
import platform
import time
from bs4 import BeautifulSoup as bs
from lib.Color import Color
from lib.Vox import Vox
from lib.Watermark import Watermark
from lib.Menu import Menu

text = Color()

VOXED_URL = 'https://www.voxed.net'
PLATFORM = platform.system()
NEXT_PAGE = 'n'
PREVIOUS_PAGE = 'b'
KEYBINDS = NEXT_PAGE, PREVIOUS_PAGE
COMMENTS_PER_IMAGE = 4


def parse_voxs(voxs):
    voxs_list = list()

    for vox in voxs:
        info = dict()

        css_selector = 'div.voxHeader div.voxComments.textShadon span'
        comments = vox.select_one(css_selector)

        if comments is None:
            continue

        url = VOXED_URL + vox.attrs.get('href')

        t = text.get_changed(vox.select_one('h4').getText(), style='bright')
        info['title'] = t
        info['comments'] = int(comments.getText())
        info['url'] = url

        voxs_list.append(info)

    return voxs_list


def main():
    print('Getting voxed\'s HTML...')

    response = requests.get(VOXED_URL)

    if not response.status_code == 200:
        m = 'couldnt request the voxed HTML code. Response status code: '
        text.print_error(m + str(response.status_code))
        exit()

    text.print_success('got voxed\'s HTML code')

    parsed = bs(response.text, 'html.parser')

    darkmode = False

    if 'darkmode' in parsed.find('html').attrs.get('class'):
        darkmode = True

    voxs = parsed.select('div#voxList a')

    voxs_list = parse_voxs(voxs)
    voxs_list = sorted(
        voxs_list,
        key=lambda x: x.get('comments'),
        reverse=True
    )

    menu = Menu(voxs_list, {
        'max_per_page': 10,
        'ask_message': 'Pick one kjj',
    }, 'title', 'comments')

    vox_chosen = menu.start()
    vox_chosen = voxs_list[vox_chosen]

    title = vox_chosen.get("title", "No title")
    comments = vox_chosen.get("comments", "No comments")
    url = vox_chosen.get("url", "No url")

    print(f'Vox: \'{title}\', {comments} comments, {url}')

    vox = Vox(url)
    vox.make_image('vox.png')

    if darkmode:
        print('Applying watermark... (right top, white)')
        color = 'white'

    else:
        print('Applying watermark... (right top, black)')
        color = 'black'

    watermark = Watermark(vox.path, color, ('right', 'top'), 25)

    watermark.export(True)

    comment_choices = list()

    comments_menu_max_per_page = 10

    index = 0
    max_per_page = comments_menu_max_per_page

    for i in range(COMMENTS_PER_IMAGE):
        tc = text.get_changed(
            f'{[ c + 1 for c in comment_choices ]}',
            color='yellow',
            style='bright',
        )

        t1 = f'Comments grabbed: {tc}'
        t2 = f'Vox: {title}, {comments} comments, url: {url}'
        t3 = f'Description: {vox.description}'
        t4 = f'Image url: {vox.image_url}'
        above_message = f'{t1}\n{t2}\n{t3}\n{t4}\n'

        menu = Menu(vox.comments, {
            'above_message': above_message,
            'ask_message': f'Pick {COMMENTS_PER_IMAGE} comments',
            'max_per_page': comments_menu_max_per_page,
        }, 'comment', 'id')

        menu.index = index
        menu.in_screen = max_per_page

        chosen = menu.start()

        index = menu.index
        max_per_page = menu.in_screen

        comment_choices.append(chosen)

    comments_chosen = [ vox.comments[n] for n in comment_choices ]

    filename = vox.make_comments_image(comments_chosen)

    watermark = Watermark(filename, color, ('right', 'top'), 25)

    watermark.export(True)

if __name__ == '__main__':
    main()

# test_url = 'https://upload.voxed.net/SmF9oeVRnrH98KQKfShq.jpg'

# style = vox.attrs.get('style')
# match = re.search(r'url\(.*\)', style)

# image_url = style[match.start():match.end()]
# image_url = image_url[image_url.find('(') + 1:image_url.find(')')].strip() # NOQA

# info['image_url'] = image_url
