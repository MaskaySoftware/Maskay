# -*- coding: utf-8 -*-
'''Busca y actualiza la colleción Paginas en la base de datos
Adicional envia correos de las páginas que cambian de estado
'''
import pymongo
from pymongo import MongoClient
import pprint
import json
import smtplib
from email.MIMEText import MIMEText
from bson.objectid import ObjectId


class Page(object):
    '''Busca y actualiza la colleción Paginas en la base de datos
    Adicional envia correos de las páginas que cambian de estado
    '''
    def __init__(self):
        '''Constructor de la clase'''
        self.client = MongoClient()
        self.db = self.client.Maskay
        self.page = None
        self.pages = self.db.pages
        self.emails = self.db.emails

    def searchPage(self, url):
        ''' Busca el objecto de base de datos dado un URL
        Asigna
        Parámetros:
        url -- Cadena de texto del URL a buscar
        '''
        self.page = self.pages.find_one({"url": url})

    def updatePage(self, duration):
        if self.page is None:
            return
        result = self.pages.update_one({"_id": self.page["_id"]}, {"$set": {"duration": duration, "status": "Finished"}})
        if (result.modified_count == 1):
            return True
        return False

    def searchEmails(self):
        searched = []
        for email in self.emails.find({"url_requested": self.page["_id"] , "status": "not_sent"}):
            searched.append(email["email"])
        return searched

    def searchPageId(self, id, status):
        self.page = self.pages.find_one({"_id": ObjectId(str(id)), "status": status})
        return self.page

    def sendEmails(self):
        if self.page == None:
            return
        emisor = "maskaysoftware@gmail.com"
        receptor = self.searchEmails()
        if len(receptor) == 0:
            return
        # Configuracion del mail 
        remitente = "Maskay <maskaysoftware@gmail.com>"
        asunto = "Maskay - Página lista para la búsqueda" 
        mensaje = """
<!DOCTYPE html>
<html lang="es">
    <head>
        <title>Correo</title>
        <meta charset="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1">
    </head>
    <body>
Buen día!<br/> <br/> 
La página que solicitó para ser examinada ya está lista.
<br />
Ingrese en nuestra página y vuelva a intentar la búsqueda, ingrese la entidad nombrada, la página y de clic en buscar.
<br />
<a href='http://186.154.95.101/maskay/'>http://186.154.95.101/maskay/</a> 
<br />
Gracias por su espera.
</body>
</html>
        """
         
        email = """From: %s 
MIME-Version: 1.0 
Content-type:text/html;charset=UTF-8
Subject: %s 
 
%s""" % (remitente, asunto, mensaje) 
        try:
            # Nos conectamos al servidor SMTP de Gmail 
            serverSMTP = smtplib.SMTP('smtp.gmail.com',587) 
            serverSMTP.ehlo() 
            serverSMTP.starttls() 
            serverSMTP.ehlo() 
            serverSMTP.login(emisor,"M4sk4yS0ft") 
                
            # Enviamos el mensaje 
            serverSMTP.sendmail(emisor,receptor,email) 
               
            # Cerramos la conexion 
            serverSMTP.close()
            self.updateEmails("sent")
        except Exception:
            print "Unknown error:", sys.exc_info()[0]

    def updateEmails(self, status):
        result = self.emails.update({"url_requested": self.page["_id"] },{"$set":{"status": status}})
        return result["nModified"]  
