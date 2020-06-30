# Developer: Martin Nieva (nievadev in GitHub)

from PIL import ImageDraw, ImageFont, Image
from moviepy import editor
from . import Color
import glob
import os

text = Color()

EXCEPTION_FILES = 'test.png', 'geckodriver.log',


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
    OUTPUT_NAME = 'result'
    IMAGE_EXTENSIONS = 'png', 'jpg', 'jpeg'
    IMAGE_EXPORT_EXTENSION = 'jpg'
    VIDEO_EXTENSIONS = 'mp4', 'gif', 'webm'
    VIDEO_EXPORT_EXTENSION = 'mp4'
    DELETE_EXTENSIONS = IMAGE_EXTENSIONS + VIDEO_EXTENSIONS + ('log', )
    VALID_EXTENSIONS = IMAGE_EXTENSIONS + VIDEO_EXTENSIONS
    WATERMARK = '@el.rincon.voxero'
    TEXT_MARGIN = 4
    SUPPORTED_X = 'left', 'center', 'right'
    SUPPORTED_Y = 'top', 'center', 'bottom'
    SUPPORTED_COLORS = {
        'black': (0, 0, 0),
        'white': (255, 255, 255),
        'red': (255, 0, 0),
        'blue': (0, 0, 255),
        'green': (0, 255, 0)
    }

    def __init__(self, filepath, color, xy, size, options=dict()):
        """Apply watermark to photo or video tool"""

        self.xy = xy
        self.color = color
        self.filepath = filepath
        self.filename, self.extension = os.path.splitext(self.filepath)
        self.size = size

        self.export_as_name = options.get('export_as_name', Watermark.OUTPUT_NAME)

        def export():
            pass

        self.export = export

        if self.filepath == 'clean':
            print('Cleaning...')

            for filetype in Watermark.DELETE_EXTENSIONS:
                clean_files(filetype)

            text.print_success('done')
            return

        # Checking the XY is supported
        self.x, self.y = self.xy[0], self.xy[1]

        if self.x not in Watermark.SUPPORTED_X:
            m = self.x + 'option is not valid'
            text.print_error(m)
            quit()

        if self.y not in Watermark.SUPPORTED_Y:
            m = self.y + 'option is not valid'
            text.print_error(m)
            quit()

        # If we don't find the file, abort
        if not os.path.isfile(self.filepath):
            m = 'didnt find the file ' + self.filepath
            text.print_error(m)
            quit()

        if self.extension[1:] in Watermark.VALID_EXTENSIONS:
            print('Recognized file: ' + self.filepath)

        # If we don't support the file self.extension, abort
        else:
            m = 'extension ' + self.extension + ' not supported'
            text.print_error(m)
            quit()

        # If the file is an image
        if self.extension[1:] in Watermark.IMAGE_EXTENSIONS:
            self._set_up_image()

        # If the file is a video
        else:
            self._set_up_video()

        text.print_success('exported file with watermark successfully')

    def _set_up_image(self):
        print('Making image...')

        img = Image.open(self.filepath)
        draw = ImageDraw.Draw(img)

        # Getting the first ocurrence of all ttf files in the directory
        font_path = glob.glob('*.ttf')

        if len(font_path) > 0:
            # Get first occurrence
            font_path = font_path[0]
            font = ImageFont.truetype(font=font_path, size=self.size)

        # In case no font is found in the directory
        else:
            m = 'no font in directory, choosing a better-than-nothing font'
            text.print_warning(m)

            font = ImageFont.load_default()

        # Default, in case the below if statements for any reason don't run
        # (you may have added more options into SUPPORTED_X or SUPPORTED_Y)
        # For default, we set the position to left and top
        position_x = 0 + Watermark.TEXT_MARGIN
        position_y = 0 + Watermark.TEXT_MARGIN

        # Doing some calculus in order to position the text correctly
        if self.x in ('center', 'right'):
            img_size_x = img.size[0]
            text_size_x = draw.textsize(Watermark.WATERMARK, font=font)[0]

            if self.x == 'center':
                position_x = img_size_x // 2 - text_size_x // 2

            else:
                position_x = img_size_x - text_size_x - Watermark.TEXT_MARGIN

        elif self.x != 'left':
            m = 'couldnt set X position, setting to 0. Check SUPPORTED_X'
            text.print_warning(m)

        if self.y in ('center', 'bottom'):
            img_size_y = img.size[1]
            text_size_y = draw.textsize(Watermark.WATERMARK, font=font)[1]

            if self.y == 'center':
                position_y = img_size_y // 2 - text_size_y // 2

            else:
                position_y = img_size_y - text_size_y - Watermark.TEXT_MARGIN

        elif self.y != 'top':
            m = 'couldnt set Y position, setting to 0. Check SUPPORTED_Y'
            text.print_warning(m)

        position = position_x, position_y

        draw.text(
            position,
            Watermark.WATERMARK,
            Watermark.SUPPORTED_COLORS.get(self.color, (255, 255, 255)),
            font=font
        )

        img = img.convert('RGB')

        def export(export_as_path=False):
            if export_as_path:
                _as = f'{self.filename}.{Watermark.IMAGE_EXPORT_EXTENSION}'

                if not _as == self.filepath:
                    os.remove(self.filepath)

            else:
                _as = f'{self.export_as_name}.{Watermark.IMAGE_EXPORT_EXTENSION}'

            img.save(_as)

        self.export = export

    def _set_up_video(self):
        print('Making video...')

        clip = editor.VideoFileClip(self.filepath)

        txt_clip = editor.TextClip(
            Watermark.WATERMARK,
            fontsize=self.size,
            color=self.color
        )

        txt_clip = txt_clip.set_position(self.xy).set_duration(clip.duration)

        final_clip = editor.CompositeVideoClip([clip, txt_clip])

        def export(export_as_path=False):
            if export_as_path:
                _as = f'{self.filename}.{Watermark.VIDEO_EXPORT_EXTENSION}'
                final_clip.write_videofile(_as)

                return

            _as = f'{self.export_as_name}.{Watermark.VIDEO_EXPORT_EXTENSION}'
            final_clip.write_videofile(_as)

        self.export = export
