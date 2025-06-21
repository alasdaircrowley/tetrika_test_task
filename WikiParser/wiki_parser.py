import requests
from bs4 import BeautifulSoup
import time

BASE_URL = 'https://ru.wikipedia.org'
START_URL = f'{BASE_URL}/wiki/Категория:Животные_по_алфавиту'
RUSSIAN_LETTERS = "АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ"
REQUEST_DELAY = 0.5
MAX_PAGES = 100


def fetch_page(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при загрузке страницы: {e}")
        return None


def parse_page(html):
    if not html:
        return [], None

    soup = BeautifulSoup(html, 'html.parser')
    content_div = soup.find('div', id='mw-pages')

    if not content_div:
        return [], None

    groups = content_div.find_all('div', class_='mw-category-group')
    data = []
    found_ya = False

    for group in groups:
        header = group.find('h3')
        if not header:
            continue

        letter = header.text.strip()
        if letter:
            letter = letter[0]

        if letter in RUSSIAN_LETTERS:
            animals = group.find_all('li')
            count = 0

            for animal in animals:
                if not animal.find('a', href=lambda x: x and 'Категория:' in x):
                    count += 1

            if count > 0:
                data.append((letter, count))
                if letter == 'Я':
                    found_ya = True

    next_link = content_div.find('a', string='Следующая страница')
    next_url = BASE_URL + next_link['href'] if next_link and 'href' in next_link.attrs else None

    return data, next_url, found_ya


def process_category(start_url):
    animal_counts = {}
    url = start_url
    page_count = 0
    ya_found = False

    while url and page_count < MAX_PAGES:
        page_count += 1
        print(f"\nСтраница {page_count}")

        html = fetch_page(url)
        if not html:
            break

        data, next_url, found_ya = parse_page(html)

        for letter, count in data:
            animal_counts[letter] = animal_counts.get(letter, 0) + count
            print(f"  Буква {letter}: {count} животных")

        if found_ya:
            ya_found = True

        if ya_found and not found_ya:
            print("Достигнут конец категории (последняя буква Я)")
            break

        if found_ya and not next_url:
            print("Достигнут конец категории (последняя буква Я)")
            break

        url = next_url
        time.sleep(REQUEST_DELAY)

    return animal_counts, page_count


def save_results(animal_counts, filename):
    sorted_letters = sorted(animal_counts.items(), key=lambda x: RUSSIAN_LETTERS.index(x[0]))

    with open(filename, 'w', encoding='utf-8') as f:
        for letter, count in sorted_letters:
            f.write(f"{letter},{count}\n")

    return len(animal_counts)


def main():
    print("Начинаю сбор данных о животных...")
    animal_counts, page_count = process_category(START_URL)

    if animal_counts:
        letters_count = save_results(animal_counts, 'beasts.csv')
        print("\nГотово! Результаты сохранены в beasts.csv")
        print(f"Обработано страниц: {page_count}")
        print(f"Найдено букв: {letters_count}")
        print(f"Всего животных: {sum(animal_counts.values())}")
    else:
        print("Не удалось собрать данные")


if __name__ == '__main__':
    main()