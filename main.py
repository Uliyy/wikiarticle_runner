import logging
import enum
import subprocess as sp
from typing import Optional
import requests

LOGFILE = "wikiarticle_runner.log"
DEFERRED_ARTICLES_FILE = "deferred_articles.txt"

deferred_articles: dict[str, int] = {}

logging.basicConfig(filename=LOGFILE, level=logging.DEBUG)
logger = logging.getLogger(__name__)

RANDOM_ARTICLE_URL = "https://en.wikipedia.org/wiki/Special:Random"


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


def load_random_article() -> Article:
    logger.info("load_random_article")
    req1 = requests.request("GET", RANDOM_ARTICLE_URL, allow_redirects=False)
    if req1.status_code != 302:
        raise Exception("Вики недоступна")
    loc = req1.headers["location"]
    req2 = requests.request("GET", loc)
    if req2.status_code != 200:
        raise Exception("Вики недоступна")
    return Article(loc)


class UserChoice(enum.Enum):
    READ = 1
    SKIP = 2
    DEFER = 3
    DEFERRED = 4
    EXIT = 5


def user_choice(art_title: str) -> UserChoice:
    print(f"Тебе интересна эта статья: {art_title}?")
    print(
        f"Варианты ответа: читать - {UserChoice.READ.value}, "
        f"пропустить - {UserChoice.SKIP.value}, "
        f"отложить - {UserChoice.DEFER.value}, "
        f"посмотреть рандомную отложенную статью - {UserChoice.DEFERRED.value}, "
        f"выйти - {UserChoice.EXIT.value}"
    )
    while True:
        try:
            b = int(input())
            for x in UserChoice:
                if b == x.value:
                    return x
            raise ValueError()
        except ValueError:
            print(
                "Я понимаю только перечисленные выше цифровые варианты. "
                "Введите верный вариант"
            )


def defer_article(article: Article):
    deferred_articles[article.get_url()] = 1


def pop_deferred_article() -> Optional[Article]:
    try:
        url = deferred_articles.popitem()[0]
        return Article(url)
    except KeyError:
        return None


def load_deferred_articles() -> dict[str, int]:
    try:
        f = open(DEFERRED_ARTICLES_FILE, "r")
        d: dict[str, int] = {}
        s = f.readline()
        while s != "":
            d[s[:-1]] = 1
            s = f.readline()
        f.close()
        return d
    except FileNotFoundError:
        return {}


def save_deferred_articles(d: dict[str, int]):
    f = open(DEFERRED_ARTICLES_FILE, "w")
    f.writelines([key + "\n" for key in d.keys()])
    f.close()


def main():
    logger.debug("starting main()...")
    while True:
        article = load_random_article()
        title = article.get_title()
        choice = user_choice(title)
        if choice == UserChoice.READ:
            article.show()
        if choice == UserChoice.SKIP:
            pass
        if choice == UserChoice.DEFER:
            defer_article(article)
        if choice == UserChoice.DEFERRED:
            article2 = pop_deferred_article()
            if article2 != None:
                while True:
                    choice2 = input(
                        f"Вам интересна эта статья (да/нет)? {article2.get_title()}: "
                    )
                    if choice2 == "да":
                        article2.show()
                        break
                    elif choice2 == "нет":
                        break
                    else:
                        print("Я понимаю только 'да' и 'нет'. Повторите ответ")
            else:
                print("В отложенных пока ничего нет :)")

        if choice == UserChoice.EXIT:
            break


if __name__ == "__main__":
    try:
        deferred_articles = load_deferred_articles()
        main()
    except Exception as e:
        logger.error(e)
    finally:
        save_deferred_articles(deferred_articles)
