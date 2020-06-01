from moviepy import editor

FILE_NAME = 'example.mp4'
OUTPUT_NAME = 'final.mp4'

clip = editor.VideoFileClip(FILE_NAME)

txt_clip = editor.TextClip('@voxed.gram', fontsize=30, color='white').set_pos('center').set_duration(10)

final_clip = editor.CompositeVideoClip([clip, txt_clip])

final_clip.write_videofile(OUTPUT_NAME)
