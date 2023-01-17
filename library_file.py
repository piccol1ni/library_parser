import os
import requests
import argparse
from tqdm import tqdm
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import lxml
from time import sleep
from pathvalidate import sanitize_filename

def defeat_cpu(book_number, ex):
    internet_status = False
    while not internet_status:
        response = requests.get(f'https://tululu.org/b{book_number}')
        try:
            response.raise_for_status()
            internet_status = True
        except(requests.exceptions.HTTPError, requests.exceptions.ConnectionError):
            print(ex)
            sleep(10)


def check_for_redirect(response):
    """
    Check if url for request can be downloaded and not redirect on main page
    """
    if response.history:
        raise requests.exceptions.HTTPError('Not a book page!')


def check_genre(response):
    """
    Check if 'Научная фантастика' in geners!
    """
    soup = BeautifulSoup(response.text, 'lxml')
    genres = soup.find('span', class_='d_book').text.split(':')
    genres = genres[1].strip().split(',')
    if 'Научная фантастика' not in genres:
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


def download_img(response, folder='images/'):
    """
    Download books images
    """
    soup = BeautifulSoup(response.text, 'lxml')
    response = requests.get(f"https://tululu.org{soup.find(class_='bookimage').find('img')['src']}")
    response.raise_for_status()
    os.makedirs(folder, exist_ok=True)
    image_name = sanitize_filename(soup.find(class_='bookimage').find('img')['src'])
    file_path = os.path.join(folder, image_name)
    with open(file_path, 'wb') as file:
        file.write(response.content)
    return file_path


def read_comments(response):
    """
    Download all comments for each book
    """
    soup = BeautifulSoup(response.text, 'lxml')
    for comment in soup.find_all(class_='texts'):
        print(comment.find(class_='black').text)


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
    one_book_information = {
        'title': f"{book_number}. {book_title.strip()}",
        'author': book_author.strip(),
        'genres': genres,
        'image': urljoin('https://tululu.org', image_address),
    }
    return one_book_information['title']


def main():
    parser = argparse.ArgumentParser(description='Напишите id книг по которым вы будете искать информацию! И скачивать их.')
    parser.add_argument('start', help='С какой книги будете искать?')
    parser.add_argument('end', help='До какой книги будете искать?')
    args = parser.parse_args()
    for book_number in tqdm(range(int(args.start), int(args.end))):
        params_text_page = {
            'txt.php': '',
            'id': book_number,
        }
        try:
            response_book_page = requests.get(f"https://tululu.org/b{book_number}")
            response_text_page = requests.get(f"https://tululu.org/", params=params_text_page)
        except(requests.exceptions.HTTPError, requests.exceptions.ConnectionError) as ex:
            defeat_cpu(book_number, ex)

        try:
            check_for_redirect(response_text_page)
            check_genre(response_book_page)
        except(requests.exceptions.HTTPError):
            continue
        parse_book_page(response_book_page)
        download_txt(response_text_page, parse_book_page(response_book_page, book_number))
        download_img(response_book_page)
        read_comments(response_book_page)


if __name__=='__main__':
    main()