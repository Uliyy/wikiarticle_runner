import logging
import subprocess as sp

logger = logging.getLogger(__name__)


class Article:
    def __init__(self, url: str) -> None:
        self._url = url

    def get_title(self) -> str:
        logger.info(f"get_article_title: {self._url}")
        from_pos = len("https://en.wikipedia.org/wiki/")
        article_title = self._url[from_pos:]
        return article_title

    def show(self):
        sp.run(["open", "/Applications/Safari.app", self._url])

    def get_url(self) -> str:
        return self._url
