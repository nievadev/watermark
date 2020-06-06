# Developer: Martin Nieva (nievadev in GitHub)
from PIL import ImageDraw, ImageFont, Image
from moviepy import editor
import click
import glob
import os
import sys

IMAGE_EXTENSIONS = 'png', 'jpg', 'jpeg'
TEXT_MARGIN = 4
VIDEO_EXTENSIONS = 'mp4', 'gif', 'webm'
OUTPUT_NAME = 'result.mp4'
WATERMARK = '@voxed.gram'
SUPPORTED_X = ('left', 'center', 'right')
SUPPORTED_Y = ('top', 'center', 'bottom')
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
        print('Deleting ' + _file + '... ')

        os.remove(_file)

    print('Done!')

@click.command()
@click.option('-c', '--color', default='white', type=click.Choice(list(SUPPORTED_COLORS)), help='Specify the color of the watermark. ')
@click.option('--xy', default=('left', 'top'), type=(str, str), help='Specify the XY coordinates of the watermark. ')
@click.option('-s', '--size', default=25, help='Specify the size of the text. ')
@click.argument('filepath')
def apply_watermark(filepath, color, xy, size):
    """Apply watermark to photo or video tool"""

    if filepath == 'clean':
        print('Cleaning...')

        for filetype in IMAGE_EXTENSIONS + VIDEO_EXTENSIONS:
            clean_files(filetype)

        print('Done. ')
        return

    # Getting file metadata
    filename, extension = os.path.splitext(filepath)
    file_ = filename + extension

    # Checking the XY is supported
    x, y = xy[0], xy[1]

    if x not in SUPPORTED_X:
        raise click.ClickException('Ignacio pelotudo!! La opcion ' + x + ' no es valida carajo!!!')

    if y not in SUPPORTED_Y:
        raise click.ClickException('Ignacio pelotudo!! La opcion ' + y + ' no es valida carajo!!!')

    # If we don't find the file, abort
    if not os.path.isfile(file_):
        raise click.ClickException('Ignacio pelotudo!! No existe ese archivo, de que pija me hablas?')

    if extension[1:] in IMAGE_EXTENSIONS + VIDEO_EXTENSIONS:
        print('Filename: ' + file_)

    # If we don't support the file extension, abort
    else:
        raise click.ClickException('Ignacio pelotudo!! Esa extension no es soportada carajo!')

    # If the file is an image
    if extension[1:] in IMAGE_EXTENSIONS:
        print('Making image...')

        img = Image.open(file_)
        draw = ImageDraw.Draw(img)

        # Getting the list of all fonts in directory, to get the first occurrence
        font_path = glob.glob('*.ttf')

        if len(font_path) > 0:
            font_path = font_path[0] # Get first occurrence
            font = ImageFont.truetype(font=font_path, size=size)
        
        # In case no font is found in the directory
        else:
            print('Warning: no font in directory, choosing a better-than-nothing font.')
            font = ImageFont.load_default().font

        # Default, in case the below if statements for any reason don't run (could be that you added more options into SUPPORTED_X or SUPPORTED_Y)
        # For default, we set the position to left and top
        position_x, position_y = 0 + TEXT_MARGIN, 0 + TEXT_MARGIN

        # Doing some calculus in order to position the text correctly
        if x in ('center', 'right'):
            img_size_x = img.size[0]
            text_size_x = draw.textsize(WATERMARK, font=font)[0]

            if x == 'center':
                position_x = img_size_x // 2 - text_size_x // 2

            else:
                position_x = img_size_x - text_size_x - TEXT_MARGIN

        elif x != 'left':
            print('Warning: couldnt set X position, setting to 0. Check SUPPORTED_X global.')

        if y in ('center', 'bottom'):
            img_size_y = img.size[1]
            text_size_y = draw.textsize(WATERMARK, font=font)[1]

            if y == 'center':
                position_y = img_size_y // 2 - text_size_y // 2

            else:
                position_y = img_size_y - text_size_y - TEXT_MARGIN

        elif y != 'top':
            print('Warning: couldnt set Y position, setting to 0. Check SUPPORTED_Y global.')

        position = position_x, position_y

        draw.text(position, WATERMARK, SUPPORTED_COLORS.get(color, (255, 255, 255)), font=font)
        img.save('result' + extension)

    # If the file is a video
    else:
        print('Making video...')

        clip = editor.VideoFileClip(file_)

        txt_clip = editor.TextClip(WATERMARK, fontsize=size, color=color).set_position(xy).set_duration(clip.duration)

        final_clip = editor.CompositeVideoClip([clip, txt_clip])
        final_clip.write_videofile(OUTPUT_NAME)

    print('Done!')

if __name__ == '__main__':
    apply_watermark()
