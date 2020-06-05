from moviepy import editor
import sys
import glob
import os

OUTPUT_NAME = 'result.mp4'
LEN_ARGS = 5

clean_filetypes = 'webm', 'mp4', 'gif', 'png', 'jpg', 'jpeg'

def clean_files(filetype):
    for file in glob.glob('*.' + filetype):
        print('Deleting ' + file + '... ')

        os.remove(file)

        print('Done!')

    return

def main(args):
    if len(args) != LEN_ARGS:
        if args[1] == 'clean':
            print('Cleaning...')

            for filetype in clean_filetypes:
                clean_files(filetype)

            return True, 'Success!'

        return False, 'Ignacio you dumbass! You havent written the arguments properly! Domaditowwwnnn'

    text_size = 25

    text_x = args[1]
    text_y = args[2]
    text_color = args[3]
    video_name = args[4]

    print('Video: ' + video_name)

    if len(args) == LEN_ARGS + 1:
        text_size = args[LEN_ARGS]

    text_anchor = text_x, text_y

    clip = editor.VideoFileClip(video_name)

    txt_clip = editor.TextClip('@voxed.gram', fontsize=text_size, color=text_color).set_position(text_anchor).set_duration(clip.duration)

    final_clip = editor.CompositeVideoClip([clip, txt_clip])

    final_clip.write_videofile(OUTPUT_NAME)

    return True, 'Success!'

if __name__ == '__main__':
    success, reason = main(sys.argv)

    print(reason)
