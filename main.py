from bs4 import BeautifulSoup as bs
import os
import requests

def download_image(image_url, export_as='downloaded'):
    filename = os.path.basename(image_url)

    name, extension = os.path.splitext(filename)

    response = requests.get(image_url)

    if not response.status_code == 200:
        return

    with open(export_as + extension, 'wb') as f:
        for chunk in response:
            f.write(chunk)

def main():
    image_url = 'https://upload.voxed.net/SmF9oeVRnrH98KQKfShq.jpg'

    download_image(image_url, 'heyitworksaaaa')

if __name__ == '__main__':
    main()
