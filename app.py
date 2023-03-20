from flask import Flask, send_from_directory
from flask import render_template
import os

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

@app.route('/contactanos')
def contactanos():
    return render_template('contactanos.html')

@app.route('/css/<archivo>')
def css_link(archivo):
    return send_from_directory(os.path.join('templates/css'), archivo)

@app.route('/images/<img>')
def img_link(img):
    return send_from_directory(os.path.join('templates/images'), img)



