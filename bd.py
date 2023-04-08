import json
import pymysql

def GuardarBD(producto, Archivojson):

    #verificar que producto no tenga espacios
    producto=producto.replace(" ","")

    # Conecta a la base de datos
    conn = pymysql.connect(
        host='localhost',
        user='root',
        password='holamundo',
        database='productos'
    )

    # Abre el archivo JSON
    with open(Archivojson) as f:
        prods = json.load(f)

    ##falta validar que la tabla a crear todavía no esté creada

    cursor=conn.cursor()

    #crear la tabla

    #sql = f"CREATE TABLE `{producto}` (link VARCHAR(300), Titulo VARCHAR(200), Precio VARCHAR(20), EnvGratis VARCHAR(50), MasVendido VARCHAR(50))"
    sql = f"CREATE TABLE `{producto}` (Imagen VARCHAR(1000), link VARCHAR(2000), Titulo VARCHAR(200), Precio int, EnvGratis VARCHAR(50), MasVendido VARCHAR(50))"
    #print(sql)

    cursor.execute(sql)

    # Recorre la lista de productos y guarda los datos en la tabla
    for prod in prods:
        imagen=prod['imagen']
        link = prod['link']
        titulo = prod['titulo']
        #precio = prod['precio']
        precio = (prod['precio']).replace(".","")
        env_gratis = prod['EnvGratis']
        mas_vendido = prod['MasVendido']
        consulta = f"INSERT INTO {producto} (imagen, Link, Titulo, Precio, EnvGratis, MasVendido) VALUES ('{imagen}', '{link}', '{titulo}', '{precio}', '{env_gratis}', '{mas_vendido}')"
        
        #print(consulta)
        cursor.execute(consulta)
        #print("h")

    # Guarda los cambios en la base de datos y cierra la conexión
    conn.commit()
    conn.close()


#GuardarBD("iphone13", "data_iphone 13.json")