from requests_html import HTMLSession
from crawlers import crawlers


session = HTMLSession(verify=False)
headers = {
    'user-agent': 'Chrome/90.0.4430.212'
}


if __name__ == "__main__":
    
    config = {
        'user': 'levuloi',
        'password': 'openqathesis62021',
        'host': 'localhost',
        'database': 'resources',
        'raise_on_warnings': True,
        'auth_plugin': 'mysql_native_password'
    }
    crawler = crawlers.BaseCrawler(
        website="https://suckhoedoisong.vn/",
        storage_dir="suckhoedoisong",
        crawled_content=False,
        db_config=config
    )
    # crawler.crawl_article_links(
    #     anchor_link='https://suckhoedoisong.vn/covid-19-benh-viem-duong-ho-hap-cap-do-chung-moi-cua-virus-corona-cn4086/p1',
    #     session=session, 
    #     headers=headers
    # )

    # crawler.crawl_article_links(
    #     anchor_link={"https://suckhoedoisong.vn/who-nam-dai-dich-covid-19-thu-hai-chet-choc-nhieu-hon-n192699.html"},
    #     session=session,
    #     headers=headers
    # )

    # crawler.crawl_special_articles(
    #     session=session,
    #     headers=headers,
    #     anchor_link="https://suckhoedoisong.vn/thay-gioi-thuoc-hay-c45/"
    # )

    crawler.crawl_articles_content(session=session, headers=headers)