# -*- coding: utf-8 -*-
'''Araña principal que busca todas los páginas a analizar'''
import json
from urlparse import urlparse
import scrapy
from scrapy import signals
from scrapy.selector import Selector


class SpiderPagesSpiderFirst(scrapy.Spider):
    '''Araña principal que busca todas las páginas a analizar'''
    name = 'spider_first'
    allowed_domains = []
    start_urls = []
    pages = []

    def __init__(self, url_to=None, *args, **kwargs):
        super(SpiderPagesSpiderFirst, self).__init__(*args, **kwargs)
        pdf_1 = self.is_pdf(url_to)
        if pdf_1 is None:
            if not url_to.startswith('http://') and not url_to.startswith('https://'):
                url_to = 'http://%s/' % url_to
            self.start_urls = ['%s' % url_to]
            parse_url = urlparse(url_to)
            self.allowed_domains = ['%s' % parse_url.netloc]

    def parse(self, response):
        '''Método que busca las url dentro de una página'''
        urlsPages = Selector(response).xpath('//a')
        for urlPage in urlsPages:
            if len(urlPage.xpath('@href')) > 0:
                url = urlPage.xpath('@href').extract()[0]
                refer = response.urljoin(url)
                url = self.get_url(url, refer)
                if url is not None:
                    pdf = self.is_pdf(url)
                    if pdf is None:
                        self.pages.append(url)

    def is_pdf(self, url):
        '''Valida si las URL contienen un documento PDF'''
        parse_url = urlparse(url)
        analyze_url = parse_url.scheme + "://" + parse_url.netloc + parse_url.path
        lista = analyze_url.split(".")
        ext = lista.pop()
        if ext.upper() == "PDF":
            return analyze_url
        return None

    def get_url(self, url, refer):
        '''Valida si la URL es válida'''
        if(url is None):
            return None
        if (len(url) <= 2):
            return None
        if(url[0] == '#'):
            return None
        if(url[0:10] == 'javascript'):
            return None
        parse_url = urlparse(refer)
        if(parse_url.netloc != self.allowed_domains[0]):
            return None
        if((refer[0:7] == 'http://') or (refer[0:8] == 'https://')):
            return refer
        return None

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        '''Se ejecuta cuando la araña termina de analizar la página
        Invoca el método de impresión de datos encontrados
        '''
        spider = super(SpiderPagesSpiderFirst, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.engine_stopped, signals.engine_stopped)
        return spider

    def engine_stopped(self):
        '''Imprime en consola las páginas encontradas'''
        print(json.dumps(self.pages))
