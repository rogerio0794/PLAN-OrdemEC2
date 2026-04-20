import copy
from datetime import datetime
import string
import itertools


# SPLIT POR COR
def split_orders_by_color(orders):
    new_orders = []

    for order in orders:
        base_id = order["order_id"]
        base_name = order.get("name", base_id)

        suffix_iter = iter(string.ascii_uppercase)

        # Descobre todas as cores existentes
        colors = set()
        for pattern in order.get("patterns", []):
            colors.update(pattern.get("quantity", {}).keys())

        # Cria um pedido para cada cor
        for color in colors:
            new_order = copy.deepcopy(order)
            suffix = next(suffix_iter)

            new_order["order_id"] = f"{base_id}"
            new_order["name"] = f"{base_name}-{suffix}"

            filtered_patterns = []

            for pattern in new_order.get("patterns", []):
                quantities = pattern.get("quantity", {})

                if color in quantities:
                    pattern["quantity"] = {color: quantities[color]}
                    filtered_patterns.append(pattern)

            new_order["patterns"] = filtered_patterns
            new_orders.append(new_order)

    return new_orders

def split_orders_by_patterns(orders):
    """
    Divide pedidos que possuem múltiplos patterns em vários pedidos,
    um para cada pattern.

    Ex:
    P1 com 2 patterns -> P1-A, P1-B
    """

    new_orders = []

    for order in orders:
        patterns = order.get("patterns", [])

        # Caso simples: só 1 pattern → mantém (mas garante order_id no pattern)
        if len(patterns) <= 1:
            order_copy = copy.deepcopy(order)

            for p in order_copy.get("patterns", []):
                p["source_order_id"] = order_copy["order_id"]  # rastreabilidade

            new_orders.append(order_copy)
            continue

        # Caso múltiplos patterns → SPLIT
        for idx, pattern in enumerate(patterns):
            new_order = copy.deepcopy(order)

            suffix = string.ascii_uppercase[idx]  # A, B, C...

            # Atualiza nome do pedido (P1-A, P1-B...)
            new_order["name"] = f"{order['name']}-{suffix}"
            new_order["order_id"] = order["order_id"]

            # Copia o pattern e injeta origem
            p_copy = copy.deepcopy(pattern)
            p_copy["source_order_id"] = new_order["order_id"]  

            new_order["patterns"] = [p_copy]

            new_orders.append(new_order)

    return new_orders

##############################################################

def format_date(date_obj):
    return date_obj.strftime("%d/%m/%Y")


##############################################################

def parse_date(date_str):
    return datetime.strptime(date_str, "%d/%m/%Y")

##############################################################

def get_order_color(order):
    for pattern in order.get("patterns", []):
        qty = pattern.get("quantity", {})
        if qty:
            return list(qty.keys())[0]
    return None

##############################################################

# CLUSTERIZAÇÃO
def cluster_orders(orders, max_days_diff=2, max_cluster_size=5):
    clusters = []

    # Ordena por data de entrega
    orders_sorted = sorted(orders, key=lambda x: parse_date(x["delivery_date"]))

    for order in orders_sorted:
        placed = False

        order_fabric = order["fabric"]["name"]
        order_date = parse_date(order["delivery_date"])

        for idx, cluster in enumerate(clusters):
            ref = cluster[0]

            same_fabric = order_fabric == ref["fabric"]["name"]

            ref_date = parse_date(ref["delivery_date"])
            date_ok = abs((order_date - ref_date).days) <= max_days_diff

            if same_fabric and date_ok:
                cluster.append(order)
                placed = True
                break

        if not placed:
            clusters.append([order])

    # ------- NOVO: quebrar clusters grandes
    final_clusters = []
    for cluster in clusters:
        
        
        # splitted = split_cluster(cluster, max_cluster_size)
        splitted = split_cluster_balanced_recursive(cluster, max_cluster_size)
        final_clusters.extend(splitted)

    # ------- Reatribuir cluster_id corretamente
    for idx, cluster in enumerate(final_clusters):
        for order in cluster:
            order["cluster_id"] = idx

    print(f"Total de clusters formados: {len(final_clusters)}")
    print(f"Tamanhos dos clusters: {[len(c) for c in final_clusters]}")

    return final_clusters


def split_cluster_balanced_recursive(cluster, max_size=5):
    """
    Divide cluster recursivamente:
    - respeita tamanho máximo
    - mantém balanceamento de peças
    """

    if len(cluster) <= max_size:
        return [cluster]

    c1, c2 = split_cluster_balanced(cluster)

    return (
        split_cluster_balanced_recursive(c1, max_size) +
        split_cluster_balanced_recursive(c2, max_size)
    )


