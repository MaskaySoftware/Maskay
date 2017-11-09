# -*- coding: utf-8 -*-
'''Clase que obtiene y actualiza los documentos PDF de la base de datos'''
from pymongo import MongoClient


class Documents:
    '''Clase que obtiene y actualiza los documentos PDF de la base de datos'''
    client = None
    db = None
    documents = None

    def __init__(self, *args, **kwargs):
        '''Constructor de la clase'''
        self.client = MongoClient()
        self.db = self.client.Maskay
        self.documents = self.db.documents

    def search(self, dominio):
        '''Busca los documentos en base de datos dato un dominio'''
        searched = []
        for doc in self.documents.find({"url_extraccion": dominio}):
            searched.append(doc)
        return searched

    def updateNumVisitas(self, document):
        '''Actualizar el número de visitas'''
        pass

    def updateAnaTxt(self, document):
        '''Actualiza el documento para
        informar que ha sido analizado como PDF de texto
        '''
        result = self.documents.update_one({"_id":document["_id"]},{"$set":{"ana_text":1}})
        if (result.modified_count == 1):
            return True
        return False

    def updateAnaImg(self, document):
        '''Actualiza el documento para
        informar que ha sido analizado como PDF de imágen
        '''
        result = self.documents.update_one({"_id":document["_id"]},{"$set":{"ana_img":1}})
        if (result.modified_count == 1):
            return True
        return False
