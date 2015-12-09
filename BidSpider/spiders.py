from bs4 import BeautifulSoup
from spider import Spider
from link_extractor import PageNumIncrementLinks
from items import BidInfoItem


class CqzbSpider(Spider):
    name = 'cqzb'
    domain = 'cqzb.gov.cn'

    def __init__(self):
        fmt = "http://www.cqzb.gov.cn/class-5-1({PageNum}).aspx"
        self.start_urls = \
            PageNumIncrementLinks(1, 50, fmt).extract_link()

    def parse(self, response):
        soup = BeautifulSoup(response)
        ul = soup.select('body > div.ztb_wrapper > div.ztb_list_wrapper > div.ztb_list_right > ul')[0]
        lines = ul.select('li')

        for line in lines:
            item = BidInfoItem()
            item['link'] = line.a['href']
            item['title'] = self.complete_link(line.a.string.strip())
            item['date'] = line.span.string[1:-1]
            yield item

    def complete_link(self, link):
        return 'http://www.' + self.domain + '/' + link