## Contar a quantidade de peças totais de um pedido (soma de todas as cores e tamanhos)
def count_total_pieces(order):
    total = 0

    for pattern in order.get("patterns", []):
        quantities = pattern.get("quantity", {})

        for color in quantities.values():
            for qty in color.values():
                total += qty

    # print(f"Pedido {order['name']} tem total de peças: {total}")

    return total


def split_cluster_balanced(cluster):
    """
    Divide um cluster em dois subclusters equilibrando
    a quantidade total de peças.
    """

    # Ordena por volume de peças (maior primeiro)
    orders_sorted = sorted(cluster, key=lambda x: count_total_pieces(x), reverse=True)

    cluster_a = []
    cluster_b = []

    load_a = 0
    load_b = 0

    for order in orders_sorted:
        pieces = count_total_pieces(order)

        if load_a <= load_b:
            cluster_a.append(order)
            load_a += pieces
        else:
            cluster_b.append(order)
            load_b += pieces

    return [cluster_a, cluster_b]


def split_cluster(cluster, max_size=5):
    """
    Divide recursivamente um cluster até que todos tenham tamanho <= max_size
    """
    if len(cluster) <= max_size:
        return [cluster]

    mid = len(cluster) // 2

    left = cluster[:mid]
    right = cluster[mid:]

    return split_cluster(left, max_size) + split_cluster(right, max_size)


##############################################################

# COMBINAR PEDIDOS
def combine_orders(orders):
    """
    Combina multiplos pedidos em uma unica ordem produtiva.
    O resultado junta os patterns dos pedidos combinados.
    """
    base = copy.deepcopy(orders[0])

    base["orders"] = [o["name"] for o in orders]  # lista de nomes
    base["delivery_date"] = min(o["delivery_date"] for o in orders)
    base["order_date"] = min(o.get("order_date", o["delivery_date"]) for o in orders)
    
    combined_patterns = []
    for o in orders:
        
        
        for p in o.get("patterns", []):
            p_copy = copy.deepcopy(p)
            combined_patterns.append(p_copy)

    base["patterns"] = combined_patterns
    

    return base


##############################################################
# AVALIAÇÃO DE CLUSTER
def evaluate_cluster(cluster, pipeline_planejador_grade, max_comb_size=3):
    
    
  

    print("\n================ AVALIANDO CLUSTER =================\n")

    # NOVA REGRA
    if len(cluster) > 3:
        best_solution = evaluate_large_cluster(cluster, pipeline_planejador_grade)
        return best_solution

    # CLUSTERS PEQUENOS (mantém lógica original)
    all_results = []

    for r in range(1, min(max_comb_size, len(cluster)) + 1):
        for combo in itertools.combinations(cluster, r):
            combo = list(combo)

            combo_ids = [job["name"] for job in combo]
            print(f"\nTestando combinação: {combo_ids}")

            pedido = combine_orders(combo) if len(combo) > 1 else combo[0]

            try:
                result = pipeline_planejador_grade(pedido)
            except Exception as e:
                print(f"Erro no planner: {combo_ids} -> {e}")
                continue           

            all_results.append({
                "jobs": [id(j) for j in combo],
                "combination": combo,
                "combination_names": [j["name"] for j in combo],
                "objective": result.get("objective", float("inf")),
                "result": result,
                "pedido": pedido
            })

    if not all_results:
        return []

    # mantém sua lógica de partição ótima
    all_jobs_set = set(id(job) for job in cluster)
    best_solution = None
    best_cost = float("inf")

    for r in range(1, len(all_results)+1):
        for subset in itertools.combinations(all_results, r):
            used_jobs = set()
            total_cost = 0
            valid = True

            for item in subset:
                item_jobs = set(item["jobs"])
                if used_jobs & item_jobs:
                    valid = False
                    break

                used_jobs |= item_jobs
                total_cost += item["objective"]

            if not valid or used_jobs != all_jobs_set:
                continue
            
            print(f"Testando partição:")
            for item in subset:
                print([j["name"] for j in item["combination"]], end=" | ")
            print(f" -> Custo total: {total_cost}")

            if total_cost < best_cost:
                best_cost = total_cost
                best_solution = subset
                
      #  Resultado final
    print("\n MELHOR SOLUÇÃO GLOBAL:")
    for item in best_solution:
        print([j["name"] for j in item["combination"]])

    print(f"Custo total: {best_cost}")


    return best_solution














##############################################################
# PROCESSAMENTO FINAL
def process_clusters(clusters, pipeline_planejador_grade):
    output_completo = []
    # output_enxuto = []
    

    for i, cluster in enumerate(clusters):
        print(f"\n================ CLUSTER {i} ================\n")

        best_solution = evaluate_cluster(cluster, pipeline_planejador_grade)
        
        

        cluster_full = build_cutting_orders_output(best_solution, i)
        
        output_completo.extend(cluster_full)

        # cluster_light = build_cutting_orders_output_light(best_solution, i)
        # output_enxuto.extend(cluster_light)


    return output_completo


