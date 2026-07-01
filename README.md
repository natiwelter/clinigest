# Clinigest

Clinigest é uma aplicação web desenvolvida em Flask para auxiliar na organização de uma clínica psicológica. O sistema permite cadastrar pacientes, agendar consultas, registrar sessões/anotações e acompanhar lançamentos financeiros.

## Funcionalidades

- Login para acesso ao sistema
- Dashboard com resumo geral
- Cadastro e edição de pacientes
- Controle de prioridade dos pacientes
- Agendamento de consultas
- Atendimento de consultas com registro de observações
- Histórico de sessões realizadas
- Anotações por paciente
- Controle financeiro de entradas e saídas
- Calendário de consultas
- Relatório individual por paciente

## Tecnologias utilizadas

- Python
- Flask
- Flask-SQLAlchemy
- SQLite
- HTML
- CSS
- JavaScript

## Como executar o projeto localmente

1. Clone o repositório:

```bash
git clone https://github.com/natiwelter/clinigest.git
```

2. Acesse a pasta do projeto:

```bash
cd clinigest
```

3. Crie um ambiente virtual:

```bash
python -m venv .venv
```

4. Ative o ambiente virtual:

No Windows:

```bash
.venv\Scripts\activate
```

No Linux/Mac:

```bash
source .venv/bin/activate
```

5. Instale as dependências:

```bash
pip install -r requirements.txt
```

6. Execute a aplicação:

```bash
python app.py
```

7. Acesse no navegador:

```text
http://127.0.0.1:5000
```

## Acesso ao sistema

Senha de acesso para demonstração:

```text
terapia123
```

## Página de apresentação

A página de informações do projeto pode ser publicada pelo GitHub Pages na pasta `docs`.

Link esperado após ativar o GitHub Pages:

```text
https://natiwelter.github.io/clinigest/
```

## Observação sobre publicação

O GitHub Pages hospeda apenas páginas estáticas. Por isso, a aplicação Flask não roda diretamente nele. O GitHub Pages foi utilizado para publicar a página de apresentação do projeto, contendo informações, tecnologias utilizadas, instruções de execução e link para o repositório.

## Autoria

Projeto desenvolvido por Natalia Welter para apresentação final de projeto acadêmico.
