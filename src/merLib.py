import requests
from bs4 import BeautifulSoup

def merLib1(producto, results):
    # Establecer la URL de la página que se quiere analizar
    url = 'https://listado.mercadolibre.com.co/' + producto

    # Establecer los encabezados para la solicitud
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.5'
    }

    # Enviar la solicitud GET a la URL con los encabezados
    response = requests.get(url, headers=headers)

    print(url)
    print(response)
    #print(response.content)

    # Analizar el contenido HTML de la página con BeautifulSoup
    soup = BeautifulSoup(response.content, 'html.parser')

    # Encontrar todos los elementos li con class="ui-search-layout__item shops__layout-item"
    li_list = soup.find_all('li', class_='ui-search-layout__item shops__layout-item')

    #2
    #li_list = soup.find_all('li', class_='ui-search-layout__item')

    # Recorrer cada elemento li y extraer la información relevante
    #results = []
    n=0
    for li in li_list:

        # Encontrar imagen (src)
    
        img = li.find('div', {'class':'slick-slide slick-active'})
        if img: #.find('img').get('src')!="data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP": 
            imagen = img.find('img').get('data-src')
        else:
            imagen = ''

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

    return results


#### 

def merLib2(producto, results):
    # Establecer la URL de la página que se quiere analizar
    url = 'https://listado.mercadolibre.com.co/' + producto

    # Establecer los encabezados para la solicitud
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.5'
    }

    # Enviar la solicitud GET a la URL con los encabezados
    response = requests.get(url, headers=headers)

    print(url)
    #print(response)
    print(response.content)

    # Analizar el contenido HTML de la página con BeautifulSoup
    soup = BeautifulSoup(response.content, 'html.parser')

    # Encontrar todos los elementos li con class="ui-search-layout__item"
    li_list = soup.find_all('li', class_='ui-search-layout__item')

    # Recorrer cada elemento li y extraer la información relevante
    #results = []
    n=0
    for li in li_list:

        # Encontrar imagen (src)
    
        img = li.find('div', {'class':'slick-slide slick-active'})
        if img: #.find('img').get('src')!="data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP": 
            imagen = img.find('img').get('data-src')
        else:
            imagen = ''

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

    return results