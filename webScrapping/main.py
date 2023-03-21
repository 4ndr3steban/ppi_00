import requests

def run(producto):
    headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36'
    }
    url = 'https://www.amazon.com/s?k=' + producto + '&crid=2IWE3L3QVKL69&sprefix=%2Caps%2C153&ref=nb_sb_ss_sx-trend-t-ps-d_2_0'
    print(url)
    response=requests.get(url, headers = headers)

    print(response)

    if response.status_code==200:
        content=response.content
        print(content)

        file=open('amazon.html','wb')
        file.write(content)
        file.close

#busqueda=input('Ingresa el articulo que deseas comprar: ')

busqueda='alexa'

run(busqueda)