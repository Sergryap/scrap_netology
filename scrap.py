from bs4 import BeautifulSoup
from fake_headers import Headers
import requests
import json
import re


def get_soup(u: str):
    """Получение данных из запроса. Создание экземпляря BeautifulSoup"""
    headers = Headers(os="win", headers=True).generate()
    src = requests.get(u, headers=headers).text
    if src:
        return BeautifulSoup(src, "lxml")
    else:
        return get_soup(u)


def load_keys(item, all_articles: list, link=None):
    """
    Добавление словаря в список. Вспомогательная функция для других функций.
    При наличии ссылки, она задается в параметре link,
    При отсутствии формируется в теле функции
    """
    date = item.find("time")["title"][:10]
    title = item.find("h2").find("span").text
    if not link:
        link = f'https://habr.com{item.find("h2").find("a")["href"]}'
    all_articles.append({
        "date": date,
        "title": title,
        "link": link
    })
    print(f"<{date}><{title}><{link}>")


def get_pattern(w: list):
    """Компиляция паттерна для поиска статей по списку"""
    p = ""
    for rew in w:
        p += fr"{rew}\w*|"
    pattern = fr"\b({p[:-1]})\b"
    return re.compile(pattern, re.IGNORECASE)


def max_page(start: str = "https://habr.com/ru/all"):
    """Определение максимальной страницы пагинации"""
    soup = get_soup(start)
    pages = soup.find(class_="tm-pagination__pages").find_all("a")
    return max([int(page.text) for page in pages])


def get_articles(w, start: str = "https://habr.com/ru/all"):
    """Парсинг с анализом по превью"""
    pattern = get_pattern(w)
    i = max_page(start)
    all_articles = []
    for n, url in enumerate([f"{start}/page{i}/" for i in range(1, i + 1)]):
        print(f"Анализ страницы №{n + 1}")
        soup = get_soup(url)
        tm_article_snippet = soup.find_all(class_="tm-article-snippet")
        for item in tm_article_snippet:
            if pattern.search(item.text):
                load_keys(item, all_articles)
    return all_articles


def get_articles_extreme(w, start: str = "https://habr.com/ru/all"):
    """Парсинг с анализом по превью и всей статье"""
    pattern = get_pattern(w)
    i = max_page(start)
    all_articles = []
    for n, url in enumerate([f"{start}/page{i}/" for i in range(1, i + 1)]):
        print(f"Анализ страницы №{n + 1}")
        soup = get_soup(url)
        tm_article_snippet = soup.find_all(class_="tm-article-snippet")
        for item in tm_article_snippet:
            link = f'https://habr.com{item.find("h2").find("a")["href"]}'
            if pattern.search(item.text):
                load_keys(item, all_articles, link)
            else:
                soup_next = get_soup(link)
                article = soup_next.find(class_="tm-article-presenter__content tm-article-presenter__content_narrow")
                if pattern.search(article.text):
                    load_keys(item, all_articles, link)
    return all_articles


def save_to_json(book: {list, dict}, file: str):
    """Сохранение результатов в json файл"""
    with open(file, "w", encoding="utf-8") as f:
        json.dump(book, f, indent=4, ensure_ascii=False)


if __name__ == '__main__':
    KEYWORDS = ['дизайн', 'фото', 'web', 'python']
    articles = get_articles_extreme(KEYWORDS)
    save_to_json(articles, "articles_extreme.json")
