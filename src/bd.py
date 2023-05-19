import json
import pymysql

def GuardarBD(producto, Archivojson):
    """Guarda el producto en la base de datos
    
    La funcion permite que se guarden los productos del archivo
    JSON a la base de datos por medio de una tabla, guardando toda 
    su informacion.
    """

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
    sql = f"""CREATE TABLE `{producto}` (Imagen VARCHAR(2000), link VARCHAR(2000), Titulo VARCHAR(200),
            Precio int, EnvGratis VARCHAR(50), MasVendido VARCHAR(50), Pagina VARCHAR(30))"""
    #print(sql)

    cursor.execute(sql)

    # Recorre la lista de productos y guarda los datos en la tabla
    for prod in prods:
        imagen=prod['imagen']
        link = prod['link']
        titulo = prod['titulo']
        #precio = prod['precio']
        try:
            # Se formatea el precio
            precio = (prod['precio']).replace(".","")
        except:
            # No se formatea si no es necesario
            precio= prod['precio']
            
        env_gratis = prod['EnvGratis']
        mas_vendido = prod['MasVendido']

        if link.find("mercadolibre")!=-1:
            pagina="Mercado Libre"
        else:
            pagina="eBay"

        # Consulta para la base de datos
        consulta = f"""INSERT INTO {producto} (imagen, Link, Titulo, Precio, EnvGratis, MasVendido, Pagina) VALUES
                      ('{imagen}', '{link}', '{titulo}', '{precio}', '{env_gratis}', '{mas_vendido}', '{pagina}')"""
        
        #print(consulta)
        cursor.execute(consulta)
        #print("h")

    # Guarda los cambios en la base de datos y cierra la conexión
    conn.commit()
    conn.close()