##############################################################
# função para clusters grandes

def evaluate_large_cluster(cluster, pipeline_planejador_grade):

    print("\n================ CLUSTER GRANDE (pares + individuais) =================\n")

    all_results = []

    # TESTAR INDIVIDUAIS
    for job in cluster:
        print(f"Testando individual: {job['name']}")

        try:
            result = pipeline_planejador_grade(job)
        except Exception as e:
            print(f"Erro: {job['name']} -> {e}")
            continue

        if result.get("status") != "Optimal":
            continue

        all_results.append({
            "jobs": [id(job)],
            "combination": [job],
            "combination_names": [job["name"]],
            "objective": result.get("objective", float("inf")),
            "result": result,
            "pedido": job
        })

    # TESTAR TODOS OS PARES
    for j1, j2 in itertools.combinations(cluster, 2):
        print(f"Testando par: {[j1['name'], j2['name']]}")

        pedido_comb = combine_orders([j1, j2])

        try:
            result = pipeline_planejador_grade(pedido_comb)
        except Exception as e:
            print(f"Erro no par: {[j1['name'], j2['name']]} -> {e}")
            continue

        if result.get("status") != "Optimal":
            continue

        all_results.append({
            "jobs": [id(j1), id(j2)],
            "combination": [j1, j2],
            "combination_names": [j1["name"], j2["name"]],
            "objective": result.get("objective", float("inf")),
            "result": result,
            "pedido": pedido_comb
        })

    if not all_results:
        return []

    # PARTIÇÃO ÓTIMA (cobrindo todos os pedidos)
    all_jobs_set = set(id(job) for job in cluster)

    best_solution = None
    best_cost = float("inf")

    print("\n================ TESTANDO PARTIÇÕES =================\n")

    for r in range(1, len(all_results) + 1):
        for subset in itertools.combinations(all_results, r):

            used_jobs = set()
            total_cost = 0
            valid = True

            for item in subset:
                item_jobs = set(item["jobs"])

                # sobreposição
                if used_jobs & item_jobs:
                    valid = False
                    break

                used_jobs |= item_jobs
                total_cost += item["objective"]

            # não cobre todos
            if not valid or used_jobs != all_jobs_set:
                continue

            print("Partição:")
            for item in subset:
                print(item["combination_names"], end=" | ")
            print(f" -> custo: {total_cost}")

            if total_cost < best_cost:
                best_cost = total_cost
                best_solution = subset

    print("\n✔ MELHOR SOLUÇÃO:")
    for item in best_solution:
        print(item["combination_names"])

    print(f"Custo total: {best_cost}")

    return best_solution







######################################################
# Ajustar saída do planner para formato de ordens de corte (com informações dos pedidos originais)

def build_cutting_orders_output(best_solution, cluster_id):
    output = []

    # Lista de todos os pedidos do cluster
    pedidos_cluster = sorted({
        o["name"]
        for item in best_solution
        for o in item["combination"]
    })

    for item in best_solution:
        pedido = item["pedido"]
        result = item["result"]
        combination = item["combination"]

        # 🔹 nomes dos pedidos nessa ordem de corte
        order_names = [o["name"] for o in combination]

        # 🔹 menor data de entrega
        min_delivery = min(parse_date(o["delivery_date"]) for o in combination)

        # 🔹 menor data de pedido
        min_order_date = min(parse_date(o.get("order_date", o["delivery_date"])) for o in combination)

        # 🔹 patterns com origem
        patterns = []
        for o in combination:
            for p in o.get("patterns", []):
                p_copy = copy.deepcopy(p)

                # remove grades (caso queira versão enxuta)
                p_copy.pop("grades", None)

                p_copy["source_order"] = o["name"]
                patterns.append(p_copy)
                

        # 🔹 montar estrutura final
        output.append({
            "cluster_id": cluster_id,
            "pedidos_cluster": pedidos_cluster,
            "ORDERS_ORDER_CUTTING": order_names,
            "cut_order":  result, 
        })

    return output




def build_cutting_orders_output_light(best_solution, cluster_id):
    full = build_cutting_orders_output(best_solution, cluster_id)

    for item in full:
        
        
        result_data = item["cut_order"]["results"]

        spreads = result_data.get("results", {}).get("spreads")
        total = result_data.get("results", {}).get("total")

        operating_results = result_data.get("operating_results")

        item["cut_order"]["results"] = {
            "spreads": spreads,
            "total": total
        }

        item["cut_order"]["operating_results"] = operating_results

    return full