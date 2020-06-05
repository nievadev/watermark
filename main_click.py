import click

@click.command()
@click.option('--video', default=False, help='Write this option in case the file you are gonna specify is a video')
@click.option('--image', default=False, help='Write this option in case the file you are gonna specify is a image')
@click.argument('filepath')
def filename(image, video, filepath):
    return

filename()
