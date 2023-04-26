from flask import Flask, send_from_directory
from flask import render_template, request, redirect, flash, current_app, url_for
from flaskext.mysql import MySQL
from flask_mail import Mail, Message
from flask_login import LoginManager, login_user, logout_user, login_required
from werkzeug.security import generate_password_hash
import logging
from smtplib import SMTPException
from threading import Thread
import os
import main
from modelos.Modelusuario import ModelUser
from modelos.entidades.usuario import User

# instanciación de la aplicación
app = Flask(__name__)

mysql = MySQL()

# variables de configuracion de la base de datos
app.config["MYSQL_DATABASE_HOST"] = 'localhost'
app.config["MYSQL_DATABASE_USER"] = 'root'
app.config["MYSQL_DATABASE_PASSWORD"] = ''
app.config["MYSQL_DATABASE_DB"] = 'productos'

mysql.init_app(app)


# Configuracion de las variables para enviar y recibir mensajes
mail = Mail()  
app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'pricescaner00@gmail.com'
app.config['MAIL_PASSWORD'] = 'useogrmuixgzvqbx'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail.init_app(app)

# Instancia para capturar errores en el envio de emails
logger = logging.getLogger(__name__)


# Funcion 1 para enviar correos de forma asincronica
def _send_async_email(app, msg):
    """Envia el mail con el metodo send
    
    captura el error de envio en caso de ocurrir
    """

    with app.app_context():
        try:
            mail.send(msg)
        except SMTPException:
            logger.exception("Ocurrió un error al enviar el email")


# Funcion 2 para enviar correos de forma asincronica
def send_email(subject, sender, recipients, text_body, cc=None, bcc=None, html_body=None):
    """Crea la instancia del mensaje y lo envia
    
    llama a la funcion _send_async_email y la ejecuta por
    otro hilo de procesamiento (se envia de forma asincronuca)
    """

    msg = Message(subject, sender=sender, recipients=recipients, cc=cc, bcc=bcc)
    msg.body = text_body
    if html_body:
        msg.html = html_body
    Thread(target=_send_async_email, args=(current_app._get_current_object(), msg)).start()


# Llave para usar en las contraseñas (hash)
app.secret_key = "price_scaner_ppi_00"

# Gestion y manejo de sesiones 
login_manager_app = LoginManager(app)

@login_manager_app.user_loader
def load_user(id):
    return ModelUser.get_by_id(mysql, id)


# Ruta para la pagina inicial
@app.route('/', methods = ["GET", "POST"])
def inicio():
    return render_template('index.html') # Se retorna el html de la pagina de incio


# Ruta para la pagina del catalogo
@app.route('/catalogo-reg', methods = ["GET"])
@login_required
def catalogo():

    # Se genera una conexion a la base de datos y se extraen los productos recien guardados
    conexion = mysql.connect()
    cursor = conexion.cursor()
    cursor.execute("SELECT * FROM ofertas")
    ofertas = cursor.fetchall()
    conexion.commit()

    return render_template('catalogo_reg.html', ofertas = ofertas) # Se retorna el html de la pagina de catalogo

# Ruta para la pagina de home
@app.route('/home', methods = ["GET"])
@login_required
def home():
    return render_template('home.html') # Se retorna el html de la pagina de home

# Ruta para la pagian de nosotros
@app.route('/nosotros', methods = ["GET"])
def nosotros():
    return render_template('nosotros.html') # Se retorna el html de la pagina de nosotros



# Ruta para la pagian de contactanos 
@app.route('/contactanos', methods = ["GET","POST"])
def contacto():

    if request.method == "POST":

        # Variables tomadas del formulario de la vista "Contactanos"
        name = request.form['name']
        email = request.form['email']
        Mensaje = request.form['message']
        print(name,email,Mensaje)

        send_email(subject = f"pricescaner_contacto: {email}",
                   sender = (name, email),
                   recipients = ["pricescaner@yahoo.com"],
                   text_body = Mensaje)

    return render_template("contactanos.html") # Se retorna el html de la pagina de contactanos


