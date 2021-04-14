import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from datetime import datetime
from agroinvestbank.items import Article


class agroinvestbankSpider(scrapy.Spider):
    name = 'agroinvestbank'
    start_urls = ['http://www.agroinvestbank.tj/ru/news/index.php']

    def parse(self, response):
        links = response.xpath('//p[@class="news-item"]/a/@href').getall()
        yield from response.follow_all(links, self.parse_article)

        next_page = response.xpath('//a[@class="next page-numbers"]/@href').get()
        if next_page:
            yield response.follow(next_page, self.parse)

    def parse_article(self, response):
        if 'pdf' in response.url.lower():
            return

        item = ItemLoader(Article())
        item.default_output_processor = TakeFirst()

        title = response.xpath('//h3/text()').get()
        if title:
            title = title.strip()

        date = response.xpath('//span[@class="news-date-time"]/text()').get()
        if date:
            date = " ".join(date.split())

        content = response.xpath('//div[@class="news-detail"]//text()').getall()
        content = [text.strip() for text in content if text.strip() and '{' not in text]
        content = " ".join(content[2:]).strip()

        item.add_value('title', title)
        item.add_value('date', date)
        item.add_value('link', response.url)
        item.add_value('content', content)

        return item.load_item()
