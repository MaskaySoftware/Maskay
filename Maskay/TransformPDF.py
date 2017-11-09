# -*- coding: utf-8 -*-
'''Transforma los documentos PDF a TXT'''
import os
import shutil
import sys
import commands
import re
from urlparse import urlparse
import PyPDF2
from Documents import Documents


class TransformPDF(object):
    '''Transforma los documentos PDF a TXT'''
    reload(sys)
    sys.setdefaultencoding('utf8')

    def __init__(self, document=None):
        '''Constructor de la clase'''
        self.document = document
        self.numpages = 0
        self.db = Documents()

    @property
    def document(self):
        '''Método get de la variable document'''
        return self.document

    @document.setter
    def document(self, document):
        '''Método set de la variable document'''
        self.document = document

    def pdfToTxt(self):
        '''Valida si un documento de texto se pudo transformar a txt.
        Devuelve verdadero o falso
        '''
        parse_url = urlparse(self.document["url_extraccion"])
        path = parse_url.netloc + "/" + self.document["nombre"]
        # Si el path existe es porque esta el pdf en el servidor
        if os.path.exists(path):
            #Transformar a txt
            self.pdfText2Txt()
            lista = self.document["nombre"].split(".")
            size = os.path.getsize(parse_url.netloc + '/' + lista[0] + '.txt')
            if size == 0:
                #UPDATE ANA_IMG 1
                self.db.updateAnaImg(self.document)
                return False
            else:
                #UPDATE ANA_TEXT 1
                self.db.updateAnaTxt(self.document)
                os.remove(path)
                return True
        else:
            return True

    def pdfText2Txt(self):
        '''Método para convertir de pdf de texto a txt'''
        try:
            parse_url = urlparse(self.document["url_extraccion"])
            path = parse_url.netloc + "/" + self.document["nombre"]
            content = ""
            pyPDF = PyPDF2.PdfFileReader(file(path, "rb"))
            self.numpages = pyPDF.getNumPages()
            for i in range(0, pyPDF.getNumPages()):
                text = pyPDF.getPage(i).extractText()
                for match in re.finditer(r'(?s)((?:[^\n][\n]?)+)', text):
                    content += " ".join(text[match.start():match.end()].strip().split()) + "\n"
            content = re.sub(r'([^a-zA-Z0-9_.\s-])+', "", content)
            #content = " ".join(content.replace(u"\xa0","\n").strip().split())
            lista = self.document["nombre"].split(".")
            f = open(parse_url.netloc + '/' + lista[0] + '.txt', 'wb')
            f.write(content.encode("utf-8", "ignore"))
            f.close()
        except Exception:
            lista = self.document["nombre"].split(".")
            f = open(parse_url.netloc + '/' + lista[0] + '.txt', 'wb')
            f.close()
            return

    def pdfImg2Txt(self):
        '''Método para convertir de pdf de imágen a txt'''
        lista = self.document["nombre"].split(".")
        parse_url = urlparse(self.document["url_extraccion"])
        pathImg = parse_url.netloc + "/" + lista[0]
        path = parse_url.netloc + "/" + self.document["nombre"]
        if not os.path.exists(pathImg):
            os.mkdir(pathImg)
        commands.getoutput('gs -sDEVICE=png16m -dINTERPOLATE -dFirstPage=1 -dLastPage=' + str(self.numpages) + ' -r300 -o ./' + pathImg + '/\_image%03d.png ' + path)
        commands.getoutput('for i in ' + pathImg +  '/*.png; do tesseract $i $i; done')
        commands.getoutput('for i in ./' + pathImg +  '/*.txt; do cat $i; done> ' + parse_url.netloc + "/" + lista[0] + '.txt')
        shutil.rmtree(pathImg)
        os.remove(path)
