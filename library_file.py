import os
import requests


#os.mkdir('books')
for id in range(1, 11):
    response = requests.get(f"https://tululu.org/txt.php?id={id}")
    response.raise_for_status()

    with open(f'books/book{id}.txt', 'wb') as file:
        file.write(response.content)