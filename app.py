# --------------Librerias-------------------
from flask import Flask, send_from_directory
from flask import render_template
from flaskext.mysql import MySQL
import os


# instanciación de la aplicación
app = Flask(__name__)

mysql = MySQL()

app.config["MYSQL_DATABASE_HOST"] = "localhost"
app.config["MYSQL_DATABASE_USER"] = "root"
app.config["MYSQL_DATABASE_PASSWORD"] = "Juan1234"
app.config["MYSQL_DATABASE_DB"] = "productos"

mysql.init_app(app)

# Ruta para la pagina inicial
@app.route('/')
def inicio():
    return render_template('index.html') # Se retorna el html de la pagina de incio

# Ruta para la pagian del catalogo
@app.route('/catalogo')
def catalogo():

    conexion = mysql.connect()
    cursor = conexion.cursor()
    cursor.execute("""SELECT * FROM audifonossamsung""")
    products = cursor.fetchall()
    conexion.commit()

    return render_template('catalogo.html', products = products) # Se retorna el html de la pagina de catalogo

# Ruta para la pagian de nosotros
@app.route('/nosotros')
def nosotros():
    return render_template('nosotros.html') # Se retorna el html de la pagina de nosotros

# Ruta para la pagian de contactanos 
@app.route('/contactanos')
def contactanos():
    return render_template('contactanos.html') # Se retorna el html de la pagina de contactanos

# Ruta para reconocer y usar los archivos css
@app.route('/css/<archivo>')
def css_link(archivo):
    return send_from_directory(os.path.join('templates/css'), archivo) # Se retorna la direccion a la carpeta de archivos css

# Ruta para reconocer y usar las imagenes
@app.route('/images/<img>')
def img_link(img):
    return send_from_directory(os.path.join('templates/images'), img) # Se retorna la direccion a la carpeta de las imagenes



if __name__ == "__main__":
    app.run(debug=True)