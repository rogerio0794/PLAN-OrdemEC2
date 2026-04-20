import json
from utils.nfp import calcular
from utils.filtro import fiter_run
from utils.mplan_grade import grids_optimization_pulp
from utils.class_api import *


def pipeline_planejador_grade(pedido):

    print()
    print("---------------INICIANDO PLANEJADOR DE GRADES-----------------")
    print()
    

    # FILTRO
    # print("INICIANDO FILTRO...")
    exemplo_json = fiter_run(pedido)    
    

    # NFP
    # print("FILTRO FINALIZADO... INICIANDO NFP")   
    exemplo_json = calcular(exemplo_json)    

    # OTIMIZADOR    
    # print("NFP FINALIZADO... INICIANDO OTIMIZADOR")
    output = grids_optimization_pulp(exemplo_json)
    
    
    # Lista de peças (patterns) e seus respectivos tempos de
    patterns = pedido["patterns"]
    
    pecas = [
        {
            "cut_order_pattern_id": item["cut_order_pattern_id"],
            "name": item["name"],
            "source_order_id": item["source_order_id"],
            "average_time_sewing_per_unit": item["average_time_sewing_per_unit"],
            "average_time_finishing_per_unit": item["average_time_finishing_per_unit"],
            "quantity": item["quantity"],
        }
        for item in patterns
    ]   

    # Cria novo dicionário final contendo os dados do exemplo.json no topo
    output_final = {
        "name": pedido.get("name"),
        "order_id": pedido.get("order_id"),
        "order_date": pedido.get("order_date"),
        "delivery_date": pedido.get("delivery_date"),
        "work_days_week": pedido.get("work_days_week", 0.0),
        "capacity_day_machine": pedido.get("capacity_day_machine", 0.0),
        "steps": pedido.get("steps"),
        "fabric": pedido.get("fabric"),
        "patterns": pecas,
        **output,  # Desestrutura o restante mantendo todas as chaves do cálculo
    }

    return output_final
