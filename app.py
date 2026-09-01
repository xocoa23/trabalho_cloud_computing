"""
DeployLog - pagina de status de deploy.

O commit e a data do build sao gravados na imagem durante o build e lidos
como variaveis de ambiente. Sem banco de dados: a pagina reflete exatamente
a imagem que esta rodando no Azure.
"""

import os

from authlib.integrations.flask_client import OAuth
from flask import Flask, redirect, render_template, session, url_for

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "chave-insegura-para-desenvolvimento")

# Atras do balanceador do Azure o container recebe HTTP puro, entao o Flask
# precisa ser informado de que a conexao original do usuario era HTTPS.
if os.getenv("APP_ENV") == "producao":
    app.config["PREFERRED_URL_SCHEME"] = "https"

    from werkzeug.middleware.proxy_fix import ProxyFix
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

CLIENT_ID = os.getenv("GITHUB_CLIENT_ID", "")
CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET", "")
LOGIN_ATIVO = bool(CLIENT_ID and CLIENT_SECRET)

oauth = OAuth(app)
if LOGIN_ATIVO:
    oauth.register(
        name="github",
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        access_token_url="https://github.com/login/oauth/access_token",
        authorize_url="https://github.com/login/oauth/authorize",
        api_base_url="https://api.github.com/",
        client_kwargs={"scope": "read:user"},
    )


@app.route("/")
def index():
    return render_template(
        "index.html",
        commit=os.getenv("APP_COMMIT", "local"),
        build_time=os.getenv("APP_BUILD_TIME", "nao informado"),
        ambiente=os.getenv("APP_ENV", "desenvolvimento"),
        usuario=session.get("usuario"),
        login_ativo=LOGIN_ATIVO,
    )


@app.route("/entrar")
def entrar():
    return oauth.github.authorize_redirect(url_for("callback", _external=True))


@app.route("/callback")
def callback():
    oauth.github.authorize_access_token()
    perfil = oauth.github.get("user").json()
    # Sessao guardada em cookie assinado. Nada e persistido no servidor.
    session["usuario"] = {
        "login": perfil.get("login"),
        "avatar": perfil.get("avatar_url"),
    }
    return redirect(url_for("index"))


@app.route("/sair")
def sair():
    session.pop("usuario", None)
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
