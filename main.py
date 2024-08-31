import logging
import enum
import subprocess as sp
from typing import Optional 
import requests

LOGFILE = "wikiarticle_runner.log"

logging.basicConfig(filename=LOGFILE, level=logging.DEBUG)
logger = logging.getLogger(__name__)

RANDOM_ARTICLE_URL = "https://en.wikipedia.org/wiki/Special:Random"


def load_random_article() -> tuple[str, str]:
    logger.info("load_random_article")
    req1 = requests.request("GET", RANDOM_ARTICLE_URL, allow_redirects=False)
    if req1.status_code != 302:
        raise Exception("Вики недоступна")
    loc = req1.headers['location']
    req2 = requests.request("GET", loc)
    if req2.status_code != 200:
        raise Exception("Вики недоступна")
    return loc, req2.text


def get_article_title(article_url: str) -> str:
    logger.info(f"get_article_title: {article_url}")
    from_pos = len("https://en.wikipedia.org/wiki/")
    article_title = article_url[from_pos:]
    return article_title





class UserChoice(enum.Enum):
    READ = 1
    SKIP = 2
    DEFER = 3
    DEFERRED = 4
    EXIT = 5


def user_choice(art_title: str) -> UserChoice:
    print(f"Тебе интересна эта статья: {art_title}?")
    print(f"Варианты ответа: читать - {UserChoice.READ.value}, "
          f"пропустить - {UserChoice.SKIP.value}, "
          f"отложить - {UserChoice.DEFER.value}, "
          f"посмотреть рандомную отложенную статью - {UserChoice.DEFERRED.value}, "
          f"выйти - {UserChoice.EXIT.value}")
    while True:
        try: 
            b = int(input())
            for x in UserChoice: 
                if b == x.value:
                    return x
            raise ValueError()
        except ValueError:
            print("Я понимаю только перечисленные выше цифровые варианты. "
                  "Введите верный вариант")
            
        
def show_article(url: str):
    sp.run(["open", "/Applications/Safari.app", url])


deferred_articles: dict[str, int] = {}
def defer_article(url: str):
    deferred_articles[url] = 1

def pop_deferred_article() -> Optional[str]:
    try:
        return deferred_articles.popitem()[0]
    except KeyError:
        return None


def main():
    logger.debug("starting main()...")
    while True:
        url, _html = load_random_article()
        title = get_article_title(url)
        choice = user_choice(title)
        if choice == UserChoice.READ:
            show_article(url)
        if choice == UserChoice.SKIP:
            pass
        if choice == UserChoice.DEFER:
            defer_article(url)
        if choice == UserChoice.DEFERRED:
            url2 = pop_deferred_article()
            if url2 != None:
                while True:
                    choice2 = input(f"Вам интересна эта статья (да/нет)? {get_article_title(url2)}: ")
                    if choice2 == "да":
                        show_article(url2)
                        break
                    elif choice2 == "нет":
                        break
                    else:
                        print("Я понимаю только 'да' и 'нет'. Повторите ответ")
            else:
                print("В отложенных пока ничего нет :)")

        if choice == UserChoice.EXIT:
            break



if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        logger.error(e)
