# -*- coding: utf-8 -*-
'''Ejecuta el componente de rastreo'''
import sys
from time import time
from urlparse import urlparse
from Pages import Page
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

# Variables
searchInNoun = []
pdf_show = []
pdf_img = []
pdf_listos = []


def start(page1, page2, page3, page4):
    '''Ejecuta el componente de rastreo con 4 páginas paralelas
    Parámetros
    page1 -- Cadena de texto con la página principal a rastrear
    page2 -- Cadena de texto con la página secundaria
    page3 -- Cadena de texto con la página secundaria
    page4 -- Cadena de texto con la página secundaria
    '''
    parse_url = urlparse(page1)
    dominio = parse_url.scheme + "://" + parse_url.netloc
    process = CrawlerProcess(get_project_settings())
    start_time = time()
    process.crawl('spider_pages', page1)
    process.crawl('spider_pages', page2)
    process.crawl('spider_pages', page3)
    process.crawl('spider_pages', page4)
    process.start()
    # El script se bloquea mientras el crawler termina
    elapsed_time = time() - start_time
    pages = Page()
    pages.searchPage(dominio)
    pages.sendEmails()
    pages.updatePage(elapsed_time)


def start_craw(page1):
    '''Ejecuta el componente de rastreo con 1 página
    Al terminar envia el correo
    Parámetros
    page1 -- Cadena de texto con la página principal a rastrear
    '''
    parse_url = urlparse(page1)
    dominio = parse_url.scheme + "://" + parse_url.netloc
    process = CrawlerProcess(get_project_settings())
    start_time = time()
    process.crawl('spider_pages', page1)
    process.start()
    # El script se bloquea mientras el crawler termina
    elapsed_time = time() - start_time
    pages = Page()
    pages.searchPage(dominio)
    pages.sendEmails()
    pages.updatePage(elapsed_time)

if __name__ == "__main__":
    '''Ejecuta el metodo según la cantidad de parámetros recibidos'''
    a = str(sys.argv[1])
    if len(sys.argv) == 2:
        start_craw(a)
    else:
        b = str(sys.argv[2])
        c = str(sys.argv[3])
        d = str(sys.argv[4])
        start(a, b, c, d)
