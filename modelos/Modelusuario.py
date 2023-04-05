from .entidades.usuario import User

class ModelUser():

    @classmethod
    def login(self, mysql, user):
        try:
            conexion = mysql.connect()
            cursor = conexion.cursor()
            sql = f"""SELECT id, nombre, email, password FROM usuarios 
                    WHERE email = '{user.email}'"""
            cursor.execute(sql)
            row = cursor.fetchone()
            if row != None:
                user = User(row[0],row[2], User.check_password(row[3], user.password), row[1])
                return user
            else:
                return None
        except Exception as ex:
            raise Exception(ex)

    @classmethod
    def get_by_id(self, mysql, id):
        try:
            conexion = mysql.connect()
            cursor = conexion.cursor()
            sql = f"SELECT id, email, nombre FROM usuarios WHERE id = {id}"
            cursor.execute(sql)
            row = cursor.fetchone()
            if row != None:
                return User(row[0], row[1], None, row[2])
            else:
                return None
        except Exception as ex:
            raise Exception(ex)