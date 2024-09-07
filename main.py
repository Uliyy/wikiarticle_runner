import logging
import enum
import requests

from storage import BaseStorage, FileStorage
from article import Article

LOGFILE = "wikiarticle_runner.log"
DEFERRED_ARTICLES_FILE = "deferred_articles.txt"

logging.basicConfig(filename=LOGFILE, level=logging.DEBUG)
logger = logging.getLogger(__name__)

RANDOM_ARTICLE_URL = "https://en.wikipedia.org/wiki/Special:Random"


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


def main(storage: BaseStorage):
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
            storage.defer_article(article)
        if choice == UserChoice.DEFERRED:
            article2 = storage.pop_deferred_article()
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

    storage = None
    try:
        storage = FileStorage(DEFERRED_ARTICLES_FILE)
        main(storage)
    except Exception as e:
        logger.error(e)
    finally:
        if storage != None:
            storage.done()
