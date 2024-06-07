from fastapi import FastAPI
from requests import *
from fastapi.middleware.cors import CORSMiddleware
import main
import numpy as np
import pandas as pd
import plotly.express as px
import sqlite3
from datetime import datetime
import sys


app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def grafico_ar(lat, long):
    conexao = sqlite3.connect('poluentes_do_ar.db')
    cursor = conexao.cursor()

    # Criar a tabela se não existir
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS dados (
        id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
        nome_poluente TEXT,
        qtd_poluente REAL
    );
    """)

    # Limpar a tabela antes de inserir os novos dados
    cursor.execute("DELETE FROM dados")

    # Fazer a requisição à API e extrair os dados
    chave_api = "70c85c4d9e45c8a96fd7ab5d1efaec5e"
    link_api = f'http://api.openweathermap.org/data/2.5/air_pollution?lat={lat}&lon={long}&appid={chave_api}&lang=pt-br'
    requisicao = get(link_api).json()
    dados_ar = requisicao['list'][0]['components']

    # Inserir os novos dados na tabela
    for poluente, quantidade in dados_ar.items():
        cursor.execute("INSERT INTO dados (nome_poluente, qtd_poluente) VALUES (?, ?)", (poluente, quantidade))

    # Carregar os dados da consulta em um DataFrame
    consulta_sql = "SELECT * FROM dados"
    data_frame = pd.read_sql_query(consulta_sql, conexao)

    # Confirmar as alterações e fechar a conexão com o banco de dados
    conexao.commit()
    conexao.close()

    # Criar o DataFrame do índice de poluentes
    indice = {
        "Nome Qualitativo": ["Bom", "Razoável", "Moderado", "Ruim", "Muito Ruim"],
        "Índice": [1, 2, 3, 4, 5],
        "SO2": ["[0; 20)", "[20; 80)", "[80; 250)", "[250; 350)", "⩾350"],
        "NO2": ["[0; 40)", "[40; 70)", "[70; 150)", "[150; 200)", "⩾200"],
        "PM10": ["[0; 20)", "[20; 50)", "[50; 100)", "[100; 200)", "⩾200"],
        "PM2.5": ["[0; 10)", "[10; 25)", "[25; 50)", "[50; 75)", "⩾75"],
        "O3": ["[0; 60)", "[60; 100)", "[100; 140)", "[140; 180)", "⩾180"],
        "CO": ["[0; 4400)", "[4400; 9400)", "[9400; 12400)", "[12400; 15400)", "⩾15400"]
    }
    indice_df = pd.DataFrame(indice)

    # Função para verificar a qualidade do ar com base nos intervalos definidos pelo índice
    def verificar_qualidade_do_ar(dados_poluentes, dados_indice):
        qualidade_do_ar = "Desconhecida"

        for i, linha in dados_indice.iterrows():
            poluentes_dentro_do_intervalo = True
            for poluente in dados_poluentes['nome_poluente']:
                if poluente in linha:
                    intervalo = linha[poluente].strip('[]()').replace("⩾", "").split(';')  # Remove caracteres especiais e divide o intervalo
                    valor_min = float(intervalo[0])
                    valor_max = float(intervalo[1]) if len(intervalo) > 1 else float('inf')
                    valor_poluente = dados_poluentes[dados_poluentes['nome_poluente'] == poluente]['qtd_poluente'].values[0]
                    if not (valor_min <= valor_poluente < valor_max):
                        poluentes_dentro_do_intervalo = False
                        break
            if poluentes_dentro_do_intervalo:
                qualidade_do_ar = linha["Nome Qualitativo"]
                break

        return qualidade_do_ar

    # Verificar a qualidade do ar
    qualidade_do_ar = verificar_qualidade_do_ar(data_frame, indice_df)
    data_frame["Qualidade do Ar"] = qualidade_do_ar

    # Plotar o gráfico com degradê de cores e animação
    fig = px.bar(data_frame, x='nome_poluente', y='qtd_poluente', color='qtd_poluente',
                color_continuous_scale='Viridis',  # Escolha o esquema de cores de sua preferência
                labels={'nome_poluente': 'Nome do Poluente', 'qtd_poluente': 'Quantidade do Poluente (µg/m³)'},
                title=f'Qualidade do Ar em {lat}, {long}')

    fig.update_layout(coloraxis_colorbar=dict(
        title="Concentração",
        tickvals=[min(data_frame['qtd_poluente']), max(data_frame['qtd_poluente'])],
        ticktext=["Baixa", "Alta"]
    ))

    # Salvar o gráfico como HTML e abrir no navegador
    fig.write_html("qualidade_do_ar2.html")
    
    


    



@app.get("/{lat}/{long}")
async def root(lat: str,long: str):
    chave_api = '70c85c4d9e45c8a96fd7ab5d1efaec5e' # permite a comunicação da API com a aplicação 
    
    try: 
        link = f'https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={long}&appid={chave_api}&lang=pt_br'

        requisicao = get(link).json() # O metdo get serve para captar o link da API e o metodo JSON serve para converter os dados informados pela API em listas e dicionarios python 
        nomeCidade = requisicao['name']
        descricao = requisicao['weather'][0]['description'] # ['weather'][0] é o campo onde a descrição está dentro o campo ['description'] serve apenas para pegar a informação de descrição do céu/temperatura que está dentro de ['weather'][0] 
        temperatura = requisicao['main']['temp']- 273.15 #
        temp_min = requisicao['main']['temp_min'] - 273.15  # Converte Kelvin para Celsius
        temp_max = requisicao['main']['temp_max'] - 273.15  # Converte Kelvin para Celsius
        horaAtual = datetime.now() #AQUI EU COLOQUEI UMA VARIAVEL E CHAMEI A CLASSE DATATIME.NOW() PARA OBTER A DATA EXATA
               
        hora = int(horaAtual.hour) #AQUI EU COLOQUEI A VARIAVEL Hora = HoraAtual."hour" para obter a hora exata
        
        grafico_ar(lat,long)
      
      #QUANDO A HORA FOR MAIOR DO QUE 6 E MENOR DO QUE 18, A IMAGEM SERÁ DO SOL
      # 
      ##              V              and      F
      
        if (descricao == 'céu limpo') and (hora > 6 and hora < 17):
         return {"message": f'{nomeCidade}',
        "temperatura":f'{temperatura:.0f}°',
        "tempo": "<img src='./src/04.png' alt='Nuvem'>",
        "descricao":f'{descricao}',
        "hora":f'{hora}',
        "temp_min":f'{temp_min:.1f}',    
        "temp_max":f'{temp_max:.1f}'  
                }
       
       #QUANDO A HORA FOR MAIOR DO QUE 19 E MENOR DO QUE 5, A IMAGEM SERÁ DA LUA
       ##                       V  and  V
        elif (descricao == 'céu limpo') and ((hora >= 18 and hora <= 23 ) or(  hora >=0 and  hora <=5)):
         return {"message": f'{nomeCidade}',
        "temperatura":f'{temperatura:.0f}°',
        "tempo": "<img src='./src/07.png' alt='Nuvem'>",
        "descricao":f'{descricao}',
        "hora":f'{hora}',      
        "temp_min":f'{temp_min:.1f}',    
        "temp_max":f'{temp_max:.1f}'
                }
        
        #QUANDO A HORA FOR MAIOR DO QUE 6 E MENOR DO QUE 18, A IMAGEM SERÁ DO SOL
        elif descricao == 'algumas nuvens' or descricao == 'nuvens dispersas' and (hora > 6 and hora < 17):
          return {"message": f'{nomeCidade}',
        "temperatura":f'{temperatura:.0f}°',
        "tempo": "<img src='./src/Nublado.png' alt='Nuvem'>",
        "descricao":f'{descricao}',      
        "temp_min":f'{temp_min:.1f}',    
        "temp_max":f'{temp_max:.1f}'      
                }
        #QUANDO A HORA FOR MAIOR DO QUE 18 E MENOR DO QUE 6, A IMAGEM SERÁ DA LUA
        elif descricao == 'algumas nuvens' or descricao == 'nuvens dispersas' and ((hora >= 18 and hora <= 23 ) or(  hora >=0 and  hora <=5)):
          return {"message": f'{nomeCidade}',
        "temperatura":f'{temperatura:.0f}°',
        "tempo": "<img src='./src/06.png' alt='Nuvem'>",
        "descricao":f'{descricao}',
        "temp_min":f'{temp_min:.1f}',    
        "temp_max":f'{temp_max:.1f}'      
              }
         #QUANDO A HORA FOR MAIOR DO QUE 6 E MENOR DO QUE 18, A IMAGEM SERÁ DO SOL
        elif descricao == 'nublado' and (hora > 6 and hora < 17):
          return {"message": f'{nomeCidade}',
        "temperatura":f'{temperatura:.0f}°',
        "tempo": "<img src='./src/09.png' alt='Nuvem'>",
        "descricao":f'{descricao}',      
        "temp_min":f'{temp_min:.1f}',    
        "temp_max":f'{temp_max:.1f}'      
                }
        #QUANDO A HORA FOR MAIOR DO QUE 18 E MENOR DO QUE 6, A IMAGEM SERÁ DA LUA
        elif descricao == 'nublado' and ((hora >= 18 and hora <= 23 ) or(  hora >=0 and  hora <=5)):
          return {"message": f'{nomeCidade}',
        "temperatura":f'{temperatura:.0f}°',
        "tempo": "<img src='./src/05.png' alt='Nuvem'>",
        "descricao":f'{descricao}',      
        "temp_min":f'{temp_min:.1f}',    
        "temp_max":f'{temp_max:.1f}'      
                }
        #QUANDO A HORA FOR MAIOR DO QUE 6 E MENOR DO QUE 18, A IMAGEM SERÁ DO SOL
        elif descricao == 'chuva leve' or descricao == 'chuva moderada' and (hora > 6 and hora < 17):
         return {"message": f'{nomeCidade}',
        "temperatura":f'{temperatura:.0f}°',
        "tempo": "<img src='./src/08.png' alt='Nuvem'>",
        "descricao":f'{descricao}',      
        "temp_min":f'{temp_min:.1f}',    
        "temp_max":f'{temp_max:.1f}'      
                }
        #QUANDO A HORA FOR MAIOR DO QUE 18 E MENOR DO QUE 6, A IMAGEM SERÁ DA LUA
        elif descricao == 'chuva leve' or descricao == 'chuva moderada' and ((hora >= 18 and hora <= 23 ) or(  hora >=0 and  hora <=5)):
         return {"message": f'{nomeCidade}',
        "temperatura":f'{temperatura:.0f}°',
        "tempo": "<img src='./src/08.png' alt='Nuvem'>",
        "descricao":f'{descricao}',      
        "temp_min":f'{temp_min:.1f}',    
        "temp_max":f'{temp_max:.1f}'      
                }
            #QUANDO A HORA FOR MAIOR DO QUE 6 E MENOR DO QUE 18, A IMAGEM SERÁ DO SOL
        elif descricao == 'chuva forte' or descricao == 'chuva muito forte' and (hora > 6 and hora < 17):
         return {"message": f'{nomeCidade}',
        "temperatura":f'{temperatura:.0f}°',
        "tempo": "<img src='./src/11.png' alt='Nuvem'>",
        "descricao":f'{descricao}',      
        "temp_min":f'{temp_min:.1f}',    
        "temp_max":f'{temp_max:.1f}'      
                }
        #QUANDO A HORA FOR MAIOR DO QUE 18 E MENOR DO QUE 6, A IMAGEM SERÁ DA LUA
        elif descricao == 'chuva forte' or descricao == 'chuva muito forte' and ((hora >= 18 and hora <= 23 ) or(  hora >=0 and  hora <=5)):
         return {"message": f'{nomeCidade}',
        "temperatura":f'{temperatura:.0f}°',
        "tempo": "<img src='./src/11.png' alt='Nuvem'>",
        "descricao":f'{descricao}',      
        "temp_min":f'{temp_min:.1f}',    
        "temp_max":f'{temp_max:.1f}'      
                }
        #QUANDO A HORA FOR MAIOR DO QUE 6 E MENOR DO QUE 18, A IMAGEM SERÁ DO SOL
        elif descricao == 'névoa' and (hora > 6 and hora < 17):
         return {"message": f'{nomeCidade}',
        "temperatura":f'{temperatura:.0f}°',
        "tempo": "<img src='./src/12.png' alt='Nuvem'>",
        "descricao":f'{descricao}',      
        "temp_min":f'{temp_min:.1f}',    
        "temp_max":f'{temp_max:.1f}'      
                }
        #QUANDO A HORA FOR MAIOR DO QUE 18 E MENOR DO QUE 6, A IMAGEM SERÁ DA LUA
        elif descricao == 'névoa' and ((hora >= 18 and hora <= 23 ) or(  hora >=0 and  hora <=5)):
         return {"message": f'{nomeCidade}',
        "temperatura":f'{temperatura:.0f}°',
        "tempo": "<img src='./src/12.png' alt='Nuvem'>",
        "descricao":f'{descricao}',      
        "temp_min":f'{temp_min:.1f}',    
        "temp_max":f'{temp_max:.1f}'      
                }
            
        elif descricao == 'trovoadas' or descricao == 'trovoada com chuva fraca' and (hora > 6 and hora < 17):
         return {"message": f'{nomeCidade}',
        "temperatura":f'{temperatura:.0f}°',
        "tempo": "<img src='./src/10.png' alt='Nuvem'>",
        "descricao":f'{descricao}',      
        "temp_min":f'{temp_min:.1f}',    
        "temp_max":f'{temp_max:.1f}'      
                }

        
        elif descricao == 'trovoadas' or descricao == 'trovoada com chuva fraca' and ((hora >= 18 and hora <= 23 ) or(  hora >=0 and  hora <=5)):
         return {"message": f'{nomeCidade}',
        "temperatura":f'{temperatura:.0f}°',
        "tempo": "<img src='./src/10.png' alt='Nuvem'>",
        "descricao":f'{descricao}',      
        "temp_min":f'{temp_min:.1f}',    
        "temp_max":f'{temp_max:.1f}'      
                }

        else :
            return {"message": f'{nomeCidade}',
                "temperatura":f'{temperatura:.0f}°',
                "tempo": "<img src='./src/05.png' alt='else'>",
                "descricao":f'{descricao}',
                "temp_min":f'{temp_min:.1f}',
                "temp_max":f'{temp_max:.1f}'      
                        }

    except Exception as e:
        return {"message": f'Não foi possivel encontrar Latitude {lat} e Longitude {long}' }
  