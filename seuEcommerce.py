from flask import Flask, make_response, render_template_string, Response
from markupsafe import escape
from flask import render_template
from flask import request
import mysql.connector
from flask_sqlalchemy import SQLAlchemy
from flask import redirect
from flask import url_for
from flask_login import (current_user, LoginManager,
                             login_user, logout_user,
                             login_required)
import hashlib
#from crypt import methods

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql://testeuser:bancoteste2@localhost:3306/seuecommerce"
#app.config["SQLALCHEMY_DATABASE_URI"] = "mysql://jonasmartins2:bancoteste2@jonasmartins2.mysql.pythonanywhere-services.com:3306/jonasmartins2$seuecommerce"

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# LOGIN

app.secret_key = 'alegrefeliz'
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

### TABELA USUARIOS

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
    
    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)

### TABELA CATEGORIAS

class Categoria(db.Model):
    __tablename__ = "categoria"
    id = db.Column('cat_id', db.Integer, primary_key=True)
    nome = db.Column('cat_nome', db.String(256))
    desc = db.Column('cat_desc', db.String(256))

    def __init__ (self, nome, desc):
        self.nome = nome
        self.desc = desc

### TABELA PERGUNTAS

class Pergunta(db.Model):
    __tablename__ = "pergunta"
    id = db.Column('pergunta_id', db.Integer, primary_key=True)
    texto = db.Column('texto_pergunta', db.String(256))
    anuncio_id = db.Column('anuncio_id',db.Integer, db.ForeignKey("anuncio.anu_id"))

    def __init__ (self, texto, anuncio_id):
        self.texto = texto
        self.anuncio_id = anuncio_id

### RESPOSTA PERGUNTAS

class Resposta(db.Model):
    __tablename__ = "resposta"
    id = db.Column('resposta_id', db.Integer, primary_key=True)
    texto = db.Column('texto_resposta', db.String(256))
    pergunta_resposta = db.Column('pergunta_resposta', db.String(256))

    def __init__ (self, texto, pergunta_resposta):
        self.texto = texto
        self.pergunta_resposta = pergunta_resposta

### TABELA ANUNCIO

class Anuncio(db.Model):
    __tablename__ = "anuncio"
    id = db.Column('anu_id', db.Integer, primary_key=True)
    nome = db.Column('anu_nome', db.String(256))
    desc = db.Column('anu_desc', db.String(256))
    qtd = db.Column('anu_qtd', db.Integer)
    imagem = db.Column(db.String(140))
    preco = db.Column('anu_preco', db.Float)
    cat_id = db.Column('cat_id',db.Integer, db.ForeignKey("categoria.cat_id"))
    usu_id = db.Column('usu_id',db.Integer, db.ForeignKey("usuario.IDUSUARIO"))


    def __init__(self, nome, desc, qtd, imagem, preco, cat_id, usu_id):
        self.nome = nome
        self.desc = desc
        self.qtd = qtd
        self.imagem = imagem
        self.preco = preco
        self.cat_id = cat_id
        self.usu_id = usu_id

### TRATAMENTO ERRO

@app.errorhandler(404)
def paginanaoencontrada(error):
    return render_template('erro.html')

#ID LOGIN
@login_manager.user_loader
def load_user(id):
    return Usuario.query.get(id)

#ROTA LOGIN
@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        email = str(request.form.get('email')).encode("utf-8")
        senha = request.form.get("senha")
        #senha = hashlib.sha512(str(request.form.get('senha')).encode("utf-8")).hexdigest()

        usuario = Usuario.query.filter_by(email=email, senha=senha).first()

        if usuario:
            login_user(usuario)
            return redirect(url_for('index'))
        else:
            return redirect(url_for('login'))
    return render_template('login.html')

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("index"))

### INDEX 
@app.route("/")
@login_required
def index():
    return render_template("index.html")

### CRUD USUARIO
@app.route("/log/usuario")
def logusuario():
    return render_template("usuario.html", usuarios = Usuario.query.all(), title="Usuário")

@app.route("/usuario/criar", methods=["POST"])
def criaruser():
    #hash = hashlib.sha512(str(request.form.get('senha')).encode("utf-8")).hexdigest()
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
        usuario.senha = request.form.get("senha")#hashlib.sha512(str(request.form.get('senha')).encode("utf-8")).hexdigest()

        db.session.add(usuario)
        db.session.commit()

        return redirect(url_for("logusuario"))
    
    return render_template("alterar_usuario.html", usuario = usuario, title="Usuário")

@app.route("/usuario/deletar/<int:id>")
def deletarusuario(id):
    usuario = Usuario.query.get(id)
    db.session.delete(usuario)
    db.session.commit()
    return redirect(url_for("logusuario"))


### CRUD ANUNCIO
@app.route("/cad/anuncio")
@login_required
def anuncio():
    return render_template('anuncio.html', anuncios = Anuncio.query.all(), categorias = Categoria.query.all(), usuarios = Usuario.query.all(), titulo="Anuncio")

