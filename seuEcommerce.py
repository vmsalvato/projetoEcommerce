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
    senha = db.Column('SENHA', db.String(256))

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
    usuario_id = db.Column('usuario_id',db.Integer, db.ForeignKey("usuario.IDUSUARIO"))

    def __init__ (self, texto, anuncio_id, usuario_id):
        self.texto = texto
        self.anuncio_id = anuncio_id
        self.usuario_id = usuario_id

### TABELA FAVORITOS

class Favorito(db.Model):
    __tablename__ = "favorito"
    id = db.Column('favorito_id', db.Integer, primary_key=True)
    avaliacao = db.Column('avaliacao', db.String(150))
    comentario = db.Column('comentario', db.String(150))
    anuncio_id = db.Column('anuncio_id',db.Integer, db.ForeignKey("anuncio.anu_id"))
    usuario_id = db.Column('usuario_id',db.Integer, db.ForeignKey("usuario.IDUSUARIO"))

    def __init__ (self, avaliacao, comentario, anuncio_id, usuario_id):
        self.avaliacao = avaliacao
        self.comentario = comentario
        self.anuncio_id = anuncio_id
        self.usuario_id = usuario_id

### TABELA RESPOSTA

class Resposta(db.Model):
    __tablename__ = "resposta"
    id = db.Column('resposta_id', db.Integer, primary_key=True)
    texto = db.Column('texto_resposta', db.String(256))
    pergunta_resposta = db.Column('pergunta_resposta', db.String(256))
    usuario_id = db.Column('usuario_id',db.Integer, db.ForeignKey("usuario.IDUSUARIO"))


    def __init__ (self, texto, pergunta_resposta, usuario_id):
        self.texto = texto
        self.pergunta_resposta = pergunta_resposta
        self.usuario_id = usuario_id

### TABELA COMPRA

class Compra(db.Model):
    __tablename__ = "compra"
    id = db.Column('compra_id', db.Integer, primary_key=True)
    nome = db.Column('anuncio_nome', db.String(256))
    qtd = db.Column('anuncio_qtd', db.Integer)
    preco = db.Column('anuncio_preco', db.Float)
    usuario_id = db.Column('usuario_id',db.Integer, db.ForeignKey("usuario.IDUSUARIO"))


    def __init__(self, nome, qtd, preco, usuario_id):
        self.nome = nome
        self.qtd = qtd
        self.preco = preco
        self.usuario_id = usuario_id

### TABELA VENDA

class Venda(db.Model):
    __tablename__ = "venda"
    id = db.Column('venda_id', db.Integer, primary_key=True)
    nome = db.Column('anuncio_nome', db.String(256))
    qtd = db.Column('anuncio_qtd', db.Integer)
    preco = db.Column('anuncio_preco', db.Float)
    usuario_id = db.Column('usuario_id',db.Integer, db.ForeignKey("usuario.IDUSUARIO"))


    def __init__(self, nome, qtd, preco, usuario_id):
        self.nome = nome
        self.qtd = qtd
        self.preco = preco
        self.usuario_id = usuario_id

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
        senha = hashlib.sha256(str(request.form.get('senha')).encode("utf-8")).hexdigest() 

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
    
    return render_template("index.html", anuncios = Anuncio.query.all(), categorias = Categoria.query.all(), usuarios = Usuario.query.all())

### CRUD USUARIO
@app.route("/log/usuario")
def logusuario():
    return render_template("usuario.html", usuarios = Usuario.query.all(), title="Usuário")

@app.route("/usuario/criar", methods=["POST"])
def criaruser():
    hash = hashlib.sha256(str(request.form.get('senha')).encode("utf-8")).hexdigest()
    usuario = Usuario(request.form.get("user"), request.form.get("email"), request.form.get("cpf"), request.form.get("sexo"), hash)
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
        usuario.senha = hashlib.sha256(str(request.form.get('senha')).encode("utf-8")).hexdigest()

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
    return render_template('anuncio.html', anuncios = Anuncio.query.all(), categorias = Categoria.query.all(), usuarios = Usuario.query.all(), titulo="Anúncio")

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
    
    return render_template("alterar_anuncio.html", anuncio = anuncio, categorias = Categoria.query.all(), usuarios = Usuario.query.all(), title="Anúncio")


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
    return render_template('pergunta.html', perguntas = Pergunta.query.all(), anuncios = Anuncio.query.all(), usuarios = Usuario.query.all(), titulo='Pergunta')

