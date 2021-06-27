from underthesea import sent_tokenize
from requests_html import HTMLSession
import mysql.connector
import re
import time


class BaseCrawler:
    def __init__(self, website, storage_dir, db_config, crawled_content=False):
        self.website = website
        self.storage_dir = storage_dir
        self.db_config = db_config
        if not crawled_content:
            self.load_article_links()
            self.num_crawled_links = len(self.crawled_links)
        else:
            pass
    
    def load_article_links(self):
        conn = mysql.connector.connect(**self.db_config)
            
        SELECT_QUERY = r"""SELECT * FROM `crawled_links` WHERE website = '{}';""".format(self.website)
        cursor = conn.cursor()
        cursor.execute(SELECT_QUERY)
        
        crawled_links = []
        for rowid, website, url in cursor:
            crawled_links.append(url)
        
        cursor.close()
        conn.close()

        self.crawled_links = set(crawled_links)
        assert len(self.crawled_links) == len(crawled_links)

    def persist_to_db(self, article_links):
        conn = mysql.connector.connect(**self.db_config)
        cursor = conn.cursor()
        INSERT_QUERY = r"""INSERT INTO `crawled_links` (website, url) VALUES ('{}', '{{}}');""".format(self.website)
        for link in article_links:
            if link not in self.crawled_links:
                cursor.execute(INSERT_QUERY.format(link))

        self.crawled_links = self.crawled_links.union(article_links)
        
        conn.commit()
        cursor.close()
        conn.close()
        
    def _retrieve_href(self, page):
        elements = page.html.xpath("//a[contains(@class, \"fbold\")]")
        article_links = [e.attrs['href'] for e in elements if e.attrs['href'].startswith(self.website)]
        article_links = set(article_links)

        return article_links

    def crawl_article_links(self, anchor_link, session, headers):
        links_queue = list(anchor_link)
        article_links = set()
        count = 0
        while len(links_queue) > 0:
            try:
                url = links_queue.pop(0)
                if url == self.website:
                    continue
            except Exception as e:
                break

            page = session.get(url, headers=headers)
            page.html.render()
            links = self._retrieve_href(page)
            added_links = links - article_links - self.crawled_links
            for link in added_links:
                self.num_crawled_links = self.num_crawled_links + 1 
                print("Crawled #{}: {}".format(self.num_crawled_links, link))

            links_queue.extend(list(added_links - anchor_link))
            article_links = article_links.union(added_links)

            count += 1
            if count % 5 == 0:
                self.persist_to_db(article_links)
                article_links = set()
                print("---------------------------------------------------------------------------------")
                print("Persisted to database")
                print("---------------------------------------------------------------------------------")
                assert self.num_crawled_links == len(self.crawled_links), "Num crawled links mismatch"

    def crawl_special_articles(self, anchor_link, session, headers):
        count = 0
        article_links = set()
        while True:
            count += 1
            print("*************************** Count {} ***************************".format(count))
            url = anchor_link + "/" + "p{}".format(count)
            page = session.get(url, headers=headers)
            page.html.render()
            links = self._retrieve_href(page)
            added_links = links - article_links - self.crawled_links
            article_links = article_links.union(added_links)
            for link in added_links:
                self.num_crawled_links = self.num_crawled_links + 1 
                print("Crawled #{}: {}".format(self.num_crawled_links, link))
            
            if count % 10 == 0:
                self.persist_to_db(article_links)
                article_links = set()
                print("---------------------------------------------------------------------------------")
                print("Persisted to database")
                print("---------------------------------------------------------------------------------")
                assert self.num_crawled_links == len(self.crawled_links), "Num crawled links mismatch"

    def _crawl_content(self, url, session, headers):
        start = time.perf_counter()
        page = session.get(url, headers=headers)
        page.html.render()
        title_element = page.html.xpath("//div[@class='title-detail']")
        assert len(title_element) == 1, "There must be only one title element"
        title_element = title_element[0]
        summary_element = page.html.xpath("//div[@class='sapo_detail']")
        assert len(summary_element) == 1, "There must be only one summary element"
        summary_element = summary_element[0]

        content_element = page.html.xpath("//div[@id=\"content_detail_news\"]")
        assert len(content_element) == 1, "There must be only one content element"
        content_element = content_element[0]
        
        title = title_element.text
        summary = summary_element.text
        content = content_element.text

        end = time.perf_counter()
        print("Elapsed: {}".format(end - start))

        return title, summary, content

    def crawl_articles_content(self, session, headers):
        conn = mysql.connector.connect(**self.db_config)
        cursor = conn.cursor()
        
        SELECT_QUERY_MEDICAL_TABLE = r"""SELECT * FROM `medical_articles`;"""
        cursor.execute(SELECT_QUERY_MEDICAL_TABLE)
        content_crawled_urls = set()
        for id, url, title, summary, content in cursor:
            content_crawled_urls.add(url)
        count = len(content_crawled_urls)
        
        SELECT_QUERY_LINK_TABLE = r"""SELECT * FROM `crawled_links`;"""
        cursor.execute(SELECT_QUERY_LINK_TABLE)
        link_crawled_urls = set()
        for id, website, url in cursor:
            link_crawled_urls.add(url)

        working_urls = link_crawled_urls - content_crawled_urls

        INSERT_QUERY = r"""INSERT INTO `medical_articles` (url, title, summary, content) VALUES ({});"""
        records = []
        # count = 0
        for url in working_urls:
            try:
                title, summary, content = self._crawl_content(url, session=session, headers=headers)
            except Exception as e:
                print(e)
                continue
            title = re.sub(r"'", r"\'", title)
            summary = re.sub(r"'", r"\'", summary)
            content = re.sub(r"'", r"\'", content)

            values = "'{}', '{}', '{}', '{}'".format(url, title, summary, content)
            query = INSERT_QUERY.format(values)
            cursor.execute(query)
            count += 1
            if count % 10 == 0:
                conn.commit()
                print("Execute {} queries".format(count))

        cursor.close()
        conn.close()
