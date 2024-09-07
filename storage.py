from typing import Optional

from article import Article


DEFERRED_ARTICLES_FILE = "deferred_articles.txt"


class BaseStorage:
    def __init__(self):
        pass

    def done(self) -> None:
        raise NotImplementedError("this method should be implemented in derived class")

    def defer_article(self, article: Article) -> None:
        raise NotImplementedError("this method should be implemented in derived class")

    def pop_deferred_article(self) -> Optional[Article]:
        raise NotImplementedError("this method should be implemented in derived class")


class FileStorage(BaseStorage):
    def __init__(self):
        super().__init__()
        try:
            self._articles: dict[str, int] = {}
            for line in open(DEFERRED_ARTICLES_FILE, "rt"):
                self._articles[line[:-1]] = 1
        except FileNotFoundError:
            pass

    def done(self):
        f = open(DEFERRED_ARTICLES_FILE, "w")
        f.writelines([key + "\n" for key in self._articles.keys()])
        f.close()

    def defer_article(self, article: Article):
        self._articles[article.get_url()] = 1

    def pop_deferred_article(self) -> Optional[Article]:
        try:
            url = self._articles.popitem()[0]
            return Article(url)
        except KeyError:
            return None
