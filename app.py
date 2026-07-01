from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from functools import wraps

app = Flask(__name__, instance_relative_config=True)

app.config['SECRET_KEY'] = 'troque-por-uma-chave-segura'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///clinigest.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ------------------ LOGIN ------------------
CLINICA_PASSWORD = "terapia123"  

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("logado"):
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        senha = request.form.get("senha")
        if senha == CLINICA_PASSWORD:
            session["logado"] = True
            return redirect(url_for("home"))
        else:
            flash("Senha incorreta!")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

# ------------------ MODELOS ------------------
class Paciente(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(120), nullable=False)
    telefone = db.Column(db.String(20))
    email = db.Column(db.String(120))
    prioridade = db.Column(db.Integer, default=0)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)
    observacoes = db.Column(db.Text)

class Consulta(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    paciente_id = db.Column(db.Integer, db.ForeignKey('paciente.id'))
    paciente = db.relationship('Paciente', backref='consultas')

    data = db.Column(db.Date)
    hora = db.Column(db.Time)
    status = db.Column(db.String(20))

    observacao = db.Column(db.Text)  # 👈 NOVO
    

class LancamentoFinanceiro(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    consulta_id = db.Column(db.Integer, db.ForeignKey('consulta.id'))
    consulta = db.relationship('Consulta', backref='financeiro')

    tipo = db.Column(db.String(10), nullable=False)
    valor = db.Column(db.Float, nullable=False)
    descricao = db.Column(db.String(255))
    data = db.Column(db.Date)

# ------------------ ROTAS ------------------
@app.route("/")
@login_required
def home():
    total_pacientes = Paciente.query.count()

    consultas_hoje = Consulta.query.filter(
        Consulta.data == datetime.today().date()
    ).count()

    lancamentos = LancamentoFinanceiro.query.all()

    entradas = sum(l.valor for l in lancamentos if l.tipo == "entrada")
    saidas = sum(l.valor for l in lancamentos if l.tipo == "saida")
    saldo = entradas - saidas

    return render_template(
        "dashboard.html",
        total_pacientes=total_pacientes,
        consultas_hoje=consultas_hoje,
        entradas=entradas,
        saldo=saldo
    )

@app.route("/pacientes", methods=["GET", "POST"])
@login_required
def pacientes():
    if request.method == "POST":
        novo = Paciente(
            nome=request.form.get("nome"),
            telefone=request.form.get("telefone"),
            email=request.form.get("email"),
            prioridade=int(request.form.get("prioridade") or 0)
        )
        db.session.add(novo)
        db.session.commit()
        flash("Paciente cadastrado com sucesso!")
        return redirect(url_for("pacientes"))

    lista = Paciente.query.order_by(Paciente.prioridade.desc()).all()
    return render_template("pacientes.html", pacientes=lista)

@app.route("/pacientes/editar/<int:id>", methods=["GET", "POST"])
@login_required
def editar_paciente(id):
    paciente = Paciente.query.get_or_404(id)

    if request.method == "POST":
        paciente.nome = request.form.get("nome")
        paciente.telefone = request.form.get("telefone")
        paciente.email = request.form.get("email")
        paciente.prioridade = int(request.form.get("prioridade") or 0)

        db.session.commit()
        flash("Paciente atualizado com sucesso!")
        return redirect(url_for("pacientes"))

    return render_template("editar_paciente.html", paciente=paciente)

@app.route("/pacientes/relatorio/<int:id>")
@login_required
def relatorio_paciente(id):
    paciente = Paciente.query.get_or_404(id)

    consultas = Consulta.query.filter_by(paciente_id=id).all()

    lancamentos = []
    total_gasto = 0

    for c in consultas:
        for f in c.financeiro:
            lancamentos.append(f)
            if f.tipo == "entrada":
                total_gasto += f.valor

    return render_template(
        "relatorio_paciente.html",
        paciente=paciente,
        consultas=consultas,
        lancamentos=lancamentos,
        total_gasto=total_gasto
    )

@app.route("/agenda", methods=["GET", "POST"])
@login_required
def agenda():
    if request.method == "POST":
        nova = Consulta(
            paciente_id=int(request.form.get("paciente_id")),
            data=datetime.strptime(request.form.get("data"), "%Y-%m-%d").date(),
            hora=datetime.strptime(request.form.get("hora"), "%H:%M").time(),
            status="agendada"
        )
        db.session.add(nova)
        db.session.commit()

        return redirect(url_for("agenda"))

    consultas = Consulta.query.order_by(Consulta.data).all()

    return render_template("agenda.html",
        consultas=consultas,
        pacientes=Paciente.query.all()
    )
    
@app.route("/sessoes")
@login_required
def sessoes():
    consultas = Consulta.query.filter_by(status="realizada")\
        .order_by(Consulta.data.desc(), Consulta.hora.desc())\
        .all()

    return render_template("sessoes.html", consultas=consultas)

@app.route("/consulta/atender/<int:id>", methods=["GET", "POST"])
@login_required
def atender_consulta(id):
    consulta = Consulta.query.get_or_404(id)

    if request.method == "POST":
        consulta.observacao = request.form.get("observacao")

        acao = request.form.get("acao")

        if acao == "concluir":
            consulta.status = "realizada"
            flash("Sessão finalizada com sucesso!")
            db.session.commit()
            return redirect(url_for("agenda"))

        else:
            consulta.status = "em_atendimento"
            db.session.commit()
            flash("Anotações salvas!")

    # histórico do paciente
    historico = Consulta.query.filter(
        Consulta.paciente_id == consulta.paciente_id,
        Consulta.id != consulta.id,
        Consulta.status == "realizada"
    ).order_by(Consulta.data.desc()).all()

    return render_template(
        "atender_consulta.html",
        consulta=consulta,
        historico=historico
    )
    
@app.route("/agenda/editar/<int:id>", methods=["GET", "POST"])
@login_required
def editar_consulta_agenda(id):
    consulta = Consulta.query.get_or_404(id)

    if request.method == "POST":
        consulta.data = datetime.strptime(request.form.get("data"), "%Y-%m-%d").date()
        consulta.hora = datetime.strptime(request.form.get("hora"), "%H:%M").time()
        consulta.status = request.form.get("status")

        consulta.observacao = request.form.get("observacao")

        # 👇 SE ESCREVEU RELATÓRIO, MARCA COMO REALIZADA
        if consulta.observacao:
            consulta.status = "realizada"

        db.session.commit()
    return redirect(url_for("agenda"))

    return render_template("editar_consulta.html", consulta=consulta)

@app.route("/agenda/apagar/<int:id>")
@login_required
def apagar_consulta(id):
    consulta = Consulta.query.get_or_404(id)
    db.session.delete(consulta)
    db.session.commit()
    return redirect(url_for("agenda"))

# ------------------ ANOTAÇÕES ------------------
@app.route("/anotacoes")
@login_required
def anotacoes():
    pacientes = Paciente.query.all()
    return render_template("anotacoes.html", pacientes=pacientes)

@app.route("/anotacoes/<int:id>")
@login_required
def anotacoes_paciente(id):
    paciente = Paciente.query.get_or_404(id)

    consultas = Consulta.query.filter_by(paciente_id=id)\
        .order_by(Consulta.data.desc(), Consulta.hora.desc())\
        .all()

    return render_template(
        "anotacoes_paciente.html",
        paciente=paciente,
        consultas=consultas
    )

# ------------------ FINANCEIRO ------------------
@app.route("/financeiro")
@login_required
def financeiro():
    lancamentos = LancamentoFinanceiro.query.order_by(
        LancamentoFinanceiro.data.desc()
    ).all()

    entradas = sum(l.valor for l in lancamentos if l.tipo == "entrada")
    saidas = sum(l.valor for l in lancamentos if l.tipo == "saida")
    saldo = entradas - saidas

    return render_template(
        "financeiro.html",
        lancamentos=lancamentos,
        entradas=entradas,
        saidas=saidas,
        saldo=saldo
    )
    
@app.route("/financeiro/novo", methods=["POST"])
@login_required
def novo_lancamento():
    tipo = request.form.get("tipo")
    valor = float(request.form.get("valor"))
    descricao = request.form.get("descricao")

    lancamento = LancamentoFinanceiro(
        tipo=tipo,
        valor=valor,
        descricao=descricao,
        data=datetime.utcnow()
    )

    db.session.add(lancamento)
    db.session.commit()

    return redirect(url_for("financeiro"))

@app.route("/financeiro/lancar/<int:consulta_id>", methods=["POST"])
@login_required
def lancar_pagamento(consulta_id):
    consulta = Consulta.query.get_or_404(consulta_id)

    valor = float(request.form.get("valor"))
    if consulta.financeiro:
        flash("Essa consulta já possui pagamento!")
        return redirect(url_for("agenda"))
    lancamento = LancamentoFinanceiro(
        consulta_id=consulta.id,
        tipo="entrada",
        valor=valor,
        descricao=f"Consulta - {consulta.paciente.nome}",
        data=datetime.utcnow()
    )

    db.session.add(lancamento)
    db.session.commit()

    flash("Pagamento lançado com sucesso!")

    return redirect(url_for("agenda"))

# ------------------ RELATORIOS ------------------

@app.route("/relatorios")
@login_required
def relatorios():
    return "<h2>Relatórios em construção</h2>"

# ------------------ CALENDÁRIO ------------------
@app.route("/calendario")
@login_required
def calendario():
    consultas = Consulta.query.filter(
        Consulta.status != "realizada"
    ).all()

    eventos = []

    for c in consultas:
        # 🚨 evita erro se data/hora estiver vazio
        if c.data and c.hora:
            eventos.append({
                "title": c.paciente.nome,
                "start": f"{c.data.strftime('%Y-%m-%d')}T{c.hora.strftime('%H:%M:%S')}",
                "url": f"/consulta/atender/{c.id}"
            })

    print(eventos)  # 👈 DEBUG

    return render_template("calendario.html", eventos=eventos)

# ------------------ MAIN ------------------
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
    
