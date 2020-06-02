from moviepy import editor
import sys

FILE_NAME = 'toedit.mp4'
OUTPUT_NAME = 'result.mp4'

def main(args):
    if len(args) != 4:
        return False, 'Pelotudo! No escribiste los argumentos bien al iniciar el script!'

    text_size = 25

    text_x = args[1]
    text_y = args[2]
    text_color = args[3]

    if len(args) == 5:
        text_size = args[4]

    text_anchor = text_x, text_y

    clip = editor.VideoFileClip(FILE_NAME)

    txt_clip = editor.TextClip('@voxed.gram', fontsize=text_size, color=text_color).set_position(text_anchor).set_duration(clip.duration)

    final_clip = editor.CompositeVideoClip([clip, txt_clip])

    final_clip.write_videofile(OUTPUT_NAME)

    return True, 'Success!'

if __name__ == '__main__':
    success, reason = main(sys.argv)

    if not success:
        print(reason)
