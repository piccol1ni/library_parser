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

from custom_exceptions import NoTextError, NotValidHenre, NotValidPath


def check_for_redirect(response):
    """
    Check if url for request can be downloaded and not redirect on main page
    """
    if response.history:
        raise NoTextError('Not a book page!')

def check_for_correct_path(path):
    if path and path[-1] != '/':
        raise NotValidPath


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
    response.raise_for_status()
    check_for_redirect(response)
    soup = BeautifulSoup(response.text, 'lxml')
    selector_links = "div.bookimage"
    selector_number_of_link = "a"
    book_links = []
    for link in soup.select(selector_links):
        book_links.append(link.select_one(selector_number_of_link)['href'][2:-1])
    return book_links


def download_json_file(path_to_file):
    with open(f'{path_to_file}all_books_info.json', 'w') as file:
        json.dump(all_parsed_books, file, indent=4, ensure_ascii=False)


def download_books(page_start_number, page_end_number):
    for page_number in range(page_start_number, page_end_number + 1):
        try:
            for book_number in get_book_links(page_number):
                text_page_params = {
                    'id': book_number,
                }
                try:
                    response_book_page = requests.get(f"https://tululu.org/b{book_number}/")
                    response_book_page.raise_for_status()
                    check_for_redirect(response_text_page)
                    response_text_page = requests.get(f"https://tululu.org/txt.php", params=text_page_params)
                    response_text_page.raise_for_status()
                    check_for_redirect(response_text_page)
                    book_page = parse_book_page(response_book_page, book_number)
                    all_parsed_books.append(book_page)
                    if not args.skip_txt:
                        download_txt(response_text_page, book_page['title'], f'{args.dest_folder}books')
                    if not args.skip_img:
                        download_img(book_page['image'], f'{args.dest_folder}images')
                except (requests.exceptions.HTTPError, requests.exceptions.ConnectionError) as ex:
                    print(ex)
                    sleep(100)
                except(NoTextError, NotValidHenre) as ex:
                    print(ex)
        except (requests.exceptions.HTTPError, requests.exceptions.ConnectionError) as ex:
            print(ex)
            sleep(100)


if __name__=='__main__':
    parser = argparse.ArgumentParser(description='???????????????? ???????????????? ????????, ?? ?????????????? ???? ???????????? ?????????????????? ??????????')
    parser.add_argument('--start', help='?? ?????????? ?????????????????? ???????????? ?????????????', type=int, default=1)
    parser.add_argument('--end', help='???? ?????????? ?????????????????? ???????????? ?????????????', type=int, default=10)
    parser.add_argument('--dest_folder', help='?????????????? ???????? ?? ???????????????? ?? ???????????????????????? ???????????????? ????????????????, ????????, json, ???????????????? ?? ?????????? "/"', default='')
    parser.add_argument('--skip_img', help='???? ?????????????????? ????????????????, ???????????? True, default=False', action='store_true')
    parser.add_argument('--skip_txt', help='???? ?????????????????? ??????????, ???????????? True, default=False', action='store_true')
    parser.add_argument('--json_path', help='?????????????? ???????? ???????? ?? json, ???????????????? ?? ?????????? "/"', default='')
    args = parser.parse_args()
    all_parsed_books = []
    page_start_number = args.start
    page_end_number = args.end
    page_number = copy.copy(page_start_number)
    folder_with_all_books = args.dest_folder
    folder_with_json_file = args.json_path
    check_for_correct_path(folder_with_all_books)
    check_for_correct_path(folder_with_json_file)
    download_books(page_start_number, page_end_number)
    if folder_with_json_file:
        download_json_file(folder_with_json_file)
    elif folder_with_all_books:
        download_json_file(folder_with_all_books)