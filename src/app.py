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
from ofertasML import generar_ofertas
from modelos.Modelusuario import ModelUser
from modelos.entidades.usuario import User

# instanciación de la aplicación
app = Flask(__name__)

mysql = MySQL()

# variables de configuracion de la base de datos
app.config["MYSQL_DATABASE_HOST"] = 'localhost'
app.config["MYSQL_DATABASE_USER"] = 'root'
app.config["MYSQL_DATABASE_PASSWORD"] = 'holamundo'
app.config["MYSQL_DATABASE_DB"] = 'productos'

mysql.init_app(app)


# Configuracion de las variables para enviar y recibir mensajes
mail = Mail()  
app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'pricescaner00' + '@' + 'gmail.com'
app.config['MAIL_PASSWORD'] = 'nwlbvpz' + 'ijilqzxcg'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail.init_app(app)

# Instancia para capturar errores en el envio de emails
logger = logging.getLogger(__name__)


# Funcion 1 para enviar correos de forma asincronica
def _send_async_email(app, msg):
    """Envia el mail con el metodo send
    
    Captura el error de envio en caso de ocurrir. La funcion recibe como 
    parametros la instancia de la aplicacion y el mensaje. Usa un try 
    except para mandar enviar el correo de manera asincronica. 
    """

    with app.app_context():
        try:
            mail.send(msg)
        except SMTPException:
            logger.exception("Ocurrió un error al enviar el email")


