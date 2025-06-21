from WikiParser import wiki_parser
from wiki_parser import parse_page, save_results, main
import os

HTML_SIMPLE = """
<div id="mw-pages">
    <div class="mw-category-group">
        <h3>А</h3>
        <ul>
            <li><a href="/wiki/Аист">Аист</a></li>
            <li><a href="/wiki/Акула">Акула</a></li>
        </ul>
    </div>
    <div class="mw-category-group">
        <h3>Б</h3>
        <ul>
            <li><a href="/wiki/Барсук">Барсук</a></li>
        </ul>
    </div>
</div>
"""

HTML_WITH_CATEGORY = """
<div id="mw-pages">
    <div class="mw-category-group">
        <h3>В</h3>
        <ul>
            <li><a href="/wiki/Волк">Волк</a></li>
            <li><a href="/wiki/Категория:Волчьи">Волчьи</a></li>
        </ul>
    </div>
</div>
"""

HTML_WITH_NEXT_PAGE = """
<div id="mw-pages">
    <div class="mw-category-group">
        <h3>Г</h3>
        <ul>
            <li><a href="/wiki/Гепард">Гепард</a></li>
        </ul>
    </div>
    <a href="/next_page">Следующая страница</a>
</div>
"""


def test_parse_page_simple():
    animals, next_page, found_ya = parse_page(HTML_SIMPLE)

    assert len(animals) == 2
    assert animals[0][0] == 'А'
    assert animals[0][1] == 2
    assert animals[1][0] == 'Б'
    assert animals[1][1] == 1
    assert next_page is None
    assert found_ya is False


def test_parse_page_with_category():
    animals, next_page, found_ya = parse_page(HTML_WITH_CATEGORY)
    assert len(animals) == 1
    assert animals[0][0] == 'В'
    assert animals[0][1] == 1
    assert found_ya is False


def test_parse_page_with_ya():
    """Тест разбора страницы с буквой Я"""
    html_with_ya = """
    <div id="mw-pages">
        <div class="mw-category-group">
            <h3>Я</h3>
            <ul>
                <li><a href="/wiki/Ягуар">Ягуар</a></li>
            </ul>
        </div>
    </div>
    """

    animals, next_page, found_ya = parse_page(html_with_ya)

    assert len(animals) == 1
    assert animals[0][0] == 'Я'
    assert animals[0][1] == 1
    assert next_page is None
    assert found_ya is True

def test_parse_page_with_next_page():
    """Тест разбора страницы со ссылкой"""
    animals, next_page, found_ya = parse_page(HTML_WITH_NEXT_PAGE)

    # Проверяем группу
    assert len(animals) == 1
    assert animals[0][0] == 'Г'
    assert animals[0][1] == 1

    assert next_page == "https://ru.wikipedia.org/next_page"
    assert found_ya is False


def test_save_results():
    test_data = {'А': 5, 'Б': 3, 'В': 7}

    save_results(test_data, "test_results.csv")
    assert os.path.exists("test_results.csv")

    with open("test_results.csv", "r", encoding="utf-8") as f:
        content = f.read()

    expected = "А,5\nБ,3\nВ,7\n"
    assert content == expected

    os.remove("test_results.csv")


def test_save_results_empty():
    save_results({}, "empty_results.csv")

    assert os.path.exists("empty_results.csv")

    with open("empty_results.csv", "r", encoding="utf-8") as f:
        content = f.read()

    assert content == ""
    os.remove("empty_results.csv")


def test_main_integration(capsys):

    original_process = wiki_parser.process_category
    wiki_parser.process_category = lambda x: ({'А': 5, 'Б': 3}, 1)

    try:
        main()
    finally:

        wiki_parser.process_category = original_process

    captured = capsys.readouterr()
    assert "Начинаю сбор данных" in captured.out
    assert "Готово!" in captured.out
    assert "Результаты сохранены" in captured.out
    assert "Обработано страниц: 1" in captured.out