# Ruta para el registro de usuarios
@app.route('/signup', methods= ["GET", "POST"])
def registro():

    if request.method == "POST":

        # Variables tomadas del formulario de la vista "signup"
        name = request.form['nombre_reg']
        email = request.form['email_reg']
        password = request.form['pass_reg']

        # Se genera la conexión con la base de datos
        conexion = mysql.connect()
        cursor = conexion.cursor()

        # Variable para controlar si el usuario ya existía
        cursor.execute("SELECT email FROM usuarios WHERE email = %s", (email))
        aux = cursor.fetchone()
        print(aux)
        if aux == None:

            # Si el usuario no existe se guarda en la base de datos
            cursor.execute("INSERT INTO usuarios (nombre, email, password) VALUES (%s,%s,%s)", 
                           (name, email, generate_password_hash(password),))
            conexion.commit()

            flash("Usuario registrado, por favor inicie sesión", "info")

            return redirect('/login') # Se envia a logearse
        else:

            # Se muesta un mensaje si el usuario es existente
            flash("Usuario existente, por favor registrese con otro email", "warning")

            return redirect('/signup')

    return render_template("signup.html")


# Ruta para el inicio de sesión de usuarios
@app.route('/login', methods= ["GET", "POST"])
def login():

    if request.method == 'POST':

        # Se instancia un objeto usuario con los datos tomados del formulario
        user = User(0, request.form['email_login'], request.form['pass_login'])
        logged_user = ModelUser.login(mysql, user)
        if logged_user != None:
            if logged_user.password:

                # Funcion para verificar el inicio de sesión del usuario en la bd
                login_user(logged_user)
                return redirect("/home")
            else:

                # Control de contraseña
                flash("Contraseña incorrecta...", "warning")
                return render_template('login.html')
        else:

            # Control de email
            flash("Usuario no encontrado...", category="error")
            return render_template('login.html')

    return render_template("login.html")


# Ruta para terminar la sesión
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/')


@app.route("/restablecer-contrasena", methods= ["GET", "POST"])
def reset_request():

    if request.method == "POST":

        email_recp = request.form['email_reset_password']

        conexion = mysql.connect()
        cursor = conexion.cursor()

        cursor.execute("SELECT id, email, nombre FROM usuarios WHERE email = %s", (email_recp))
        aux = cursor.fetchone()

        if aux == None:
            flash("Usuario no encontrado...", "error")
            
        else:
            user = User(aux[0], aux[1], None, aux[2])
            token = user.get_reset_token()
            print(token)
            print(user.email)

            send_email(subject = "[PRICESCANER] Restablecimiento de contraseña",
                    sender = ("PRICESCANER", "pricescaner@yahoo.com"),
                    recipients = [email_recp],
                    text_body = ".",
                    html_body = render_template("reset_email.html", user = user, token = token))

            flash("Solicitud de restablecimiento enviada. Revise su correo", "info")
            
    
    return render_template("reset_password.html")


@app.route('/restablecer-contrasena-verificado/<token>', methods=['GET', 'POST'])
def reset_verified(token):

    user = User.verify_reset_token(token, mysql)
    print(user[0])
    if not user:
        print('usuario no encontrado')
        flash("Ocurrio un error. Intentelo nuevamente")
        return redirect('/restablecer-contrasena')

    if request.method == "POST":
        password = request.form['respassword']
        passwordsec = request.form['reppassword']

        if password == passwordsec:
            conexion = mysql.connect()
            cursor = conexion.cursor()

            cursor.execute("UPDATE productos.usuarios SET password = %s WHERE (nombre = %s)",
                            (generate_password_hash(password), user[0]))
            conexion.commit()
            flash("Contraseña cambiada exitosamente")
            return redirect('/login')
        
        else:
            flash("Contraseñas diferentes. Intentelo de nuevo", "error")

    return render_template('reset_verified.html')


# Ruta para buscar un producto y mostrar los resultados 
@app.route("/buscar-producto", methods = ["GET", "POST"])
def buscar_producto():
    if request.method == "POST":

        busqueda = request.form['busqueda'] # Se obtiene la busqueda que ingresa el usuario

        try:
            main.guardar(busqueda) # se guarda el producto buscado en una base de datos haciendo web scraping
        except:
            pass

        aux = busqueda.replace(" ", "") # Esta variable guarda el nombre de la tabla
        
        # Se genera una conexion a la base de datos y se extraen los productos recien guardados
        conexion = mysql.connect()
        cursor = conexion.cursor()
        cursor.execute("SELECT * FROM %s " % (aux))
        productos = cursor.fetchall()
        print(productos)
        conexion.commit()

        # Eliminar del directorio de trabajo el archivo auxiliar creado para la base de datos
        os.remove("data_"+busqueda+".json") 

        # Se muestran los resultados de la busqueda
        return render_template('resultbusqueda.html', productos = productos, busqueda = busqueda)
    
    return redirect("/")


