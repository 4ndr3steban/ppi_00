import json
import requests
from bs4 import BeautifulSoup
import bd
import merLib
import ebay

def guardar(producto):
    resultado=[]
    resultsMerLib = merLib.merLib1(producto, resultado)
    results = ebay.ebay1(producto, resultsMerLib)

    # Abrir el archivo data.json y escribir los resultados en él
    with open("data_" + producto + ".json", "w") as outfile:
        json.dump(results, outfile)

    print(producto, outfile.name)

    # Ejecutar funcion que crea la tabla e inserta los datos del producto (contenidos en el .json) en ella
    bd.GuardarBD(producto, outfile.name)


# Definir el producto a buscar en Mercado Libre Colombia

#busqueda=input('Escribe el producto que quieres comprar: ')
busqueda='iPad'
guardar(busqueda)