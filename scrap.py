from bs4 import BeautifulSoup
from fake_headers import Headers
import requests
import json
import re


class Articles:

    def __init__(self, start="https://habr.com/ru/all", keywords=('дизайн', 'фото', 'web', 'python')):
        self.start = start
        self.keywords = keywords

    def get_soup(self, link=None):
        """Получение данных из запроса. Создание экземпляря BeautifulSoup"""
        headers = Headers(os="win", headers=True).generate()
        url = self.start if not link else link
        src = requests.get(url, headers=headers).text
        if src:
            return BeautifulSoup(src, "lxml")
        else:
            return self.get_soup()

    @staticmethod
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

    def pattern(self):
        """Компиляция паттерна для поиска статей по списку"""
        p = ""
        for rew in self.keywords:
            p += fr"{rew}\w*|"
        pattern = fr"\b({p[:-1]})\b"
        return re.compile(pattern, re.IGNORECASE)

    def max_page(self):
        """Определение максимальной страницы пагинации"""
        soup = self.get_soup()
        pages = soup.find(class_="tm-pagination__pages").find_all("a")
        return max([int(page.text) for page in pages])

    def get_articles(self):
        """Парсинг с анализом по превью"""
        pattern = self.pattern()
        i = self.max_page()
        all_articles = []
        for n, url in enumerate([f"{self.start}/page{i}/" for i in range(1, i + 1)]):
            print(f"Анализ страницы №{n + 1}")
            soup = self.get_soup()
            tm_article_snippet = soup.find_all(class_="tm-article-snippet")
            for item in tm_article_snippet:
                if pattern.search(item.text):
                    self.load_keys(item, all_articles)
        return all_articles

    def get_articles_extreme(self):
        """Парсинг с анализом по превью и всей статье"""
        pattern = self.pattern()
        i = self.max_page()
        all_articles = []
        for n, url in enumerate([f"{self.start}/page{i}/" for i in range(1, i + 1)]):
            print(f"Анализ страницы №{n + 1}")
            soup = self.get_soup()
            tm_article_snippet = soup.find_all(class_="tm-article-snippet")
            for item in tm_article_snippet:
                link = f'https://habr.com{item.find("h2").find("a")["href"]}'
                if pattern.search(item.text):
                    self.load_keys(item, all_articles, link)
                else:
                    soup_next = self.get_soup(link=link)
                    article = soup_next.find(
                        class_="tm-article-presenter__content tm-article-presenter__content_narrow")
                    if pattern.search(article.text):
                        self.load_keys(item, all_articles, link)
        return all_articles

    @staticmethod
    def save_to_json(book: {list, dict}, file: str):
        """Сохранение результатов в json файл"""
        with open(file, "w", encoding="utf-8") as f:
            json.dump(book, f, indent=4, ensure_ascii=False)


if __name__ == '__main__':
    parser = Articles()
    articles = parser.get_articles_extreme()
    parser.save_to_json(articles, "articles_extreme.json")