# Funcion 2 para enviar correos de forma asincronica
def send_email(subject, sender, recipients, text_body, cc=None, bcc=None, html_body=None):
    """Crea la instancia del mensaje y lo envia
    
    Llama a la funcion _send_async_email y la ejecuta por
    otro hilo de procesamiento (se envia de forma asincronica). Esta funcion, recibe los diferentes
    parametros necesarios para enviar el correo de manera mas eficiente y posteriormente
    envia el mensaje.
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
    """Encontrar un usuario segun su id
    
    Busca y toma como parametro el id de un usuario en la base de datos y lo retorna
    """

    return ModelUser.get_by_id(mysql, id)


# Ruta para la pagina inicial
@app.route('/', methods = ["GET", "POST"])
def inicio():
    """Muestra la pestaña principal

    La funcion no toma ningun parametro, pero se encarga de mostrar por pantalla
    la pagina inicial de la aplicacion.
    """
    # Se retorna el html de la pagina de incio
    return render_template('index.html') 


# Ruta para la pagina del catalogo
@app.route('/catalogo-reg', methods = ["GET"])
@login_required
def catalogo():
    """Muestra los productos en oferta
    
    La funcion no toma ningun parametro, pero se encarga de hacer webscraping 
    a las tiendas y extrae los productos que estan en oferta. Posteriormente
    los guarda en la base de datos y luego los muestra en la aplicacion.
    """

    generar_ofertas()

    # Se genera una conexion a la base de datos y se extraen los productos recien guardados
    conexion = mysql.connect()
    cursor = conexion.cursor()
    cursor.execute("SELECT * FROM ofertas")
    ofertas = cursor.fetchall()
    conexion.commit()

    # Se retorna el html de la pagina de catalogo
    return render_template('catalogo_reg.html', ofertas = ofertas)

# Ruta para la pagina de home
@app.route('/home', methods = ["GET"])
@login_required
def home():
    """Muestra la pestaña home

    La funcion no toma ningun parametro, pero se encarga de mostrar por pantalla
    la pagina inicial de la aplicacion de un usuario registrado.
    """

    # Se retorna el html de la pagina de home
    return render_template('home.html')


# Ruta para la pagian de nosotros
@app.route('/nosotros', methods = ["GET"])
def nosotros():
    """Muestra la pestaña de nosotros

    La funcion no toma ningun parametro, pero se encarga de mostrar por pantalla
    la pagina de "Nosotros".
    """
    # Se retorna el html de la pagina de nosotros
    return render_template('nosotros.html')



# Ruta para la pagian de contactanos 
@app.route('/contactanos', methods = ["GET","POST"])
def contacto():
    """Envia email para contactarse con los admins
    
    La funcion no recibe parametros. Captura los datos del usuario y el 
    mensaje a enviar, luego mediante la funcion send_email envia el mensaje. 
    """

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

    # Se retorna el html de la pagina de contactanos
    return render_template("contactanos.html") 


# Ruta para el registro de usuarios
@app.route('/signup', methods= ["GET", "POST"])
def registro():
    """Registrar un nuevo usuario

    Se ingresan los datos requeridos (nombre, email, password)
    se revisa que el usuario sea valido (no se encuentre ya registrado)
    si el usuario es valido se guarda en la base de datos
    """

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

            # Se envia a logearse
            return redirect('/login') 
        else:

            # Se muesta un mensaje si el usuario es existente
            flash("Usuario existente, por favor registrese con otro email", "warning")

            return redirect('/signup')

    return render_template("signup.html")


# Ruta para el inicio de sesión de usuarios
@app.route('/login', methods= ["GET", "POST"])
def login():
    """Inicio de sesion de un usuario
    
    el usuario ingresa su nombre y contraseña
    se verifican con los registrados en la base de datos
    si son correctos se le da acceso a la aplicacion
    """

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
    """Cierre de sesion de un usuario
    
    Mediante la funcion logout_user el usuario finaliza su sesion
    """
    logout_user()
    return redirect('/')


# Ruta para enviar el correo de cambio de contraseña
@app.route("/restablecer-contrasena", methods= ["GET", "POST"])
def reset_request():
    """Enviar correo para cambiar el password de un usuario
    
    Para la funcion, el usuario ingresa su email si este concuerda con el registrado
    se envia un a su email un mensaje para cambiar su password
    """

    if request.method == "POST":

        # Se recibe el email del usuario
        email_recp = request.form['email_reset_password']

        conexion = mysql.connect()
        cursor = conexion.cursor()

        # Se compara con el email registrado
        cursor.execute("SELECT id, email, nombre FROM usuarios WHERE email = %s", (email_recp))
        aux = cursor.fetchone()

        # Se comprueba que el email ingresado exista
        if aux == None:
            flash("Usuario no encontrado...", "error")
            
        else:

            # Se extrae el usuario de la bd y se crea un token de seguridad
            user = User(aux[0], aux[1], None, aux[2])
            token = user.get_reset_token()
            print(token)
            print(user.email)

            # Se envia el email con el link a la pagina de cambio de contraseña
            send_email(subject = "[PRICESCANER] Restablecimiento de contraseña",
                    sender = ("PRICESCANER", "pricescaner@yahoo.com"),
                    recipients = [email_recp],
                    text_body = ".",
                    html_body = render_template("reset_email.html", user = user, token = token))

            flash("Solicitud de restablecimiento enviada. Revise su correo", "info")
            
    
    return render_template("reset_password.html")


# Ruta segura para cambiar la contraseña
@app.route('/restablecer-contrasena-verificado/<token>', methods=['GET', 'POST'])
def reset_verified(token):
    """Cambiar contraseña de un usuario
    
    Se verifica que el usuario ingresara al link enviado a su email
    luego el usuario ingresa su nuevo password y este es cambiado
    en la base de datos. 
    La funcion usa un try except para verificar el token de seguridad que se le 
    envia al correo. 
    """

    try:
        # Se verifica el token de seguridad enviado al email del usuario
        user = User.verify_reset_token(token, mysql)
        print(user[0])
    except:
        return "<p>El tiempo de uso de este link se ha vencido.</p>"

    # Se controlan posibles errores de autenticación
    if not user:
        print('usuario no encontrado')
        flash("Ocurrio un error. Intentelo nuevamente")
        return redirect('/restablecer-contrasena')

    if request.method == "POST":

        # Se recibe la nueva contraseña
        password = request.form['respassword']
        passwordsec = request.form['reppassword']

        # Se compureba que se haya ingresado bien la contraseña
        if password == passwordsec:
            conexion = mysql.connect()
            cursor = conexion.cursor()

            # Se cambia la contraseña vieja por la nueva
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
    """Busca el producto
    
    Despues de que el usuario ingresa un producto que desea encontrar, 
    esta funcion permite que se haga una busqueda por medio del 
    Web Scapping y finalmente se muestran los resultados.
    """

    if request.method == "POST":

        busqueda = request.form['busqueda'] # Se obtiene la busqueda que ingresa el usuario

        try:
            # se guarda el producto buscado en una base de datos haciendo web scraping
            main.guardar(busqueda)
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
    """Busca el producto de un usuario registrado
    
    Similar a la funcion anterior, sin embargo aqui se esta haciendo
    una busqueda con base al producto que el usuario desea usando los
    filtros en la pagina web. Estos incluyen nombre del producto, 
    rango de precios y si desea envio gratis o no
    """

    if request.method == "POST":
        
        # Se obtienen los datos del producto ingresado
        busqueda_reg = request.form['busquedareg']
        rango = [request.form['min-price'], request.form['max-price']]
        envio = request.form['envio']

        print(busqueda_reg, rango, envio)
        try:
            # se guarda el producto buscado en una base de datos haciendo web scraping
            main.guardar(busqueda_reg)
        except:
            pass

        aux = busqueda_reg.replace(" ", "") # Esta variable guarda el nombre de la tabla
        
        # Se genera una conexion a la base de datos y se extraen los productos recien guardados
        conexion = mysql.connect()
        cursor = conexion.cursor()

        # Se tienen en cuenta las variantes de busqueda para extraer la lista de productos de la bd
        if envio == "Si" and rango[0] != "" and rango[1] != "":
            cursor.execute("SELECT * FROM %s WHERE Precio > %s AND Precio < %s AND EnvGratis != '' ORDER BY Precio " 
                           % (aux, rango[0], rango[1]))
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
    """Guardar el correo electronico
    
    Permite hacer una conexion a la base de datos donde se verifica
    si el correo ingresado es existente o es nuevo. En caso de que sea 
    nuevo, se agrega el correo a la base de datos, si es un correo
    existente simplemente se genera la conexion a la base de datos
    """
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
    # Se retorna la direccion a la carpeta de archivos css
    return send_from_directory(os.path.join('templates/static/css'), archivo)


# Ruta para reconocer y usar las imagenes
@app.route('/static/images/<img>', methods = ["Get"])
def img_link(img):
    # Se retorna la direccion a la carpeta de las imagenes
    return send_from_directory(os.path.join('templates/static/images'), img)


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