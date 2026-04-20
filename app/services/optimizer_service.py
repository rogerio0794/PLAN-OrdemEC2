# app/services/optimizer_service.py

from utils.plan_orders2 import (
    split_orders_by_patterns,
    cluster_orders,
    process_clusters
)
from utils.io import *

from utils.pipeline_grades import pipeline_planejador_grade


def run_optimization(data):
    info = data["info"]
    orders = data["orders"]
            
    salvar_json("info.json", info)
    salvar_json("orders.json", orders)
    

    print("\n========== INICIANDO OTIMIZAÇÃO ==========")
    print(f"Total de pedidos recebidos: {len(orders)}")

    # Split
    orders_split = split_orders_by_patterns(orders)
    print(f"Após split: {len(orders_split)} pedidos")

    # Clusterização
    clusters = cluster_orders(
        orders_split,
        max_days_diff=info.get("max_days_diff", 2),
        max_cluster_size=info.get("max_cluster_size", 5)
    )
    print(f"Total de clusters: {len(clusters)}")

    # Processamento final
    output = process_clusters(clusters, pipeline_planejador_grade)
    salvar_json("saida_completa.json", output)


    print("========== FIM DA OTIMIZAÇÃO ==========\n")

    return output
