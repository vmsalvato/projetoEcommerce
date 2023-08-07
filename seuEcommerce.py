from flask import Flask, make_response
from markupsafe import escape
from flask import render_template
from flask import request

app = Flask (__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/log/usuario")
def usuario():
    return render_template("usuario.html", title="Login Usuário")

@app.route("/log/loguser", methods=["POST"])
def logusuario():
    return request.form

@app.route("/log/anuncio")
def anuncio():
    return render_template("anuncio.html")

@app.route("/anuncio/pergunta")
def pergunta():
    return render_template("pergunta.html")

@app.route("/anuncio/favoritos")
def favoritos():
    return render_template("favoritos.html")

@app.route("/config/categoria")
def categoria():
    return render_template("categoria.html")

@app.route("/relatorios/vendas")
def rel_vendas():
    return render_template("rel_vendas.html")

@app.route("/relatorios/compras")
def rel_compras():
    return render_template("rel_compras.html")