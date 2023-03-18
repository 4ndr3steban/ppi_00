from flask import Flask
from flask import render_template


app = Flask(__name__)


@app.route('/')
def inicio():
    return render_template('index.html')

@app.route('/catalogo')
def catalogo():
    return render_template('catalogo.html')

@app.route('/nosotros')
def nosotros():
    return render_template('nosotros.html')




