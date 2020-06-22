# Developer: Martin Nieva (nievadev in GitHub)

from PIL import ImageDraw, ImageFont, Image
from moviepy import editor

# todo: look up for executable_path arg of webdriver
# todo: fix export method later
# todo: fix this later
try:
    from .Color import Color
except:
    from Color import Color
     
import click
import glob
import os
import sys

text = Color()

IMAGE_EXTENSIONS = 'png', 'jpg', 'jpeg'
IMAGE_EXPORT_EXTENSION = 'jpg'
VIDEO_EXPORT_EXTENSION = 'mp4'
TEXT_MARGIN = 4
VIDEO_EXTENSIONS = 'mp4', 'gif', 'webm'
OTHER_DELETE_EXTENSIONS = '', 
OUTPUT_NAME = 'result'
WATERMARK = '@el.rincon.voxero'
INSULT_NAME = 'Ignacio'
EXCEPTION_FILES = 'test.png', 
SUPPORTED_X = 'left', 'center', 'right'
SUPPORTED_Y = 'top', 'center', 'bottom'
SUPPORTED_COLORS = {
    'black' : (0, 0, 0), 
    'white' : (255, 255, 255), 
    'red' : (255, 0, 0), 
    'blue' : (0, 0, 255), 
    'green' : (0, 255, 0)
}

def clean_files(filetype):
    """Delete files which names end with the filetype specified"""

    files = glob.glob('*.' + filetype)

    if len(files) < 1:
        print('No .' + filetype + ' files.')
        return

    for _file in files:
        if _file in EXCEPTION_FILES:
            text.print_warning('ignoring  ' + _file)

            continue

        print('Deleting ' + _file + '... ', end='')

        os.remove(_file)

        text.print_color('done', color='green', style='bright', newline=True)

class Watermark:
    def __init__(self, filepath, color, xy, size):
        """Apply watermark to photo or video tool"""

        self.xy = xy
        self.color = color
        self.filepath = filepath
        self.filename, self.extension = os.path.splitext(self.filepath)
        self.size = size

        def export():
            pass

        self.export = export

        if self.filepath == 'clean':
            print('Cleaning...')

            for filetype in IMAGE_EXTENSIONS + VIDEO_EXTENSIONS + OTHER_DELETE_EXTENSIONS:
                clean_files(filetype)

            text.print_success('done')
            return

        # Checking the XY is supported
        self.x, self.y = self.xy[0], self.xy[1]

        if self.x not in SUPPORTED_X:
            raise click.ClickException(INSULT_NAME + ' pelotudo!! La opcion ' + self.x + ' no es valida carajo!!!')

        if self.y not in SUPPORTED_Y:
            raise click.ClickException(INSULT_NAME + ' pelotudo!! La opcion ' + self.y + ' no es valida carajo!!!')

        # If we don't find the file, abort
        if not os.path.isfile(self.filepath):
            raise click.ClickException(INSULT_NAME + ' pelotudo!! No existe ese archivo, de que pija me hablas?')

        if self.extension[1:] in IMAGE_EXTENSIONS + VIDEO_EXTENSIONS:
            print('Recognized file: ' + self.filepath)

        # If we don't support the file self.extension, abort
        else:
            raise click.ClickException(INSULT_NAME + ' pelotudo!! Esa extension no es soportada carajo!')

        # If the file is an image
        if self.extension[1:] in IMAGE_EXTENSIONS:
            self._set_up_image()

        # If the file is a video
        else:
            self._set_up_video()

        text.print_success('exported file with watermark successfully')

    def _set_up_image(self):
        print('Making image...')

        img = Image.open(self.filepath)
        draw = ImageDraw.Draw(img)

        # Getting the list of all fonts in directory, to get the first occurrence
        font_path = glob.glob('*.ttf')

        if len(font_path) > 0:
            font_path = font_path[0] # Get first occurrence
            font = ImageFont.truetype(font=font_path, size=self.size)
        
        # In case no font is found in the directory
        else:
            text.print_warning('no font in directory, choosing a better-than-nothing font')

            font = ImageFont.load_default()

        # Default, in case the below if statements for any reason don't run (could be that you added more options into SUPPORTED_X or SUPPORTED_Y)
        # For default, we set the position to left and top
        position_x, position_y = 0 + TEXT_MARGIN, 0 + TEXT_MARGIN

        # Doing some calculus in order to position the text correctly
        if self.x in ('center', 'right'):
            img_size_x = img.size[0]
            text_size_x = draw.textsize(WATERMARK, font=font)[0]

            if self.x == 'center':
                position_x = img_size_x // 2 - text_size_x // 2

            else:
                position_x = img_size_x - text_size_x - TEXT_MARGIN

        elif self.x != 'left':
            text.print_warning('couldnt set X position, setting to 0. Check SUPPORTED_X global')

        if self.y in ('center', 'bottom'):
            img_size_y = img.size[1]
            text_size_y = draw.textsize(WATERMARK, font=font)[1]

            if self.y == 'center':
                position_y = img_size_y // 2 - text_size_y // 2

            else:
                position_y = img_size_y - text_size_y - TEXT_MARGIN

        elif self.y != 'top':
            text.print_warning('couldnt set Y position, setting to 0. Check SUPPORTED_Y global')

        position = position_x, position_y

        draw.text(position, WATERMARK, SUPPORTED_COLORS.get(self.color, (255, 255, 255)), font=font)

        img = img.convert('RGB')

        def export(as_path=False):
            if as_path:
                img.save(self.filename + '.' + IMAGE_EXPORT_EXTENSION)

                return

            img.save(OUTPUT_NAME + '.' + IMAGE_EXPORT_EXTENSION)

        self.export = export

    def _set_up_video(self):
        print('Making video...')

        clip = editor.VideoFileClip(self.filepath)

        txt_clip = editor.TextClip(WATERMARK, fontsize=self.size, color=self.color).set_position(self.xy).set_duration(clip.duration)

        final_clip = editor.CompositeVideoClip([clip, txt_clip])

        def export(as_path=False):
            if as_path:
                final_clip.write_videofile(self.filename + '.' + VIDEO_EXPORT_EXTENSION)

                return

            final_clip.write_videofile(OUTPUT_NAME + '.' + VIDEO_EXPORT_EXTENSION)

        self.export = export

@click.command()
@click.option('-c', '--color', default='white', type=click.Choice(list(SUPPORTED_COLORS)), help='Specify the color of the watermark. ')
@click.option('--xy', default=('left', 'top'), type=(str, str), help='Specify the XY coordinates of the watermark. ')
@click.option('-s', '--size', default=25, help='Specify the size of the text. ')
@click.argument('filepath')
def main(filepath, color, xy, size):
    f = Watermark(filepath, color, xy, size)
    f.export()
    
if __name__ == '__main__':
    main()
