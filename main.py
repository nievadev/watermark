from bs4 import BeautifulSoup as bs
from Color import Color
import os, requests, platform, time, cursor, re

text = Color()

VOXED_URL = 'https://www.voxed.net'
PLATFORM = platform.system()
NEXT_PAGE = 'n'
PREVIOUS_PAGE = 'b'
KEYBINDS = NEXT_PAGE, PREVIOUS_PAGE

def clean_screen():
    if PLATFORM == 'Windows':
        os.system('cls')

    elif PLATFORM == 'Linux':
        os.system('clear')

def validate_input(chosen, index, max_length) -> bool:
    if chosen in KEYBINDS:
        return True, 'pressed key'

    elif not chosen.isdigit():
        return False, 'not valid option. Trying again... '

    elif not max_length >= int(chosen) > index:
        return False, 'out of range'

    return True, 'validated input'

def extract_vox_data(voxs):
    voxs_list = list()

    for vox in voxs:
        info = dict()

        comments = vox.select_one('div.voxHeader div.voxComments.textShadon span')

        if comments == None:
            continue

        url = VOXED_URL + vox.attrs.get('href')

        info['title'] = vox.select_one('h4').getText()
        info['comments'] = int(comments.getText())
        info['url'] = url

        # style = vox.attrs.get('style')
        # match = re.search(r'url\(.*\)', style)

        # image_url = style[match.start():match.end()]
        # image_url = image_url[image_url.find('(') + 1:image_url.find(')')].strip()

        # info['image_url'] = image_url

        voxs_list.append(info)

    return voxs_list

def start_menu(options_list, max_per_page=10):
    index = 0
    in_screen = max_per_page

    if len(options_list) < max_per_page:
        in_screen = len(options_list)

    while True:
        clean_screen()

        cursor.hide()
    
        print()

        text.print_color('Menu: ', color='blue', style='bright', newline=True)

        for i in range(index, in_screen):
            vox = options_list[i]
            print(i + 1, '->', vox.get('title', 'notitle'), f'({vox.get("comments", "0")})')

        print('Press ' + NEXT_PAGE.upper() + ' to go to the next page.')
        print('Press ' + PREVIOUS_PAGE.upper() + ' to go to the previous page.')
        print()

        pressed_key = input(f'Choose vox [{index + 1}/{in_screen}]: ').strip().lower()

        print()

        success, reason = validate_input(pressed_key, index, in_screen)

        if not success:
            text.print_error(reason)
            time.sleep(0.5)

            continue

        elif reason == 'pressed key':
            if pressed_key == 'n':
                if in_screen == len(options_list):
                    continue

                index += max_per_page

                if in_screen + max_per_page > len(options_list):
                    in_screen = len(options_list)

                    continue

                in_screen += max_per_page

            elif pressed_key == 'b':
                if index - max_per_page < 0:
                    continue

                index -= max_per_page
            
                if in_screen == len(options_list):
                    in_screen = index + max_per_page

                    continue

                in_screen -= max_per_page

            continue

        vox_chosen = int(pressed_key) - 1

        text.print_success(reason)
        cursor.show()

        break

    return vox_chosen

def main():
    response = requests.get(VOXED_URL)

    if not response.status_code == 200:
        text.print_error('couldnt request the voxed HTML code. Response status code: ' + str(response.status_code))
        exit()

    parsed = bs(response.text, 'html.parser')

    voxs = parsed.select('div#voxList a')

    voxs_list = extract_vox_data(voxs)

    voxs_list = sorted(voxs_list, key=lambda x: x.get('comments'), reverse=True)

    vox_chosen = start_menu(voxs_list, 10)

    print(voxs_list[vox_chosen])

if __name__ == '__main__':
    main()

# test_url = 'https://upload.voxed.net/SmF9oeVRnrH98KQKfShq.jpg'
# filename, extension = download_file(test_url, 'downloaded')
# text.print_success('exported file as \'' + filename + extension + '\'.')
