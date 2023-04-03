from flask import Flask, send_from_directory
from flask import render_template, request, redirect
from flaskext.mysql import MySQL
import os
import main_ML


# instanciación de la aplicación
app = Flask(__name__)

mysql = MySQL()

"""
# variables de configuracion de la base de datos online
app.config["MYSQL_DATABASE_HOST"] = 'sql10.freemysqlhosting.net'
app.config["MYSQL_DATABASE_USER"] = 'sql10609996'
app.config["MYSQL_DATABASE_PASSWORD"] = 'VYzVtXawXQ'
app.config["MYSQL_DATABASE_DB"] = 'sql10609996'
"""

# variables de configuracion de la base de datos de productos
app.config["MYSQL_DATABASE_HOST"] = 'localhost'
app.config["MYSQL_DATABASE_USER"] = 'root'
app.config["MYSQL_DATABASE_PASSWORD"] = ''
app.config["MYSQL_DATABASE_DB"] = 'productos'

mysql.init_app(app)


# Ruta para la pagina inicial
@app.route('/', methods = ["GET", "POST"])
def inicio():
    return render_template('index.html') # Se retorna el html de la pagina de incio


# Ruta para la pagian del catalogo
@app.route('/catalogo', methods = ["Get"])
def catalogo():

    return render_template('catalogo.html') # Se retorna el html de la pagina de catalogo


# Ruta para la pagian de nosotros
@app.route('/nosotros', methods = ["Get"])
def nosotros():
    return render_template('nosotros.html') # Se retorna el html de la pagina de nosotros


# Ruta para la pagian de contactanos 
@app.route('/contactanos', methods = ["Get"])
def contactanos():
    return render_template('contactanos.html') # Se retorna el html de la pagina de contactanos


@app.route('/signup', methods= ["GET", "POST"])
def registro():
    return render_template("signup.html")


@app.route('/login', methods= ["GET", "POST"])
def login():
    return render_template("login.html")


# Ruta para buscar un producto y mostrar los resultados 
@app.route("/buscar-producto", methods = ["GET", "POST"])
def buscar_producto():
    if request.method == "POST":

        busqueda = request.form['busqueda'] # Se obtiene la busqueda que ingresa el usuario

        try:
            main_ML.guardar(busqueda) # se guarda el producto buscado en una base de datos haciendo web scraping
        except:
            pass

        aux = busqueda.replace(" ", "") # Esta variable guarda el nombre de la tabla
        
        # Se genera una conexion a la base de datos y se extraen los productos recien guardados
        conexion = mysql.connect()
        cursor = conexion.cursor()
        cursor.execute("SELECT * FROM %s " % (aux))
        productos = cursor.fetchall()
        conexion.commit()

        # Eliminar del directorio de trabajo el archivo auxiliar creado para la base de datos
        os.remove("data_"+aux+".json") 

        # Se muestran los resultados de la busqueda
        return render_template('resultbusqueda.html', productos = productos, busqueda = busqueda)
    
    return redirect("/")


@app.route("/guardar-email", methods = ["GET", "POST"])
def guardar_email():
    if request.method == "POST":

        busqueda = request.form['email_no_user'] # Se obtiene la busqueda que ingresa el email
        conexion = mysql.connect()
        cursor = conexion.cursor()
        print(busqueda)
        try:
            ingreso = f"INSERT INTO emails (mail) VALUES ('{busqueda}')"
            cursor.execute(ingreso)
        except:
            pass
        conexion.commit()
        
        return render_template('index.html')
    
    return redirect("/")


# Ruta para reconocer y usar los archivos css
@app.route('/static/css/<archivo>', methods = ["Get"])
def css_link(archivo):
    return send_from_directory(os.path.join('templates/static/css'), archivo) # Se retorna la direccion a la carpeta de archivos css


# Ruta para reconocer y usar las imagenes
@app.route('/static/images/<img>', methods = ["Get"])
def img_link(img):
    return send_from_directory(os.path.join('templates/static/images'), img) # Se retorna la direccion a la carpeta de las imagenes


if __name__ == "__main__":
    app.run(debug=True)