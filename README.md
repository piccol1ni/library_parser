# Программа по парсингу книг из библиотеки
1. Скрипт помогает скачать книги и их обложки.
2. Собирает всю нужную информацию по книгам которыми вы заинтересовались!

## Как запустить программу
1. Вам необходимо скачать проект себе на компьютер, при помощи команды :
```
git clone git@github.com:piccol1ni/library_parser.git
```
2. После установки рабочего проекта на свой компьютер, необходимо подтянуть все актуальные библиотеки, которые понадобятся для работы, командой :
```
pip install -r requirements.txt
```
3. После установки всего вышеперечисленного на свой компьютер, запустите программу командой :
```
python3 library_file.py 1 11
```
Если вы не хотите загрязнять свой компьютер лишними библиотеками, воспользуйтесь [виртуальным окружением](https://habr.com/ru/post/157287/).

## start и end

При запуске программы нужно указать обязательно 2 аргумента, они обозначают начальную и конечную стьраничку, с которой программа будет скачивать книги.

## --dest_folder, --skip_img, --skip_txt, --json_path
Опционные аргументы, которые нужно явно указывать как в примере :
```
python3 library_file.py 1 11 --dest_folder home/test --skip_img True --skip_txt True --json_path home/test/json_files
```
1. dest_folder - ваш кастомнгый путь к папке, где будут храниться скаченные книги, обложки и json файл! Если путь не указать, файлы сохранятся в папке откуда был запущен скрипт!
2. skip_img - запустить скрипт без скачиввания обложек, работает только если указать True, как в примере.
3. skip_txt - запустить скрипт без скачиввания книг, работает только если указать True, как в примере.
4. json_path - ваш кастомный путь к папке, где будет храниться json файл со всеми скаченными книгами! Если путь не указать, файлы сохранятся в папке откуда был запущен скрипт!

