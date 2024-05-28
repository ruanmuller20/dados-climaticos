# Dependencias pip para instalar antes de rodar o projeto
  pip install fastapi[all]
  pip install requests
  pip install fastapi uvicornpip

# Depois da instalação é preciso ativar o plugin cliando duas vezes no icone
    depois disso rode o comando no terminal na pasta do projeto   
    rodar projeto com uvicorn main:app  --reload --host 0.0.0.0 --port 8000 elimina cors
    abra o arquivo index.html no seu chrome
    troque pelo seu ip local arquivo da linha 14 no index.html