@app.route("/buscar-producto-reg", methods = ["GET", "POST"])
def buscar_producto_reg():
    if request.method == "POST":

        busqueda_reg = request.form['busquedareg']
        rango = [request.form['min-price'], request.form['max-price']]
        envio = request.form['envio']

        print(busqueda_reg, rango, envio)
        try:
            main.guardar(busqueda_reg) # se guarda el producto buscado en una base de datos haciendo web scraping
        except:
            pass

        aux = busqueda_reg.replace(" ", "") # Esta variable guarda el nombre de la tabla
        
        # Se genera una conexion a la base de datos y se extraen los productos recien guardados
        conexion = mysql.connect()
        cursor = conexion.cursor()

        if envio == "Si" and rango[0] != "" and rango[1] != "":
            cursor.execute("SELECT * FROM %s WHERE Precio > %s AND Precio < %s AND EnvGratis != '' ORDER BY Precio " % (aux, rango[0], rango[1]))
            productos = cursor.fetchall()
            conexion.commit()

        elif envio == "Si" and rango[0] != "":
            cursor.execute("SELECT * FROM %s WHERE Precio > %s AND EnvGratis != '' ORDER BY Precio " % (aux, rango[0]))
            productos = cursor.fetchall()
            conexion.commit()
        
        elif envio == "Si" and rango[1] != "":
            cursor.execute("SELECT * FROM %s WHERE Precio < %s AND EnvGratis != '' ORDER BY Precio " % (aux, rango[1]))
            productos = cursor.fetchall()
            conexion.commit()

        elif envio == "Si":
            cursor.execute("SELECT * FROM %s WHERE EnvGratis != '' ORDER BY Precio " % (aux))
            productos = cursor.fetchall()
            conexion.commit()

        elif envio == "No" and rango[0] != "" and rango[1] != "":
            cursor.execute("SELECT * FROM %s WHERE Precio > %s AND Precio < %s ORDER BY Precio" % (aux, rango[0], rango[1]))
            productos = cursor.fetchall()
            conexion.commit()

        elif envio == "No" and rango[0] != "":
            cursor.execute("SELECT * FROM %s WHERE Precio > %s ORDER BY Precio" % (aux, rango[0]))
            productos = cursor.fetchall()
            conexion.commit()
        
        elif envio == "No" and rango[1] != "":
            cursor.execute("SELECT * FROM %s WHERE Precio < %s ORDER BY Precio" % (aux, rango[1]))
            productos = cursor.fetchall()
            conexion.commit()

        else:
            cursor.execute("SELECT * FROM %s ORDER BY Precio" % (aux))
            productos = cursor.fetchall()
            conexion.commit()
        

        # Eliminar del directorio de trabajo el archivo auxiliar creado para la base de datos
        os.remove("data_"+busqueda_reg+".json") 
        
        # Se muestran los resultados de la busqueda
        return render_template('resbusqueda_reg.html', productos = productos, busqueda = busqueda_reg)
    return redirect("/")



@app.route("/guardar-email", methods = ["GET", "POST"])
def guardar_email():
    if request.method == "POST":

        busqueda = request.form['email_no_user'] # Se obtiene la busqueda que ingresa el email

        # Se genera la conexión a la base de datos
        conexion = mysql.connect()
        cursor = conexion.cursor()
        print(busqueda)
        try:

            # Se ingresa el correo si este es nuevo en la bd
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


# Control para redireccionar cuando se intenta acceder a ciertas paginas sin logearse
def status_401(error):
    return redirect('/login')


# Control para paginas que no existen 
def status_404(error):
    return "<h1>Página no encontrada</h1>", 404


if __name__ == "__main__":
    app.register_error_handler(401, status_401)
    app.register_error_handler(404, status_404)
    app.run(debug=True)