@app.route("/pergunta/criar", methods=['POST'])
def criarpergunta():
    pergunta = Pergunta(request.form.get('texto'), request.form.get('anuncio_id'), request.form.get('usuario_id'))
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
        pergunta.usuario_id = request.form.get("usuario_id")

        db.session.add(pergunta)
        db.session.commit()

        return redirect(url_for("pergunta"))
    
    return render_template("alterar_pergunta.html", pergunta = pergunta, anuncios = Anuncio.query.all(), usuarios = Usuario.query.all(), title="Pergunta")

### CRUD RESPOSTA 
@app.route("/anuncio/resposta")
@login_required
def resposta():
    return render_template('responder_pergunta.html', perguntas = Pergunta.query.all(), respostas = Resposta.query.all(), anuncios = Anuncio.query.all(), usuarios = Usuario.query.all())

@app.route("/resposta/criar", methods=['POST'])
def criarresposta():
    resposta = Resposta(request.form.get('pergunta_anuncio'), request.form.get('texto_resposta'), request.form.get('usuario_id'))
    db.session.add(resposta)
    db.session.commit()
    return redirect(url_for('resposta'))

@app.route("/resposta/deletar/<int:id>")
def deletaresposta(id):
    resposta = Resposta.query.get(id)
    db.session.delete(resposta)
    db.session.commit()
    return redirect(url_for("resposta"))

@app.route("/resposta/editar/<int:id>", methods=["GET","POST"])
def editarresposta(id):
    resposta = Resposta.query.get(id)
    if request.method == "POST":

        resposta.pergunta_anuncio = request.form.get("pergunta_anuncio")
        resposta.pergunta_resposta = request.form.get("texto_resposta")
        resposta.usuario_id = request.form.get("usuario_id")

        db.session.add(resposta)
        db.session.commit()

        return redirect(url_for("resposta"))
    
    return render_template("alterar_responder_pergunta.html", resposta = resposta, usuarios = Usuario.query.all(), anuncios = Anuncio.query.all(), perguntas = Pergunta.query.all(), title="Resposta")

### CRUD FAVORITOS

@app.route("/anuncio/favoritos")
@login_required
def favoritos():
    return render_template("favoritos.html", usuarios = Usuario.query.all(), favoritos = Favorito.query.all(), anuncios = Anuncio.query.all(),  titulo='Favoritos')

@app.route("/favorito/criar", methods=['POST'])
def criarfavorito():
    favorito = Favorito(request.form.get('avaliacao'), request.form.get('comentario'), request.form.get('anuncio_id'), request.form.get('usuario_id'))
    db.session.add(favorito)
    db.session.commit()
    return redirect(url_for('favoritos'))

@app.route("/favorito/deletar/<int:id>")
def deletarfavorito(id):
    favorito = Favorito.query.get(id)
    db.session.delete(favorito)
    db.session.commit()
    return redirect(url_for("favoritos"))

@app.route("/favorito/editar/<int:id>", methods=["GET","POST"])
def editarfavorito(id):
    favorito = Favorito.query.get(id)
    if request.method == "POST":

        favorito.avaliacao = request.form.get("avaliacao")
        favorito.comentario = request.form.get("comentario")
        favorito.anuncio_id = request.form.get("anuncio_id")
        favorito.usuario_id = request.form.get("usuario_id")

        db.session.add(favorito)
        db.session.commit()

        return redirect(url_for("favoritos"))
    
    return render_template("alterar_favorito.html", favorito = favorito, usuarios = Usuario.query.all(), anuncios = Anuncio.query.all(), title="Favorito")

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
    return render_template("rel_vendas.html", vendas = Venda.query.all(), usuarios = Usuario.query.all(), title="Vendas")

@app.route("/anuncio/venda", methods=["GET","POST"])
def venda_anuncio():
    venda = Venda(request.form.get('anuncio_nome'), request.form.get('anuncio_qtd'), request.form.get('anuncio_preco'), request.form.get('usu'))
    db.session.add(venda)
    db.session.commit()
    return redirect(url_for('rel_vendas'))    

### RELATORIO COMPRAS

@app.route("/relatorios/compras")
@login_required
def rel_compras():
    return render_template("rel_compras.html" , compras = Compra.query.all(), usuarios = Usuario.query.all(), title='Compras')

@app.route("/anuncio/compra", methods=["GET","POST"])
def compra_anuncio():
    compra = Compra(request.form.get('anuncio_nome'), request.form.get('anuncio_qtd'), request.form.get('anuncio_preco'), request.form.get('usu'))
    db.session.add(compra)
    db.session.commit()
    return redirect(url_for('rel_compras'))

if __name__ == "seuEcommerce":
    with app.app_context():
        db.create_all()