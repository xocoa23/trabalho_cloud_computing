# DeployLog

Aplicação web em Python que mostra qual versão do código está rodando no
servidor. O commit e o horário do build são gravados na imagem Docker durante
o build e lidos pela aplicação como variáveis de ambiente. Não há banco de
dados: a página é um reflexo direto do artefato publicado.

Trabalho da disciplina de Cloud Computing — deploy com container no Azure.

## Tecnologias

Python 3.12, Flask, Gunicorn, GitHub OAuth (Authlib), Docker,
Azure Container Registry, Azure Web App for Containers, GitHub Actions.

## Arquitetura

```
  desenvolvedor
       |  git push (main)
       v
  +------------------+
  |  GitHub Actions  |   o build acontece aqui, no runner do GitHub
  |  docker build    |
  +--------+---------+
           | docker push
           v
  +------------------+          +------------------------+
  | Azure Container  | -------> |  Azure Web App         |
  | Registry         |   pull   |  for Containers        |
  +------------------+          +-----------+------------+
           ^                                |
           |   az webapp config + restart   |  URL publica HTTPS
           +---- (GitHub Actions) ----------+
                                            |
                          curl /versao  <---+  validacao

  Tudo dentro do Resource Group rg-deploylog
```

## Fluxo do CI/CD

1. Push na branch `main` dispara `.github/workflows/deploy.yml`.
2. O runner do GitHub constrói a imagem, injetando o SHA do commit e o
   horário do build como argumentos de build.
3. A imagem é publicada no Azure Container Registry.
4. O workflow faz login no Azure, aponta o Web App para a imagem nova
   (`az webapp config container set`) e reinicia o Web App.
5. **Validação:** o workflow consulta `https://<webapp>/versao` até a
   resposta conter o SHA do commit que disparou o pipeline. Se em 5 minutos
   o site não estiver servindo a versão nova, o pipeline fica vermelho.

## Rodando localmente

```bash
pip install -r requirements.txt
python app.py          # http://localhost:8000
                       # http://localhost:8000/versao  (JSON com commit e build)
```

## Secrets do repositório

| Secret | Valor |
|---|---|
| `ACR_SERVIDOR` | `<nome-do-acr>.azurecr.io` |
| `ACR_USUARIO` | nome do ACR |
| `ACR_SENHA` | senha de administrador do ACR |
| `AZURE_CREDENTIALS` | JSON do service principal (ver abaixo) |

Gerando o `AZURE_CREDENTIALS` (no Cloud Shell do portal Azure):

```bash
az ad sp create-for-rbac --name sp-deploylog --role contributor \
  --scopes /subscriptions/<id-da-assinatura>/resourceGroups/rg-deploylog \
  --json-auth
```

## App settings do Web App

| Setting | Valor |
|---|---|
| `WEBSITES_PORT` | `8000` (porta do gunicorn) |
| `APP_ENV` | `producao` |
| `SECRET_KEY` | texto aleatório longo |
| `GITHUB_CLIENT_ID` / `GITHUB_CLIENT_SECRET` | da OAuth App |

## Autenticação GitHub

OAuth App registrada em <https://github.com/settings/developers>, com callback
apontando para `https://<webapp>.azurewebsites.net/callback`. O client id e o
secret ficam nas app settings do Web App, nunca no código.

## Encerrando

```bash
az group delete --name rg-deploylog --yes --no-wait
```
