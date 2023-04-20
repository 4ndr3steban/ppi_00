import requests
from bs4 import BeautifulSoup

def ebay1(producto, results):
    # Establecer la URL de la página que se quiere analizar
    url= 'https://www.ebay.com/sch/i.html?_from=R40&_trksid=p2380057.m570.l1313&_nkw='+ producto+'&_sacat=0'
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

    # Encontrar todos los elementos li con class="s-item s-item__pl-on-bottom"
    li_list = soup.find_all('li', class_='s-item s-item__pl-on-bottom')

    # Recorrer cada elemento li y extraer la información relevante
    #results = []
    n=100
    for li in li_list:

        # Encontrar imagen (src)
    
        img = li.find('div', {'class':'s-item__image-wrapper image-treatment'})
        if img: #.find('img').get('src')!="data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP": 
            imagen = img.find('img').get('src')
        else:
            imagen = ''

        # Encontrar el enlace
        try:
            link = li.find('a', class_='s-item__link')['href']
        except (KeyError, TypeError):
            link = ""

        # Encontrar el título
        try:
            titulo = li.find('div', class_='s-item__title').text.strip()
        except (AttributeError, TypeError):
            titulo = ""

        # Intentar encontrar el precio
        try:
            precio = li.find('span', class_='s-item__price').text.strip()
            pre=precio.replace("COP $","")
            pre=pre.replace(" ","")
            #pre=pre.replace(".","")
            pre=pre.replace("$","")
            pre=pre.replace("\u00a0","")
            if pre.find("a")!=-1:
                pre=pre[(pre.find("a")+1):len(precio)]

            if pre.find(".")!=-1:
                pre=pre[0:pre.find(".")]

            precio=int(pre)
            #precio=pre
        except (AttributeError, TypeError):
            precio = ""

        ## Intentar encontrar la etiqueta MasVendido
        # try:
        #     MasVendido = li.find('label', class_='ui-search-styled-label ui-search-item__highlight-label__text').text.strip()
        # except (AttributeError, TypeError):
        #     MasVendido = ""
        MasVendido = ""
        # Intentar encontrar la etiqueta EnvGratis
        try:
            EnvGratis = li.find('span', class_='s-item__shipping s-item__logisticsCost').text.strip()
            if EnvGratis!="Env\u00edo internacional gratis":
                EnvGratis=""
        except (AttributeError, TypeError):
            EnvGratis = ""

        # Agregar la información a la lista de resultados
        
        if titulo!="Shop on eBay":
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