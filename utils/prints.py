
def print_final_orders_grouped(cluster_results):
    print("\n================ RESULTADO FINAL =================\n")

    for cluster in cluster_results:
        cluster_id = cluster.get("cluster_id", "N/D")
        cluster_orders = cluster.get("orders", [])
        work_orders = cluster.get("work_orders", [])

        # Cabeçalho do cluster
        print(f"\n================ CLUSTER {cluster_id} =================")    
        
         #pedidos do cluster
        print(f"Pedidos no cluster: {cluster.get('original_orders', [])}")

        print("\n--- WORK ORDERS GERADAS ---")

        # Work orders dentro do cluster
        for wo in work_orders:
            print(f"\n=== Work Order {wo.get('work_order')} ===")

            # Tecido
            fabric_name = wo.get("fabric", {}).get("name", "N/D")
            print(f"Tecido: {fabric_name}")
            
            # Pedidos associados
            print(f"Pedidos: {wo.get('orders', [])}")
            print(f"Data do pedido: {wo.get('order_date', 'N/D')}")
            print(f"Data de entrega: {wo.get('delivery_date', 'N/D')}")
            print(f"Data de início: {wo.get('start_date', 'N/D')}")

            # Peças organizadas
            print("Peças:")

            patterns = wo.get("patterns", [])

            # Agrupar por pedido de origem (fica MUITO mais claro)
            grouped = {}
            for p in patterns:
                source = p.get("source_order", "N/D")
                grouped.setdefault(source, []).append(p.get("name", "N/D"))

            for source_order, pieces in grouped.items():
                print(f"  Pedido {source_order}:")
                for piece in pieces:
                    print(f"    - {piece}")

        print("\n" + "=" * 60) 
    
    
    

    
    
    
    
    
def print_clusters_full(clusters):
    print("\n================ CLUSTERS COMPLETOS =================\n")

    for i, cluster in enumerate(clusters):

        # 🔹 Lista de pedidos do cluster
        order_ids = [order["name"] for order in cluster]

        print(f"\nCluster {i} (tamanho {len(cluster)}):")
        print(f"Pedidos no cluster: {order_ids}")

        for order in cluster:
            fabric = order["fabric"]["name"]
            delivery = order["delivery_date"]

            print(f"\n  Pedido: {order['name']}")
            print(f"    Tecido: {fabric}")
            print(f"    Entrega: {delivery}")

            # 🔹 Patterns
            for pattern in order.get("patterns", []):
                pattern_name = pattern.get("name", "N/A")
                quantities = pattern.get("quantity", {})

                print(f"    Peça: {pattern_name}")

                for color, sizes in quantities.items():
                    print(f"      Cor: {color}")

                    for size, qty in sizes.items():
                        print(f"        Tam: {size} | Qtd: {qty}")

        print("\n" + "-" * 60)


def print_clusters(clusters):
    print("\n================ CLUSTERS =================\n")

    for i, cluster in enumerate(clusters):
        ids = [order["name"] for order in cluster]
        print(f"Cluster {i} (tamanho {len(cluster)}): {ids}")





def print_cutting_orders(output):
    print("\n================ ORDENS DE CORTE ================\n")

    for i, item in enumerate(output, 1):
        cut_order = item["cut_order"]

        print(f"ORDEM {i}")
        print("-" * 50)

        # 🔹 pedidos na ordem
        print(f"Pedidos na ordem: {item['ORDERS_ORDER_CUTTING']}")

        # 🔹 tecido
        fabric = cut_order.get("fabric", {})
        print(f"Tecido: {fabric.get('name')} (Gramatura: {fabric.get('gramatura')})")

        # 🔹 datas
        print(f"Data pedido: {cut_order.get('order_date')}")
        print(f"Data entrega: {cut_order.get('delivery_date')}")

        # 🔹 patterns (peças)
        print("\nPeças:")

        for pattern in cut_order.get("patterns", []):
            nome = pattern.get("name")
            # origem = pattern.get("order_id", "N/A")
            origem = pattern.get("source_order_id", "N/A")
            quantidade = pattern.get("quantity", {})

            print(f"  - Modelo: {nome}")
            print(f"    Pedido origem: {origem}")

            for cor, tamanhos in quantidade.items():
                print(f"    Cor: {cor}")
                for tamanho, qtd in tamanhos.items():
                    print(f"      {tamanho}: {qtd}")

        print("\nCustos:")
        print(f"  Custo tecido: {cut_order.get('cost_fabric')}")
        print(f"  Custo corte: {cut_order.get('cost_cut')}")
        print(f"  Custo setup: {cut_order.get('cost_setup')}")
        print(f"  Objetivo: {cut_order.get('objective')}")

        print("\n" + "=" * 60 + "\n")