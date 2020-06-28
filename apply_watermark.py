import click
from lib import Watermark


@click.command()
@click.option(
    '-c', '--color',
    default='white',
    type=click.Choice(list(Watermark.SUPPORTED_COLORS)),
    help='Specify the color of the watermark. '
)
@click.option(
    '--xy',
    default=('left', 'top'),
    type=(str, str),
    help='Specify the XY coordinates of the watermark. '
)
@click.option(
    '-s', '--size',
    default=25,
    help='Specify the size of the text. '
)
@click.argument('filepath')
def main(filepath, color, xy, size):
    f = Watermark(filepath, color, xy, size)
    f.export()


if __name__ == '__main__':
    main()
