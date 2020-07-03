# todo: implement press enter again to just use the already grabbed comments

import click
from lib.Vox import Vox
from lib.Watermark import Watermark


@click.command()
@click.option(
    '-u', '--url', 'url',
    type=str,
    default=''
)
def main(url):
    vox = Vox.choose_vox() if len(url) == 0 else Vox(url)

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
