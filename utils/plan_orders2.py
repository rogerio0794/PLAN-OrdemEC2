import copy
import itertools
import string
from datetime import datetime


# ==========================================================
# DATE UTILS
# ==========================================================

def parse_date(date_str):
    return datetime.strptime(date_str, "%d/%m/%Y")


def format_date(date_obj):
    return date_obj.strftime("%d/%m/%Y")


# ==========================================================
# ORDER HELPERS
# ==========================================================

def count_total_pieces(order):
    total = 0
    for pattern in order.get("patterns", []):
        for color in pattern.get("quantity", {}).values():
            for qty in color.values():
                total += qty
    return total


def get_order_color(order):
    for pattern in order.get("patterns", []):
        qty = pattern.get("quantity", {})
        if qty:
            return list(qty.keys())[0]
    return None


# ==========================================================
# SPLIT ORDERS
# ==========================================================

def split_orders_by_patterns(orders):
    new_orders = []

    for order in orders:
        patterns = order.get("patterns", [])

        if len(patterns) <= 1:
            order_copy = order.copy()
            order_copy["patterns"] = []

            for p in patterns:
                p_copy = p.copy()
                p_copy["source_order_id"] = order["order_id"]
                order_copy["patterns"].append(p_copy)

            new_orders.append(order_copy)
            continue

        for idx, pattern in enumerate(patterns):
            new_order = order.copy()
            suffix = string.ascii_uppercase[idx]

            new_order["name"] = f"{order['name']}-{suffix}"

            p_copy = pattern.copy()
            p_copy["source_order_id"] = order["order_id"]

            new_order["patterns"] = [p_copy]
            new_orders.append(new_order)

    return new_orders


# ==========================================================
# CLUSTERING
# ==========================================================

def cluster_orders(orders, max_days_diff=2, max_cluster_size=5):
    clusters = []

    orders_sorted = sorted(orders, key=lambda x: parse_date(x["delivery_date"]))

    for order in orders_sorted:
        placed = False

        for cluster in clusters:
            ref = cluster[0]

            same_fabric = order["fabric"]["name"] == ref["fabric"]["name"]
            date_ok = abs(
                (parse_date(order["delivery_date"]) - parse_date(ref["delivery_date"])).days
            ) <= max_days_diff

            if same_fabric and date_ok:
                cluster.append(order)
                placed = True
                break

        if not placed:
            clusters.append([order])

    final_clusters = []
    for cluster in clusters:
        final_clusters.extend(split_cluster_balanced_recursive(cluster, max_cluster_size))

    for idx, cluster in enumerate(final_clusters):
        for order in cluster:
            order["cluster_id"] = idx

    return final_clusters


def split_cluster_balanced_recursive(cluster, max_size=5):
    if len(cluster) <= max_size:
        return [cluster]

    c1, c2 = split_cluster_balanced(cluster)

    return (
        split_cluster_balanced_recursive(c1, max_size) +
        split_cluster_balanced_recursive(c2, max_size)
    )


def split_cluster_balanced(cluster):
    orders_sorted = sorted(cluster, key=count_total_pieces, reverse=True)

    cluster_a, cluster_b = [], []
    load_a = load_b = 0

    for order in orders_sorted:
        pieces = count_total_pieces(order)

        if load_a <= load_b:
            cluster_a.append(order)
            load_a += pieces
        else:
            cluster_b.append(order)
            load_b += pieces

    return cluster_a, cluster_b


# ==========================================================
# COMBINATION LOGIC
# ==========================================================

def generate_combinations(cluster, max_size):
    for r in range(1, min(max_size, len(cluster)) + 1):
        yield from itertools.combinations(cluster, r)


def generate_pairs_and_singles(cluster):
    # individuais
    for job in cluster:
        yield [job]

    # pares
    for j1, j2 in itertools.combinations(cluster, 2):
        yield [j1, j2]


