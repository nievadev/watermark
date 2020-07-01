# todo: implement press enter again to just use the already grabbed comments

import platform
import click
import requests
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


def request_get(url):
    response = requests.get(url)

    if not response.status_code == 200:
        m = 'couldnt request the voxed HTML code. Response status code: '
        text.print_error(m + str(response.status_code))
        exit()

    return response


def get_voxs_info(voxs):
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


@click.command()
@click.option(
    '-u', '--url', 'url',
    type=str,
    default=''
)
def main(url):
    if len(url) == 0:
        print('Getting voxed\'s HTML...')

        response = request_get(VOXED_URL)

        text.print_success('got voxed\'s HTML code')

        parsed = bs(response.text, 'html.parser')

        voxs = parsed.select('div#voxList a')

        voxs_list = get_voxs_info(voxs)

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

        vox = Vox(url, parsed)

    else:
        vox = Vox(url)

    title = vox.title
    comments = vox.total_comments

    print(f'Vox: \'{title}\', {comments} comments, {url}')

    vox.make_image()

    comments_chosen = vox.start_comments_menu()

    filename = vox.make_comments_image(comments_chosen)

    watermark = Watermark(filename, vox.watermark_color, ('right', 'top'), 25)

    watermark.export(True)


if __name__ == '__main__':
    main()

# test_url = 'https://upload.voxed.net/SmF9oeVRnrH98KQKfShq.jpg'

# style = vox.attrs.get('style')
# match = re.search(r'url\(.*\)', style)

# image_url = style[match.start():match.end()]
# image_url = image_url[image_url.find('(') + 1:image_url.find(')')].strip() # NOQA

# info['image_url'] = image_url
