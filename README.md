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
  | Registry         |  webhook |  for Containers        |
  +------------------+          +-----------+------------+
                                            |
                                     URL publica HTTPS

  Tudo dentro do Resource Group rg-deploylog
```

## Fluxo do CI/CD

1. Push na branch `main` dispara `.github/workflows/deploy.yml`.
2. O runner do GitHub constrói a imagem, injetando o SHA do commit e o
   horário do build como argumentos de build.
3. A imagem é publicada no Azure Container Registry.
4. O Web App está com deploy contínuo ligado: o ACR avisa por webhook e o
   Web App puxa a imagem nova e reinicia sozinho.

O Azure não precisa de credencial do GitHub e o GitHub não precisa de
credencial do Azure além do acesso ao registry.

## Rodando localmente

```bash
pip install -r requirements.txt
python app.py          # http://localhost:8000
```

## Secrets do repositório

| Secret | Valor |
|---|---|
| `ACR_SERVIDOR` | `<nome-do-acr>.azurecr.io` |
| `ACR_USUARIO` | nome do ACR |
| `ACR_SENHA` | senha de administrador do ACR |

## Autenticação GitHub

OAuth App registrada em <https://github.com/settings/developers>, com callback
apontando para `https://<webapp>.azurewebsites.net/callback`. O client id e o
secret ficam nas app settings do Web App, nunca no código.

## Encerrando

```bash
az group delete --name rg-deploylog --yes --no-wait
```
