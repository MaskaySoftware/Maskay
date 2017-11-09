# -*- coding: utf-8 -*-
'''Ejecuta el componente de extracción'''
import sys
import json
import threading
from urlparse import urlparse
from Documents import Documents
from TransformPDF import TransformPDF
from ExtractPDF import ExtractPDF

# Variables

searchInNoun = []
pdf_show = []
pdf_img = []
pdf_listos = []
pdfimg = None


def start(page, palabra):
    '''Crea el paralelismo para ejecutar el componente de extracción
    Imprime en consola el resultado de la extracción
    Parámetros
    page -- URL de la página solicitada
    palabra -- Cadena de texto con la palabra de búsqueda
    '''
    parse_url = urlparse(page)
    dominio = parse_url.scheme + "://" + parse_url.netloc
    documents = Documents()
    # Obtenga todos los documentos del dominio ingresado
    docs = documents.search(dominio)
    extract = ExtractPDF(None, palabra)
    palabras = extract.searchToNoun()
    if len(docs) > 4:
        threads = []
        len1 = int(round(1.0/4*len(docs)))
        len2 = int(round(1.0/2*len(docs)))
        len3 = int(round(3.0/4*len(docs)))
        threads.append(threading.Thread(target=startPDF, args=(docs[:len1], palabra, palabras)))
        threads.append(threading.Thread(target=startPDF, args=(docs[len2:len3], palabra, palabras)))
        threads.append(threading.Thread(target=startPDF, args=(docs[len3:], palabra, palabras)))
        [thread.start() for thread in threads]
        [thread.join() for thread in threads]
    else:
        startPDF(docs, palabra, palabras)
    print(json.dumps(pdf_show))


def startPDF(docs, palabra, palabras):
    '''Ejecuta el componente de extracción
    Parámetros
    docs -- Arreglo con los documentos a examinar
    palabra -- Cadena de texto con la palabra de búsqueda
    palabras -- Arreglo con las entidades nombradas encontradas en la palabra
    '''
    for doc in docs:
        transform = TransformPDF(doc)
        bandera = transform.pdfToTxt()
        if(bandera is False):
            pdf_img.append(doc)
            if pdfimg == "true":
                transform.pdfImg2Txt()
        else:
            pdf_listos.append(doc)
            extract = ExtractPDF(doc, palabra, palabras)
            count = extract.searchInPDF()
            if count > 0:
                pdf_show.append([doc["url_pdf"], extract.getParagraphShow(), count])


if __name__ == "__main__":
    '''Ejecuta el método principal'''
    a = str(sys.argv[1])
    b = str(sys.argv[2])
    pdfimg = str(sys.argv[3])
    start(a, b)
