import os
import requests
from bs4 import BeautifulSoup
import lxml
from pathvalidate import sanitize_filename

def check_for_redirect(response):
    if response.history != []:
        raise requests.HTTPError('ERROR!!!!')

def download_txt(url, filename, folder='books/'):
    response = requests.get(url)
    response.raise_for_status()
    os.makedirs(folder, exist_ok=True)
    filename = sanitize_filename(filename)
    with open(f'{folder}{filename}', 'wb') as file:
        file.write(response.content)
    return os.path.join(folder, filename)

def download_img(url, folder='images/'):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'lxml')
    response = requests.get(f"https://tululu.org{soup.find(class_='bookimage').find('img')['src']}")
    os.makedirs(folder, exist_ok=True)
    image_name = sanitize_filename(soup.find(class_='bookimage').find('img')['src'])
    with open(f"{folder}{image_name}", 'wb') as file:
        file.write(response.content)
    return os.path.join(folder, image_name)


def title_author_parser(id):
    response = requests.get(f'https://tululu.org/b{id}/')
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'lxml')
    title_and_author = soup.find(class_='ow_px_td').find('h1').text.split('::')
    book_title = title_and_author[0].strip()
    return f'{id}. {book_title}'


def main():
    for id in range(1, 11):
        response = requests.get(f"https://tululu.org/txt.php?id={id}")
        response.raise_for_status()
        try:
            check_for_redirect(response)
            download_txt(f"https://tululu.org/txt.php?id={id}", title_author_parser(id))
            download_img(f'https://tululu.org/b{id}')
        except:
            pass


if __name__=='__main__':
    main()