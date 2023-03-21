import json
from bs4 import BeautifulSoup

# Abre el archivo HTML
with open('amazon_alexa.html', 'r') as file:
    html = file.read()

# Analiza el HTML con BeautifulSoup
soup = BeautifulSoup(html, 'html.parser')

# Busca todos los divs con la clase especificada
divs = soup.find_all('div', {'class': 'sg-col-20-of-24 s-result-item s-asin sg-col-0-of-12 sg-col-16-of-20 sg-col s-widget-spacing-small sg-col-12-of-16'})
contador = 0

# Procesa cada div
for div in divs:
    # Busca la etiqueta img y obtiene el atributo src
    img = div.find('img', {'class': 's-image'})
    link = img.get('src') if img else ''

    # Busca la etiqueta span con el título y obtiene el texto
    title_span = div.find('span', {'class': 'a-size-medium a-color-base a-text-normal'})
    title = title_span.text if title_span else ''

    # Busca la etiqueta span con la valoración y obtiene el texto
    rating_span = div.find('span', {'class': 'a-icon-alt'})
    rating = rating_span.text if rating_span else ''

    # Busca la etiqueta span con el precio y obtiene el texto
    price_span = div.find('span', {'class': 'a-price-whole'})
    price = price_span.text if price_span else ''

    # Escribe los datos en un archivo JSON
    with open('data2.json', 'a') as file:
        contador += 1
        data = {'Producto #': contador, 'link': link, 'title': title, 'rating': rating, 'price': price}
        json.dump(data, file)
        file.write('\n')
