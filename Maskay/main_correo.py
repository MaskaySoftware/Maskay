# -*- coding: utf-8 -*-
'''Ejecuta el envío de correos'''
import sys
from Pages import Page

searchInNoun = []
pdf_show = []
pdf_img = []
pdf_listos = []


def start_resend(id):
    '''Ejecuta el envío de correos si el estado
    de la página es Finished'''
    pages = Page()
    page = pages.searchPageId(id, "Finished")
    if page is not None:
        pages.sendEmails()

if __name__ == "__main__":
    '''Ejecuta el método principal'''
    a = str(sys.argv[1])
    start_resend(a)
