import requests
from bs4 import BeautifulSoup
import json
import pymysql
import os

def ofertasEB():
    # Establecer la URL de la página que se quiere analizar
    url = 'https://www.ebay.com/globaldeals'

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

    # Encontrar todos los elementos li con class="promotion-item default"
    div_list = soup.find_all('div', class_='col')

    # Recorrer cada elemento li y extraer la información relevante
    results = []

    n = 0
    trash_price=["'","COP $", " "]
    for div in div_list:
        # Encontrar imagen (src)
        img = div.find('div', {'class': 'slashui-image-cntr'}) #promotion-item__img-container
        if img:
            imagen = img.find('img').get('src')
        else:
            imagen = ''

        # Encontrar el enlace
        '''
        try:
            link = div.find('div', class_='dne-itemtile dne-itemtile-medium')['href']
        except (KeyError, TypeError):
            link = ""
        '''
        enlace = div.find('div', class_='dne-itemtile dne-itemtile-medium')
        if enlace:
            link = enlace.find('a').get('href')
        else:
            link = ''


        # Encontrar el título
        try:
            titulo = div.find('span', class_='ebayui-ellipsis-2').text.strip()
        except (AttributeError, TypeError):
            titulo = ""

        # Intentar encontrar el precio
        try:
            precio = div.find('span', class_='first').text.strip()
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
        except (AttributeError, TypeError):
            precio = ""

        # % de Descuento
        try:
            descuento = div.find('span', class_='itemtile-price-strikethrough').text.strip()
        except (AttributeError, TypeError):
            descuento = ""

        # Envío
        '''
        try:
            envio = li.find('span', class_='promotion-item__next-day-text').text.strip()
        except (AttributeError, TypeError):
            envio = ""
        '''
        envio = ""

        # Agregar la información a la lista de resultados
        n += 1
        result = {
            "Resultado # ": n,
            "imagen": imagen,
            "link": link,
            "titulo": titulo,
            "precio": precio,
            "envio": envio,
            "Descuento": descuento
        }
        results.append(result)

    # Abrir el archivo data.json y escribir los resultados en él
    with open("data_ofertaseb.json", "w") as outfile:
        json.dump(results, outfile)

    # Crear la tabla e insertar los datos de las ofertas (contenidos en el .json) en ella

    # Conecta a la base de datos
    conn = pymysql.connect(
        host='localhost',
        user='root',
        password='Juan1234',
        database='productos'
    )

    # Abre el archivo JSON
    with open("data_ofertaseb.json") as f:
        prods = json.load(f)

    ##falta validar que la tabla a crear todavía no esté creada, y si es así, borrarla

    cursor=conn.cursor()

    #crear la tabla

    #sql = f"CREATE TABLE `{producto}` (link VARCHAR(300), Titulo VARCHAR(200), Precio VARCHAR(20), EnvGratis VARCHAR(50), MasVendido VARCHAR(50))"

    '''
    try:
        # Crear la tabla en database de mysql
        cursor.execute("CREATE TABLE OFERTAS (Imagen VARCHAR(2000), link VARCHAR(2000), Titulo VARCHAR(200), Precio int, Envio VARCHAR(100), Descuento VARCHAR(100))")

    except:
        # Ejecutar la sentencia SQL para eliminar la tabla, en caso de que esté creada en la database y crearla de nuevo
        cursor.execute("DROP TABLE OFERTAS")
        cursor.execute("CREATE TABLE OFERTAS (Imagen VARCHAR(2000), link VARCHAR(2000), Titulo VARCHAR(200), Precio int, Envio VARCHAR(100), Descuento VARCHAR(100))")
    '''

    # Recorre la lista de productos y guarda los datos en la tabla
    for prod in prods:
        imagen=prod['imagen']
        link = prod['link']
        titulo = prod['titulo']
        titulo = titulo.replace("'", "")

        precio = prod['precio']
        '''
        try:
            precio = (prod['precio']).replace(".","")
        except:
            precio= prod['precio']
        '''
                
        envio = prod['envio']
        descuento = prod['Descuento']
        consulta = f"INSERT INTO OFERTAS (imagen, Link, Titulo, Precio, Envio, Descuento) VALUES ('{imagen}', '{link}', '{titulo}', '{precio}', '{envio}', '{descuento}')"

        cursor.execute(consulta)

    # Eliminar el archivo .json
    os.remove("data_ofertaseb.json")

    # Guarda los cambios en la base de datos y cierra la conexión
    conn.commit()
    conn.close()