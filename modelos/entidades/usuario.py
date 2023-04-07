from werkzeug.security import check_password_hash
from flask_login import UserMixin

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