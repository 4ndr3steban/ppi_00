import json
import requests
from bs4 import BeautifulSoup
import bd

def guardar(producto):
    # Establecer la URL de la página que se quiere analizar
    url = 'https://listado.mercadolibre.com.co/'+producto

    # Establecer los encabezados para la solicitud
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.5'
    }

    # Enviar la solicitud GET a la URL con los encabezados
    response = requests.get(url, headers=headers)

    print(response)

    # Analizar el contenido HTML de la página con BeautifulSoup
    soup = BeautifulSoup(response.content, 'html.parser')

    # Encontrar todos los elementos li con class="ui-search-layout__item shops__layout-item"
    li_list = soup.find_all('li', class_='ui-search-layout__item shops__layout-item')

    # Recorrer cada elemento li y extraer la información relevante
    results = []
    n=0
    for li in li_list:

        # Encontrar imagen (src)
        """
        try:
            img = li.find('div', class_="slick-slide slick-active")['src']
        except (KeyError, TypeError):
            img = ""
        """
        # Busca la etiqueta img y obtiene el atributo src
        
        """
        img = li.find('div', {'class': 'slick-slide slick-active'})
        imagen = img.get('src') #if img else ''
        """

        img = li.find('div', {'data-index': '0'})
        if img.find('img').get('src')!="data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP": 
            imagen = img.find('img').get('src')
        else:
            imagen = ''


        """
        img = li.find('img', {'class': 'ui-search-result-image__element shops__image-element'})
        imagen = img.get('src') #if image else ''
        """

        # Encontrar el enlace
        try:
            link = li.find('a', class_='ui-search-link')['href']
        except (KeyError, TypeError):
            link = ""

        # Encontrar el título
        try:
            titulo = li.find('h2', class_='ui-search-item__title shops__item-title').text.strip()
        except (AttributeError, TypeError):
            titulo = ""

        # Intentar encontrar el precio
        try:
            precio = li.find('span', class_='price-tag-fraction').text.strip()
        except (AttributeError, TypeError):
            precio = ""

        # Intentar encontrar la etiqueta MasVendido
        try:
            MasVendido = li.find('label', class_='ui-search-styled-label ui-search-item__highlight-label__text').text.strip()
        except (AttributeError, TypeError):
            MasVendido = ""

        # Intentar encontrar la etiqueta EnvGratis
        try:
            EnvGratis = li.find('p', class_='ui-search-item__shipping ui-search-item__shipping--free shops__item-shipping-free').text.strip()
        except (AttributeError, TypeError):
            EnvGratis = ""

        # Agregar la información a la lista de resultados
        n+=1
        result = {
            "Resultado # ": n,
            "imagen": imagen,
            "link": link,
            "titulo": titulo,
            "precio": precio,
            "EnvGratis": EnvGratis,
            "MasVendido": MasVendido
        }
        results.append(result)

    # Abrir el archivo data.json y escribir los resultados en él
    with open("data_"+producto+".json", "w") as outfile:
        json.dump(results, outfile)

    print(producto, outfile.name)

    # Ejecutar funcion que crea la tabla e inserta los datos del producto (contenidos en el .json) en ella
    bd.GuardarBD(producto, outfile.name)


# Definir el producto a buscar en Mercado Libre Colombia

#busqueda=input('Escribe el producto que quieres comprar: ')
busqueda='iphone 12'

guardar(busqueda)