def combine_orders(orders):
    base = orders[0].copy()

    base["orders"] = [o["name"] for o in orders]
    base["delivery_date"] = min(o["delivery_date"] for o in orders)
    base["order_date"] = min(o.get("order_date", o["delivery_date"]) for o in orders)

    patterns = []
    for o in orders:
        for p in o.get("patterns", []):
            patterns.append(copy.deepcopy(p))

    base["patterns"] = patterns

    return base


def evaluate_combination(combo, planner):
    pedido = combine_orders(combo) if len(combo) > 1 else combo[0]

    print(f"→ Executando planner para: {[j['name'] for j in combo]}")

    try:
        result = planner(pedido)
    except Exception as e:
        print(f"✖ Erro no planner: {e}")
        return None

    status = result.get("status", "UNKNOWN")
    obj = result.get("objective", "N/A")

    print(f"   Status: {status} | Objective: {obj}")

    if status != "Optimal":
        return None

    return {
        "jobs": [j["name"] for j in combo],
        "combination": combo,
        "combination_names": [j["name"] for j in combo],
        "objective": obj,
        "result": result,
        "pedido": pedido
    }


# ==========================================================
# SET PARTITION (CORE OTIMIZAÇÃO)
# ==========================================================

def solve_set_partition(all_results, cluster):
    if not all_results:
        print("⚠ Nenhuma combinação válida encontrada!")
        return []

    all_jobs = set(o["name"] for o in cluster)

    best_solution = None
    best_cost = float("inf")

    print("\nTestando partições possíveis...\n")

    for r in range(1, len(all_results) + 1):
        for subset in itertools.combinations(all_results, r):

            used = set()
            cost = 0
            valid = True

            for item in subset:
                jobs = set(item["jobs"])

                if used & jobs:
                    valid = False
                    break

                used |= jobs
                cost += item["objective"]

            if not valid or used != all_jobs:
                continue

            print("Partição válida:", [i["combination_names"] for i in subset], f"| Custo: {cost}")

            if cost < best_cost:
                best_cost = cost
                best_solution = subset

    print("\n>>> MELHOR PARTIÇÃO:")
    for item in best_solution:
        print(item["combination_names"])
    print(f"Custo total: {best_cost}")

    return best_solution


# ==========================================================
# CLUSTER EVALUATION
# ==========================================================

def evaluate_cluster(cluster, planner, max_comb_size=3):
    print("\n--- Avaliando cluster ---")
    
    if len(cluster) > 3:
        print("Modo: PARES + INDIVIDUAIS")
        combos = generate_pairs_and_singles(cluster)
    else:
        print("Modo: COMBINAÇÕES COMPLETAS")
        combos = generate_combinations(cluster, max_comb_size)

    results = []

    for combo in combos:
        combo = list(combo)
        print(f"\nTestando combinação: {[o['name'] for o in combo]}")

        res = evaluate_combination(combo, planner)

        if res:
            print(f"✔ Sucesso | Custo: {res['objective']}")
            results.append(res)
        else:
            print("✖ Inválido ou erro")

    print("\n--- Resolvendo partição ótima ---")
    return solve_set_partition(results, cluster)


# ==========================================================
# OUTPUT
# ==========================================================

def build_cutting_orders_output(best_solution, cluster_id):
    output = []

    pedidos_cluster = sorted({
        o["name"]
        for item in best_solution
        for o in item["combination"]
    })

    for item in best_solution:
        combination = item["combination"]

        output.append({
            "cluster_id": cluster_id,
            "pedidos_cluster": pedidos_cluster,
            "ORDERS_ORDER_CUTTING": [o["name"] for o in combination],
            "cut_order": item["result"]
        })

    return output


# ==========================================================
# PIPELINE FINAL
# ==========================================================

def process_clusters(clusters, planner):
    output = []

    for i, cluster in enumerate(clusters):
        print(f"\n================ CLUSTER {i} =================")
        print(f"Pedidos no cluster: {[o['name'] for o in cluster]}")

        best_solution = evaluate_cluster(cluster, planner)

        print(f"\n>>> Melhor solução para cluster {i}:")
        for item in best_solution:
            print(f"  Combinação: {item['combination_names']} | Custo: {item['objective']}")

        output.extend(build_cutting_orders_output(best_solution, i))

    return output