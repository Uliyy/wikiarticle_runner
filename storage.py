from typing import Optional

from article import Article


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
    def __init__(self, filename: str):
        super().__init__()
        self.filename = filename
        try:
            self._articles: dict[str, int] = {}
            for line in open(filename, "rt"):
                self._articles[line[:-1]] = 1
        except FileNotFoundError:
            pass

    def done(self):
        f = open(self.filename, "w")
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
