import urllib.parse

import requests
from bs4 import BeautifulSoup
import lxml

from library_file import check_for_redirect


def main():
    number_of_page = 1
    while True:
        if number_of_page == 10:
            return f'hi'
        response = requests.get('https://tululu.org/l55/'+ str(number_of_page))
        response.raise_for_status()
        check_for_redirect(response)
        soup = BeautifulSoup(response.text, 'lxml')
        book_links = []
        for link in soup.find_all(class_='bookimage'):
            book_links.append(link.find('a')['href'][2:-1])
        print(book_links)
        number_of_page += 1

if __name__=='__main__':
    main()