import os
import requests
import argparse
from tqdm import tqdm
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import lxml
from time import sleep
import urllib.parse
from pathvalidate import sanitize_filename
import json
import copy

from custom_exceptions import NoTextError, NotValidHenre


def check_for_redirect(response):
    """
    Check if url for request can be downloaded and not redirect on main page
    """
    if response.history:
        raise NoTextError('Not a book page!')


def check_genre(book_page):
    """
    Check if 'Научная фантастика' in geners!
    """
    if 'Научная фантастика' not in book_page['genres']:
        raise NotValidHenre('Not a valid genre!')


def download_txt(response, filename, folder='books/'):
    """
    Download books texts
    """
    if args.skip_txt:
        return None
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
    if args.skip_img:
        return None
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
    selector_image_adress = "div.bookimage img"
    image_address = soup.select_one(selector_image_adress)['src']
    selector_genres = "span.d_book"
    genres = soup.select_one(selector_genres).text.split(':')
    genres = genres[1].strip().split(',')
    selector_comment = "span.black"
    selector_comments = "div.texts"
    comments = [comment.select_one(selector_comment).text for comment in soup.select(selector_comments)]
    book = {
        'title': f"{book_number}. {book_title.strip()}",
        'author': book_author.strip(),
        'genres': genres,
        'image': urljoin(f"https://tululu.org/b{book_number}", f"//{image_address}"),
        'comments': comments,
    }
    return book


def get_book_links(page_number):
    response = requests.get(f'https://tululu.org/l55/{str(page_number)}')
    check_for_redirect(response)
    soup = BeautifulSoup(response.text, 'lxml')
    selector_links = "div.bookimage"
    selector_number_of_link = "a"
    book_links = []
    for link in soup.select(selector_links):
        book_links.append(link.select_one(selector_number_of_link)['href'][2:-1])
    page_number += 1
    return book_links


def download_json_file(folder_with_all_books, folder_with_json_file):
    if folder_with_all_books:
        with open(f'{folder_with_all_books}/all_books_info.json', 'w') as file:
            json.dump(all_parsed_books, file, indent=4, ensure_ascii=False)
    else:
        with open('all_books_info.json', 'w') as file:
            json.dump(all_parsed_books, file, indent=4, ensure_ascii=False)
    
    if folder_with_json_file:
        with open(f'{folder_with_json_file}/all_books_info.json', 'w') as file:
            json.dump(all_parsed_books, file, indent=4, ensure_ascii=False)

def download_books(page_number):
    if page_number == args.end + 1:
        return 'STOP!'
    for book_number in get_book_links(page_number):
        text_page_params = {
            'id': book_number,
        }
        try:
            response_book_page = requests.get(f"https://tululu.org/b{book_number}")
            response_book_page.raise_for_status()
            response_text_page = requests.get(f"https://tululu.org/txt.php", params=text_page_params)
            check_for_redirect(response_text_page)
            book_page = parse_book_page(response_book_page, book_number)
            all_parsed_books.append(book_page)
            if args.dest_folder:
                download_txt(response_text_page, book_page['title'], f'{args.dest_folder}/books')
                download_img(book_page['image'], f'{args.dest_folder}/images')
            else:
                download_txt(response_text_page, book_page['title'])
                download_img(book_page['image'])
        except(requests.exceptions.HTTPError, requests.exceptions.ConnectionError) as ex:
            print(ex)
            sleep(100)
        except(NoTextError, NotValidHenre) as ex:
            print(ex)
    page_number+=1
    download_books(page_number)


if __name__=='__main__':
    parser = argparse.ArgumentParser(description='Напишите страницы книг, с которых вы хотите скачивать книги')
    parser.add_argument('start', help='С какой странички будете качать?', type=int)
    parser.add_argument('end', help='До какой странички будете качать?', type=int)
    parser.add_argument('--dest_folder', help='Укажите путь к каталогу с результатами парсинга картинок, книг, json')
    parser.add_argument('--skip_img', help='Не скачивать картинки, пример True, default=False', action='store_true')
    parser.add_argument('--skip_txt', help='Не скачивать книги, пример True, default=False', action='store_true')
    parser.add_argument('--json_path', help='Указать свой путь к json')
    args = parser.parse_args()
    all_parsed_books = []
    page_start_number = args.start
    page_number = copy.copy(page_start_number)
    folder_with_all_books = args.dest_folder
    folder_with_json_file = args.json_path
    download_books(page_number)
    download_json_file(folder_with_all_books, folder_with_json_file)
