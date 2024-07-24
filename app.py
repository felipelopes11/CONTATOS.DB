from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
import smtplib
from email.mime.text import MIMEText

app = Flask(__name__)
app.secret_key = 'chave_secreta'


def conectar_banco_dados():
    conn = sqlite3.connect('contatos.db')
    cursor = conn.cursor()
    return conn, cursor


def criar_tabela_contatos():
    conn, cursor = conectar_banco_dados()
    cursor.execute('''CREATE TABLE IF NOT EXISTS contatos
                      (id INTEGER PRIMARY KEY AUTOINCREMENT,
                       nome TEXT,
                       telefone TEXT,
                       empresa TEXT,
                       email TEXT)''')
    conn.commit()
    conn.close()
    


def obter_contatos():
    conn, cursor = conectar_banco_dados()
    cursor.execute('SELECT * FROM contatos')
    contatos = cursor.fetchall()
    conn.close()

    contatos_list = []
    for contato in contatos:
        contato_dict = {
            'id': contato[0],
            'nome': contato[1],
            'telefone': contato[2],
            'empresa': contato[3],
            'email': contato[4]
        }
        contatos_list.append(contato_dict)

    return contatos_list



def obter_contato_por_id(id):
    conn, cursor = conectar_banco_dados()
    cursor.execute('SELECT * FROM contatos WHERE id = ?', (id,))
    contato = cursor.fetchone()
    conn.close()

    if contato is not None:
        contato_dict = {
            'id': contato[0],
            'nome': contato[1],
            'telefone': contato[2],
            'empresa': contato[3],
            'email': contato[4]
        }
        return contato_dict
    else:
        return None


def inserir_contato(nome, telefone, empresa, email):
    conn, cursor = conectar_banco_dados()
    cursor.execute('INSERT INTO contatos (nome, telefone, empresa, email) VALUES (?, ?, ?, ?)',
                   (nome, telefone, empresa, email))
    conn.commit()
    conn.close()


def atualizar_contato(id, nome, telefone, empresa, email):
    conn, cursor = conectar_banco_dados()
    cursor.execute('UPDATE contatos SET nome = ?, telefone = ?, empresa = ?, email = ? WHERE id = ?',
                   (nome, telefone, empresa, email, id))
    conn.commit()
    conn.close()


def excluir_contato(id):
    conn, cursor = conectar_banco_dados()
    cursor.execute('DELETE FROM contatos WHERE id = ?', (id,))
    conn.commit()
    conn.close()


def enviar_email(destinatario, mensagem):
    # Configurações do servidor de e-mail
    host = 'smtp.gmail.com'  # Insira o endereço do servidor SMTP
    port = 587  # Insira a porta do servidor SMTP
    username = 'agendaproject.system@gmail.com'  # Insira o seu e-mail de envio
    password = 'priqoxlayhashbyl'  # Insira a senha do seu e-mail de envio

    # Crie um objeto MIMEText com a mensagem
    msg = MIMEText(mensagem)

    # Configuração dos cabeçalhos do e-mail
    msg['Subject'] = 'Contato Cadastrado'
    msg['From'] = username
    msg['To'] = destinatario

    try:
        # Estabeleça a conexão com o servidor SMTP
        server = smtplib.SMTP(host, port)

        # Inicie a conexão segura (TLS)
        server.starttls()

        # Faça login no servidor SMTP
        server.login(username, password)

        # Envie o e-mail
        server.send_message(msg)

        # Encerre a conexão com o servidor SMTP
        server.quit()

        flash('E-mail enviado com sucesso!', 'success')
    except Exception as e:
        flash(f'Erro ao enviar e-mail: {str(e)}', 'danger')


@app.route('/enviar-email', methods=['POST'])
def enviar_email_route():
    destinatario = request.form['emailContato']  # Obtém o e-mail do destinatário do formulário
    mensagem = request.form['mensagem']  # Obtém a mensagem do formulário

    enviar_email(destinatario, mensagem)

    return redirect(url_for('agenda_contatos'))


@app.route('/')
def agenda_contatos():
    contatos = obter_contatos()
    return render_template('contatos.html', contatos=contatos)


@app.route('/adicionar-contato', methods=['GET', 'POST'])
def adicionar_contato():
    if request.method == 'POST':
        nome = request.form['nome']
        telefone = request.form['telefone']
        empresa = request.form['empresa']
        email = request.form['email']

        inserir_contato(nome, telefone, empresa, email)

        flash('Contato adicionado com sucesso!', 'success')
        return redirect(url_for('agenda_contatos'))
    else:
        return render_template('adicionar_contato.html')


@app.route('/editar-contato/<int:id>', methods=['GET', 'POST'])
def editar_contato(id):
    contato = obter_contato_por_id(id)

    if contato is None:
        flash('Contato não encontrado.', 'danger')
        return redirect(url_for('agenda_contatos'))

    if request.method == 'POST':
        nome = request.form['nome']
        telefone = request.form['telefone']
        empresa = request.form['empresa']
        email = request.form['email']

        atualizar_contato(id, nome, telefone, empresa, email)

        flash('Contato atualizado com sucesso!', 'success')
        return redirect(url_for('agenda_contatos'))
    else:
        return render_template('editar_contato.html', contato=contato)


@app.route('/excluir-contato/<int:id>', methods=['GET', 'POST'])
def excluir_contato_route(id):
    if request.method == 'POST':
        excluir_contato(id)
        flash('Contato excluído com sucesso!', 'success')
        return redirect(url_for('agenda_contatos'))
    else:
        contato = obter_contato_por_id(id)
        if contato is None:
            flash('Contato não encontrado.', 'danger')
            return redirect(url_for('agenda_contatos'))
        return render_template('excluir_contato.html', contato=contato)



@app.route('/enviar-mensagem/<int:id>', methods=['GET', 'POST'])
def enviar_mensagem(id):
    contato = obter_contato_por_id(id)

    if contato is None:
        flash('Contato não encontrado.', 'danger')
        return redirect(url_for('agenda_contatos'))

    if request.method == 'POST':
        destinatario = contato['email']
        mensagem = request.form['mensagem']

        enviar_email(destinatario, mensagem)

        flash('E-mail enviado com sucesso!', 'success')
        return redirect(url_for('agenda_contatos'))
    else:
        return render_template('enviar_mensagem.html', contato=contato)


if __name__ == '__main__':
    criar_tabela_contatos()
    app.run(debug=True)
