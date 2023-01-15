import requests
from bs4 import BeautifulSoup
import lxml

def main():
    response = requests.get('https://www.franksonnenbergonline.com/')
    soup = BeautifulSoup(response.text, 'lxml')
    print(soup.find(class_='entry-title-link').text)
    print(soup.find(class_='alignleft post-image entry-image')['src'])
    print(soup.find(class_='entry-content').find('p').text)


if __name__=='__main__':
    main()