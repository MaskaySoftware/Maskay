# -*- coding: utf-8 -*-
'''Clase del componente de extracción'''
import threading
from nltk import word_tokenize
from nltk.tag import StanfordPOSTagger
from urlparse import urlparse


class ExtractPDF():
    '''Clase del componente de extracción'''
    document = None
    search = None
    paragraphs = []
    content = None
    count = 0
    paragshow = ""
    nounSearch = []
    models = '/usr/share/stanford-postagger/models/spanish.tagger'
    jar = '/usr/share/stanford-postagger/stanford-postagger.jar'
    st = StanfordPOSTagger(models, jar, encoding='utf8')

    def __init__(self, document=None, search=None, nounSearch=None):
        '''Constructor de la clase'''
        self.document = document
        self.search = search
        self.nounSearch = nounSearch

    @property
    def search(self):
        '''Método get de la variable search'''
        return self.search

    @search.setter
    def search(self, search):
        '''Método set de la variable search'''
        self.search = search

    @property
    def document(self):
        '''Método get de la variable document'''
        return self.document

    @document.setter
    def document(self, document):
        '''Método set de la variable document'''
        self.document = document

    @property
    def nounSearch(self):
        '''Método get de la variable nounSearch'''
        return self.nounSearch

    @nounSearch.setter
    def nounSearch(self, nounSearch):
        '''Método set de la variable nounSearch'''
        self.nounSearch = nounSearch

    def getParagraphShow(self):
        '''Método get de la variable paragshow'''
        return self.paragshow


    def getContent(self):
        '''Lee el documento .txt
        Asigna a la variable contet el contenido leído
        '''
        lista = self.document["nombre"].split(".")
        parse_url = urlparse(self.document["url_extraccion"])
        f = open(parse_url.netloc + '/' + lista[0] + '.txt', 'r')
        self.content = str(f.read())
        f.close()

    def toParagraph(self):
        '''Convierte a párrafo
        Asigna a la variable paragraphs la conversión
        '''
        self.getContent()
        self.paragraphs = self.content.split("\n")

    def searchToNoun(self):
        '''Convierte la palabra de búsqueda a entidad nombrada
        Asigna a la variable nounSearch la conversión
        '''
        self.nounSearch = []
        words = word_tokenize(self.search)
        tagged_words = self.st.tag(words)
        for (word, tag) in tagged_words:
            if self.isNoun(tag): self.nounSearch.append(word.upper())
        return self.nounSearch

    def searchInPDF(self):
        '''Ejecuta los hilos para la búsqueda por parrafo de las entidades'''
        self.toParagraph()
        threads = [threading.Thread(target=self.searchInParagraph, args=(paragraph,)) for paragraph in self.paragraphs]
        [thread.start() for thread in threads]
        [thread.join() for thread in threads]
        return self.count

    def searchInParagraph(self, paragraph):
        '''Busca las entidades nombradas en cadena en el párrafo'''
        paragraphMod = word_tokenize(paragraph)
        for i,word in enumerate(paragraphMod):
            aux1 = 0
            aux2 = i
            for z,noun in enumerate(self.nounSearch):
                if aux2 < len(paragraphMod) and paragraphMod[aux2].upper() == self.nounSearch[z].upper():
                    aux1 = aux1 + 1
                    aux2 = aux2 + 1
                else:
                    break
            if(aux1 == len(self.nounSearch)):
                self.count = self.count + 1
                if self.count == 1:
                    self.paragshow = paragraph

    def isNoun(self, tag):
        '''Verifica si el tag es relacionado con entidad nombrada
        Devuelve verdadero si el tag corresponde
        '''
        if tag in ['nc00000', 'nc0n000', 'nc0p000', 'nc0s000', 'np00000']:
            return True
        return False
