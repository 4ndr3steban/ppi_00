from .entidades.usuario import User

# Clase para controlar los usuarios en la base de datos
class ModelUser():

    @classmethod
    def login(self, mysql, user):
        """ Se verifica si el usuario si existe en la base de datos"""

        try:

            # Se genera la conexión a la bd
            conexion = mysql.connect()
            cursor = conexion.cursor()

            # Se extrae la información de un usuario
            sql = f"""SELECT id, nombre, email, password FROM usuarios 
                    WHERE email = '{user.email}'"""
            cursor.execute(sql)
            row = cursor.fetchone()

            # Se verifica si el usuario existe
            if row != None:
                user = User(row[0],row[2], User.check_password(row[3], user.password), row[1])
                return user
            else:
                return None
        except Exception as ex:
            raise Exception(ex)

    @classmethod
    def get_by_id(self, mysql, id):
        """ Funcion para obtener la info de un usuario mediante su id"""

        try:

            # Se conecta con la base de datos
            conexion = mysql.connect()
            cursor = conexion.cursor()

            # Se selecciona un usuario
            sql = f"SELECT id, email, nombre FROM usuarios WHERE id = {id}"
            cursor.execute(sql)
            row = cursor.fetchone()

            # Se extrae su información
            if row != None:
                return User(row[0], row[1], None, row[2])
            else:
                return None
        except Exception as ex:
            raise Exception(ex)