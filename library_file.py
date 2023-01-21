import os
import requests
import argparse
from tqdm import tqdm
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import lxml
from time import sleep
from pathvalidate import sanitize_filename


def check_for_redirect(response):
    """
    Check if url for request can be downloaded and not redirect on main page
    """
    if response.history:
        raise requests.exceptions.HTTPError('Not a book page!')


def check_genre():
    """
    Check if 'Научная фантастика' in geners!
    """
    if 'Научная фантастика' not in book_page['genres']:
        raise requests.exceptions.HTTPError('Not a valid genre!')


def download_txt(response, filename, folder='books/'):
    """
    Download books texts
    """
    os.makedirs(folder, exist_ok=True)
    filename = sanitize_filename(filename)
    file_path = os.path.join(folder, filename)
    with open(file_path, 'wb') as file:
        file.write(response.content)
    return file_path


def download_img(image_url, folder='images/'):
    """
    Download books images
    """
    response = requests.get(image_url)
    response.raise_for_status()
    os.makedirs(folder, exist_ok=True)
    image_name = sanitize_filename(urlparse(image_url).path)
    file_path = os.path.join(folder, image_name)
    with open(file_path, 'wb') as file:
        file.write(response.content)
    return file_path


def parse_book_page(response, book_number = 0):
    """
    Parse whole info about book
    """
    soup = BeautifulSoup(response.text, 'lxml')
    title_and_author = soup.find(class_='ow_px_td').find('h1').text.split('::')
    book_title, book_author = [*title_and_author]
    image_address = soup.find(class_='bookimage').find('img')['src']
    genres = soup.find('span', class_='d_book').text.split(':')
    genres = genres[1].strip().split(',')
    comments = [comment.find(class_='black').text for comment in soup.find_all(class_='texts')]
    book = {
        'title': f"{book_number}. {book_title.strip()}",
        'author': book_author.strip(),
        'genres': genres,
        'image': urljoin(f"https://tululu.org/b{book_number}", f"//{image_address}"),
        'comments': comments,
    }
    print(book)
    return book


def main():
    global book_page
    parser = argparse.ArgumentParser(description='Напишите id книг по которым вы будете искать информацию! И скачивать их.')
    parser.add_argument('start', help='С какой книги будете искать?')
    parser.add_argument('end', help='До какой книги будете искать?')
    args = parser.parse_args()
    for book_number in tqdm(range(int(args.start), int(args.end))):
        text_page_params = {
            'id': book_number,
        }
        try:
            response_book_page = requests.get(f"https://tululu.org/b{book_number}")
            response_book_page.raise_for_status()
            check_for_redirect(response_book_page)
            response_text_page = requests.get(f"https://tululu.org/txt.php", params=text_page_params)
            response_text_page.raise_for_status()
            check_for_redirect(response_text_page)
            book_page = parse_book_page(response_book_page, book_number)
            check_genre()
            download_txt(response_text_page, book_page['title'])
            download_img(book_page['image'])
        except(requests.exceptions.HTTPError, requests.exceptions.ConnectionError) as ex:
            sleep(100)
            print(ex)


if __name__=='__main__':
    main()