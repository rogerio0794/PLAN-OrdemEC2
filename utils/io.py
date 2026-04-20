import copy
from datetime import datetime
import string
import json
import glob

def carregar_pedidos(pasta):
    """
    Lê todos os arquivos .json dentro da pasta indicada
    e retorna uma lista de dicionários.
    """
    lista = []
    for arquivo in glob.glob(f"{pasta}/*.json"):
        with open(arquivo, "r", encoding="utf-8") as f:
            dados = json.load(f)
            lista.append(dados)
    return lista










    
def salvar_json(caminho, dados):
    with open(caminho, "w", encoding="utf-8") as f:
        json.dump(dados, f, indent=4, ensure_ascii=False)
        
def abrir_json(caminho):
    with open(caminho, "r", encoding="utf-8") as f:
        dados = json.load(f)        
    return dados


