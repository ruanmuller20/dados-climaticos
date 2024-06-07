# Dependencias pip para instalar antes de rodar o projeto (obs: Usar versão mais atualizada do python)
  pip install fastapi[all]
  pip install requests
  pip install numpy
  pip install plotly
  pip install pandas
  pip install db-sqlite3
  

# Passo a Passo para rodar o projeto
    Troque pelo seu ip local na linha 23 no arquivo script.js
    depois disso rode o comando no terminal na pasta do projeto   
    rodar projeto com 'uvicorn main:app  --reload --host 0.0.0.0 --port 8000' ou clicar no arquivo 'rodar_servidor.bat'
    Abra o arquivo index.html no seu chrome