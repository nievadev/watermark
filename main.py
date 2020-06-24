from bs4 import BeautifulSoup as bs
import requests
import platform
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


def extract_vox_data(voxs):
    voxs_list = list()

    for vox in voxs:
        info = dict()

        css_selector = 'div.voxHeader div.voxComments.textShadon span'
        comments = vox.select_one(css_selector)

        if comments is None:
            continue

        url = VOXED_URL + vox.attrs.get('href')

        info['title'] = vox.select_one('h4').getText()
        info['comments'] = int(comments.getText())
        info['url'] = url

        # style = vox.attrs.get('style')
        # match = re.search(r'url\(.*\)', style)

        # image_url = style[match.start():match.end()]
        # image_url = image_url[image_url.find('(') + 1:image_url.find(')')].strip() # NOQA

        # info['image_url'] = image_url

        voxs_list.append(info)

    return voxs_list


def main():
    print('Getting voxed\'s HTML...')

    response = requests.get(VOXED_URL)

    if not response.status_code == 200:
        text.print_error('couldnt request the voxed HTML code. Response status code: ' + str(response.status_code))
        exit()

    text.print_success('got voxed\'s HTML code')

    parsed = bs(response.text, 'html.parser')

    darkmode = True if 'darkmode' in parsed.find('html').attrs.get('class') else False

    voxs = parsed.select('div#voxList a')

    voxs_list = extract_vox_data(voxs)
    voxs_list = sorted(voxs_list, key=lambda x: x.get('comments'), reverse=True)

    menu = Menu(voxs_list, options={ 'max_per_page' : 10, 'ask_message' : 'Pick one kjj' })

    vox_chosen = menu.start()
    vox_chosen = voxs_list[vox_chosen]

    print(f'Vox: "{ vox_chosen.get("title", "No title") }", { vox_chosen.get("comments", 0) } comments')

    vox = Vox(vox_chosen.get('url', ''))
    vox.make_image('final_vox.png')

    if darkmode:
        print('Applying watermark... (xy -> right top, detected darkmode so color -> white)')
        color = 'white'

    else:
        print('Applying watermark... (xy -> right top, not detected darkmode so color -> black)')
        color = 'black'

    watermark = Watermark(vox.path, color, ('right', 'top'), 25)
    watermark.export(True)

if __name__ == '__main__':
    main()

# test_url = 'https://upload.voxed.net/SmF9oeVRnrH98KQKfShq.jpg'
