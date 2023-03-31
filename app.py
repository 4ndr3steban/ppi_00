from flask import Flask, send_from_directory
from flask import render_template, request, redirect
from flaskext.mysql import MySQL
import os
import main_ML




# instanciación de la aplicación
app = Flask(__name__)

mysql = MySQL()

app.config["MYSQL_DATABASE_HOST"] = "localhost"
app.config["MYSQL_DATABASE_USER"] = "root"
app.config["MYSQL_DATABASE_PASSWORD"] = ""
app.config["MYSQL_DATABASE_DB"] = "productos"

mysql.init_app(app)

# Ruta para la pagina inicial
@app.route('/', methods = ["GET", "POST"])
def inicio():
    return render_template('index.html') # Se retorna el html de la pagina de incio


@app.route("/buscar-producto", methods = ["GET", "POST"])
def buscar_producto():
    if request.method == "POST":
        busqueda = request.form['busqueda']
        main_ML.guardar(busqueda)

        aux = busqueda.replace(" ", "")
        conexion = mysql.connect()
        cursor = conexion.cursor()
        cursor.execute("SELECT * FROM %s " % (aux))
        productos = cursor.fetchall()
        conexion.commit()
        return render_template('resultbusqueda.html', productos = productos, busqueda = busqueda)
    
    return redirect("/")


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