# DeployLog

Trabalho da disciplina de Cloud Computing — deploy de uma aplicação Python
em container Docker no Azure.

**Site no ar:** <https://webapp-deploylog-xocoa23.azurewebsites.net>

A página mostra qual versão do código está rodando no servidor (commit e
horário do build) e tem login com GitHub (OAuth).

## Tecnologias

Python, Flask, Docker, GitHub Actions, Azure Container Registry e Azure Web App.

## Como funciona o deploy

A cada push na branch `main`, o GitHub Actions (`.github/workflows/deploy.yml`):

1. constrói a imagem Docker e envia para o Azure Container Registry;
2. faz login no Azure, aponta o Web App para a imagem nova e reinicia;
3. valida o deploy: consulta `/versao` no site até ele responder com o
   commit do push.

## Rodando localmente

```bash
pip install -r requirements.txt
python app.py
```
