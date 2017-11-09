# -*- coding: utf-8 -*-
'''Crawler que realiza la extracción de los documentos PDF'''
import os
import json
from urlparse import urlparse
from datetime import datetime
import time
import redis
import scrapy
from scrapy import signals
from Maskay.items import PDFItem
from Maskay.RestrictedWord import RestrictedWord
from scrapy.selector import Selector
from scrapy.http import Request, HtmlResponse
from scrapy.linkextractors import LinkExtractor


class SpiderPagesSpider(scrapy.Spider):
    '''Crawler que realiza la extracción de los documentos PDF'''
    name = 'spider_pages'
    allowed_domains = []
    start_urls = []
    r = redis.StrictRedis(host='localhost', port=6379, db=9)
    documents = []
    names = []
    domain = None

    def __init__(self, url_to=None, *args, **kwargs):
        '''Contructor del crawler'''
        super(SpiderPagesSpider, self).__init__(*args, **kwargs)
        self.start_urls = ['%s' % url_to]
        parse_url = urlparse(url_to)
        self.domain = parse_url.scheme + "://" + parse_url.netloc
        self.allowed_domains = ['%s' % parse_url.netloc]
        self.link_extractor = LinkExtractor()

    def parse(self, response):
        '''Método que busca las url dentro de una página'''
        pdf_1 = self.is_pdf(response.url)
        if pdf_1 is not None:
            yield scrapy.Request(pdf_1, callback= self.save_pdf)
        else:
            if isinstance(response, HtmlResponse):
                urlsPages = Selector(response).xpath('//a')
                for urlPage in urlsPages:
                    if len(urlPage.xpath('@href')) > 0:
                        url = urlPage.xpath('@href').extract()[0]
                        refer = response.urljoin(url)
                        pdf = self.is_pdf(refer)
                        if pdf is not None:
                            yield scrapy.Request(pdf, callback= self.save_pdf)
                        url = self.get_url(url, refer)
                        if url is not None:
                            if self.analyze_page(url):
                                yield scrapy.Request(url, callback = self.parse, dont_filter=True)

    def is_pdf(self, url):
        '''Valida si el url es un documento PDF
        Devuelve vacío si contiene una palagra restringida
        Devuelve vacío si no es PDF
        '''
        restrictedWord = RestrictedWord()
        words = restrictedWord.search()
        if url.upper() in words:
            return None
        parse_url = urlparse(url)
        analyze_url = parse_url.scheme + "://" + parse_url.netloc + parse_url.path
        lista = analyze_url.split(".")
        ext = lista.pop()
        if ext.upper() == "PDF":
            return analyze_url
        return None

    def analyze_page(self, url):
        '''Verifica si la página ya fue visitada'''
        dateNow = datetime.now()
        if(self.r.get(url) is None):
            self.r.set(url, time.strftime("%Y-%m-%d"))
            return True
        else:
            datePage = datetime.strptime(self.r.get(url), "%Y-%m-%d")
            if (dateNow - datePage).days >= 29 :
                self.r.set(url, time.strftime("%Y-%m-%d"))
                return True
            else:
                return False

    def save_pdf(self, response):
        '''Envia el item para que sea almacenado en base de datos'''
        name = response.url.split('/')[-1].encode('utf-8')
        print response.url
        print name
        path = self.allowed_domains[0]
        #Revisa en Redis
        print self.r.get(name)
        if(self.r.get(name) is None):
            #Item para guardar en mongo
            self.documents.append(response.url)
            self.names.append(name)
            item = PDFItem()
            item['nombre'] = name
            item['fecha_creacion'] = time.strftime("%Y-%m-%d")
            item['num_visitas'] = 0 
            item['url_extraccion'] = self.domain
            item['ana_text'] = 0
            item['ana_img'] = 0 
            item['url_pdf'] = response.url
            if not os.path.exists(path):
                os.mkdir(path)
            f = open(path + "/" + name, 'wb')
            f.write(response.body)
            f.seek(0,os.SEEK_END)
            size = f.tell() 
            f.close()
            self.r.set(name, size)
            yield item
        else:
            if not os.path.exists(path):
                os.mkdir(path)
            f = open(path + "/test_" + name, 'wb')
            f.write(response.body)
            f.close()
            size = os.path.getsize(path + "/test_" + name)
            if self.r.get(response.url) != size:
                self.documents.append(response.url)
                if os.path.exists(path + "/" + name):
                    os.remove(path + "/" + name)
                os.rename(path + "/test_" + name,path + "/" + name)
            else:
                os.remove(path + "/test_" + name)

    
    def get_url(self, url, refer):
        '''Valida si es una URL admitida
        Parámetros:
        url -- Es el link sin procesar
        refer -- Es la página de donde se sacó el pdf
        Devuelve vacío si no es url
        '''
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
        '''Se ejecuta cuando el craeler termina de analizar
        Invoca el método de impresión de datos encontrados
        '''
        spider = super(SpiderPagesSpider, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.engine_stopped, signals.engine_stopped)
        return spider

    def engine_stopped(self):
        '''Imprime en consola las páginas encontradas'''
        print json.dumps(self.names)
        print json.dumps(self.documents)
