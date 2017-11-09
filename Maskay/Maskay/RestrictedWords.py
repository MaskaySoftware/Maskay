# -*- coding: utf-8 -*-
'''Clase que obtiene las palabras restringidas registradas en la base de datos'''
from pymongo import MongoClient


class RestrictedWords(object):
    '''Clase que obtiene las palabras restringidas registradas en la base de datos'''
    def __init__(self):
        self.client = MongoClient()
        self.database = self.client.Maskay
        self.words = self.database.words

    def search(self):
        '''Método que busca en base de datos todas las palabras'''
        searched = []
        for word in self.words.find({}):
            searched.append(word)
        return searched

    def searchByWord(self, word):
        '''Método que busca en base de datos la palabra'''
        searched = []
        for word in self.words.find({"word": word}):
            searched.append(word)
        return searched