@app.route("/anuncio/criar", methods=['POST'])
def criaranuncio():
    anuncio = Anuncio(request.form.get('nome'), request.form.get('desc'),request.form.get('qtd'), request.form.get('imagem'), request.form.get('preco'), request.form.get('cat'), request.form.get('usu'))

    db.session.add(anuncio)
    db.session.commit()
    return redirect(url_for('anuncio'))

@app.route("/anuncio/editar/<int:id>", methods=["GET","POST"])
def editaranuncio(id):
    anuncio = Anuncio.query.get(id)
    if request.method == "POST":

        anuncio.nome = request.form.get("nome")
        anuncio.desc = request.form.get("desc")
        anuncio.qtd = request.form.get("qtd")
        anuncio.qtd = request.form.get("imagem")
        anuncio.preco = request.form.get("preco")
        anuncio.cat_id = request.form.get("cat")
        anuncio.usu_id = request.form.get("usu")

        db.session.add(anuncio)
        db.session.commit()

        return redirect(url_for("anuncio"))
    
    return render_template("alterar_anuncio.html", anuncio = anuncio, title="Anúncio")


@app.route("/anuncio/deletar/<int:id>")
def deletaranuncio(id):
    anuncio = Anuncio.query.get(id)
    db.session.delete(anuncio)
    db.session.commit()
    return redirect(url_for("anuncio"))

### CRUD PERGUNTA 
@app.route("/anuncio/pergunta")
@login_required
def pergunta():
    return render_template('pergunta.html', perguntas = Pergunta.query.all(), anuncios = Anuncio.query.all(), titulo='Pergunta')

@app.route("/pergunta/criar", methods=['POST'])
def criarpergunta():
    pergunta = Pergunta(request.form.get('texto'), request.form.get('anuncio_id'))
    db.session.add(pergunta)
    db.session.commit()
    return redirect(url_for('pergunta'))

@app.route("/pergunta/deletar/<int:id>")
def deletarpergunta(id):
    pergunta = Pergunta.query.get(id)
    db.session.delete(pergunta)
    db.session.commit()
    return redirect(url_for("pergunta"))

@app.route("/pergunta/editar/<int:id>", methods=["GET","POST"])
def editarpergunta(id):
    pergunta = Pergunta.query.get(id)

    if request.method == "POST":

        pergunta.texto = request.form.get("texto")
        pergunta.anuncio_id = request.form.get("anuncio_id")

        db.session.add(pergunta)
        db.session.commit()

        return redirect(url_for("pergunta"))
    
    return render_template("alterar_pergunta.html", pergunta = pergunta, title="Pergunta")

### CRUD RESPOSTA 
@app.route("/anuncio/resposta")
@login_required
def resposta():
    return render_template('responder_pergunta.html', perguntas = Pergunta.query.all(), respostas = Resposta.query.all(), anuncios = Anuncio.query.all())

@app.route("/resposta/criar", methods=['POST'])
def criarresposta():
    resposta = Resposta(request.form.get('pergunta_anuncio'), request.form.get('texto_resposta'))
    db.session.add(resposta)
    db.session.commit()
    return redirect(url_for('resposta'))

@app.route("/resposta/deletar/<int:id>")
def deletaresposta(id):
    resposta = Resposta.query.get(id)
    db.session.delete(resposta)
    db.session.commit()
    return redirect(url_for("resposta"))

### FAVORITOS

@app.route("/anuncio/favoritos")
def favoritos():
    return render_template("favoritos.html")

### CRUD CATEGORIA

@app.route("/config/categoria")
@login_required
def categoria():
    return render_template('categoria.html', categorias = Categoria.query.all(), titulo='Categoria')

@app.route("/categoria/criar", methods=['POST'])
def criarcategoria():
    categoria = Categoria(request.form.get('nome'), request.form.get('desc'))
    db.session.add(categoria)
    db.session.commit()
    return redirect(url_for('categoria'))

@app.route("/categoria/deletar/<int:id>")
def deletarcategoria(id):
    categoria = Categoria.query.get(id)
    db.session.delete(categoria)
    db.session.commit()
    return redirect(url_for("categoria"))

@app.route("/categoria/editar/<int:id>", methods=["GET","POST"])
def editarcategoria(id):
    categoria = Categoria.query.get(id)
    if request.method == "POST":

        categoria.nome = request.form.get("nome")
        categoria.desc = request.form.get("desc")

        db.session.add(categoria)
        db.session.commit()

        return redirect(url_for("categoria"))
    
    return render_template("alterar_categoria.html", categoria = categoria, title="Categoria")

### RELATORIO VENDAS

@app.route("/relatorios/vendas")
@login_required
def rel_vendas():
    return render_template("rel_vendas.html")

### RELATORIO COMPRAS

@app.route("/relatorios/compras")
@login_required
def rel_compras():
    return render_template("rel_compras.html")

if __name__ == "seuEcommerce":
    with app.app_context():
        db.create_all()