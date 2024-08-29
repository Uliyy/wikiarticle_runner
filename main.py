import logging

import requests
import subprocess as sp

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
    from_pos = len("https://en.wikipedia.org/wiki/")
    article_title = article_url[from_pos:]
    return article_title


def user_choice(art_title: str) -> bool:
    print(f"Тебе интересна эта статья: {art_title}?")
    while True:
        b = input()
        if b == "да":
            return True
        elif b == "нет":
            return False
        else:
            print("Я понимаю только 'да' и 'нет'. Повторите ответ")
        
def show_article(url: str):
    sp.run(["open", "/Applications/Safari.app", url])

def main():
    logger.info("starting main()...")
    while True:
        url, html = load_random_article()
        title = get_article_title(url)
        choice = user_choice(title)
        if choice:
            show_article(url)
        print("Продолжаем выбирать статью?")
        ans = input()
        if ans == "нет":
            break



if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        logger.error(e)
