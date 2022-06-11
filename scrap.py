from bs4 import BeautifulSoup
import requests
import json
import re


def get_soup(u: str):
    """Получение данных из запроса. Создание экземпляря BeautifulSoup"""
    headers = {
        "Accept": "*/*",
        "User-Agent": "Mozilla/5.0 (iPad; CPU OS 11_0 like Mac OS X) AppleWebKit/604.1.34 (KHTML, like Gecko) Version/11.0 Mobile/15A5341f Safari/604.1"
    }
    src = requests.get(u, headers=headers).text
    return BeautifulSoup(src, "lxml")


def load_keys(item, all_articles: list, link=None, lk=False):
    """
    Добавление словаря в список. Вспомогательная функция для других функций.
    При наличии ссылки, она задается в параметре link,
    При отсутствии формируется в теле функции
    """
    date = item.find("time")["title"][:10]
    title = item.find("h2").find("span").text
    if lk:
        link = f'https://habr.com{item.find("h2").find("a")["href"]}'
    all_articles.append({
        "date": date,
        "title": title,
        "link": link
    })
    print(f"<{date}><{title}><{link}>")


def get_pattern(w=('дизайн', 'фото', 'web', 'python')):
    """Компиляция паттерна для поиска статей по списку"""
    pattern = fr"\b({w[0]}\w*|{w[1]}\w*|{w[2]}\w*|{w[3]}\w*)\b"
    return re.compile(pattern, re.IGNORECASE)


def get_articles(start: str = "https://habr.com/ru/all"):
    """Парсинг с анализом по превью"""
    pattern = get_pattern()
    all_articles = []
    for n, url in enumerate([f"{start}/page{i}/" for i in range(1, 51)]):
        print(f"Анализ страницы №{n + 1}")
        soup = get_soup(url)
        tm_article_snippet = soup.find_all(class_="tm-article-snippet")
        for item in tm_article_snippet:
            if pattern.search(item.text):
                load_keys(item, all_articles, lk=True)
    return all_articles


def get_articles_extreme(start: str = "https://habr.com/ru/all"):
    """Парсинг с анализом по превью и всей статье"""
    pattern = get_pattern()
    all_articles = []
    for n, url in enumerate([f"{start}/page{i}/" for i in range(1, 51)]):
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
    articles = get_articles_extreme()
    save_to_json(articles, "articles_inside.json")
    # get_articles_inside()
