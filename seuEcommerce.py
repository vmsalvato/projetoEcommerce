from flask import Flask, make_response, Response
from markupsafe import escape
from flask import render_template
from flask import request
import mysql.connector
from flask_sqlalchemy import SQLAlchemy
from flask import redirect
from flask import url_for

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql://testeuser:bancoteste2@localhost:3306/seuecommerce"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

class Usuario(db.Model):
    id = db.Column('IDUSUARIO', db.Integer, primary_key=True)
    nome = db.Column('NOME', db.String(250))
    email = db.Column('EMAIL', db.String(60))
    cpf = db.Column('CPF', db.String(11))
    sexo = db.Column('SEXO', db.String(1))
    senha = db.Column('SENHA', db.String(60))

    def __init__(self, nome, email, cpf, sexo, senha):
        self.nome = nome
        self.email = email
        self.cpf = cpf
        self.sexo = sexo
        self.senha = senha

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/log/usuario")
def logusuario():
    return render_template("usuario.html", usuarios = Usuario.query.all(), title="Usuário")

@app.route("/usuario/criar", methods=["POST"])
def criaruser():
    usuario = Usuario(request.form.get("user"), request.form.get("email"), request.form.get("cpf"), request.form.get("sexo"), request.form.get("senha"))
    db.session.add(usuario)
    db.session.commit()
    return redirect(url_for("logusuario"))

@app.route("/usuario/detalhar/<int:id>")
def buscarusuario(id):
    usuario = Usuario.query.get(id)
    return usuario.nome

@app.route("/usuario/editar/<int:id>", methods=["GET","POST"])
def editarusuario(id):
    usuario = Usuario.query.get(id)
    if request.method == "POST":

        usuario.nome = request.form.get("user")
        usuario.email = request.form.get("email")
        usuario.cpf = request.form.get("cpf")
        usuario.sexo = request.form.get("sexo")
        usuario.senha = request.form.get("senha")

        db.session.add(usuario)
        db.session.commit()

        return redirect(url_for("logusuario"))
    
    return render_template("alterar.html", usuario = usuario, title="Usuário")

@app.route("/usuario/deletar/<int:id>")
def deletarusuario(id):
    usuario = Usuario.query.get(id)
    db.session.delete(usuario)
    db.session.commit()
    return redirect(url_for("logusuario"))

@app.route("/anuncio/novo")
def anuncio():
    return render_template("anuncio.html")

@app.route("/anuncio/pergunta")
def pergunta():
    return render_template("pergunta.html")

@app.route("/anuncio/favoritos")
def favoritos():
    return render_template("favoritos.html")

@app.route("/categoria/novo")
def categoria():
    return render_template("categoria.html")

@app.route("/relatorios/vendas")
def rel_vendas():
    return render_template("rel_vendas.html")

@app.route("/relatorios/compras")
def rel_compras():
    return render_template("rel_compras.html")

if __name__ == "seuEcommerce":
    with app.app_context():
        db.create_all()