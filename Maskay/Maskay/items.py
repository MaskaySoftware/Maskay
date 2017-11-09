# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy

class PDFItem(scrapy.Item):
    # define the fields for your item here like:
    nombre = scrapy.Field()
    fecha_creacion = scrapy.Field()
    num_visitas = scrapy.Field()
    fecha_actualizacion = scrapy.Field()
    url_pdf = scrapy.Field()
    url_extraccion = scrapy.Field()
    ana_text = scrapy.Field()
    ana_img = scrapy.Field()
