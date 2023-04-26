from werkzeug.security import check_password_hash
from flask_login import UserMixin
import jwt
from time import time
import os

# Clase para el control de usuarios
class User(UserMixin):

    def __init__(self, id, email, password, name="") -> None:
        self.id = id
        self.email = email
        self.password = password
        self.name = name
        

    @classmethod
    def check_password(self, hashed_password, password):
        # Se checkea si la contraseña que se ingrese es la correcta comparandola con la hasheada
        return check_password_hash(hashed_password, password)
    
    def get_reset_token(self, expires=500):
        return jwt.encode({'reset_password': self.name, 'exp': time() + expires},
                          key='price_scaner_ppi_00', algorithm="HS256")

    @staticmethod
    def verify_reset_token(token, mysql):
        try:
            username = jwt.decode(token, key='price_scaner_ppi_00', algorithms=["HS256"])['reset_password']
            print(username)
        except Exception as e:
            print(e)
            return

        conexion = mysql.connect()
        cursor = conexion.cursor()

        cursor.execute("SELECT nombre FROM usuarios WHERE nombre = %s", (username))
        aux = cursor.fetchone()
        return aux