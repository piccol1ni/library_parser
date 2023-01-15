import requests
from bs4 import BeautifulSoup
import lxml
import library_file


def check_for_redirect(response):
    if response.history != []:
        raise requests.HTTPError('ERROR!!!!')

def main():
    for id in range(1, 11):
        response = requests.get(f'https://tululu.org/b{id}')
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'lxml')
        try:
            print(f"Заголовок: {library_file.title_author_parser(id)}\nhttps://tululu.org{soup.find(class_='bookimage').find('img')['src']}")
            print()

            for comment in soup.find_all(class_='texts'):
                print(comment.find(class_='black').text)
            print()
        except:
            pass


if __name__=='__main__':
    main()