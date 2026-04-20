import pulp
import numpy as np
import json
import time


def output_json(input_json, optimization_data, layouts_data):
    """Output json Generator.

    Args:
        input_json (dict): Input Json file.
        optimization_data (dict): Info and Variables of optimization.
        layouts_data (dict): grid data.

    Returns:
        dict: Results.
    """
    
    WIDTH =  [width['width'] for width in input_json['fabric']['widths']]
    DEMANDS = input_json['demands']
    #Settings
    cost_overproduction_allowed = input_json['settings']['cost_overproduction_allowed']
    speed = input_json['settings']['speed']
    #Fabric
    price_per_linear_meter = [width['cost_per_meter'] for width in input_json['fabric']['widths']] #W
    #Cost Operations
    cost_per_cut_meter = input_json['settings']['cost_cut']*layouts_data['price_fabric_meter']
    cost_setup = input_json['settings']['cost_setup']*layouts_data['price_fabric_meter']

    output_json = {
        "status": optimization_data['status'],
        "objective": np.round(optimization_data['objective'], 4),
        "cost_overproduction_allowed": np.round(cost_overproduction_allowed*\
                                                sum(optimization_data['variables']['u'][c][p][s]*layouts_data['cost_piece'][p][s]
                                                                                for c in DEMANDS for p in range(len(DEMANDS[c]))
                                                                                    for s in DEMANDS[c][p]), 2),
        "cost_fabric": np.round(sum(price_per_linear_meter[id_w]*\
                                    layouts_data['length'][w][l]*\
                                        sum(optimization_data['variables']['x'][c][w][l]
                                            for c in DEMANDS) for id_w,w in enumerate(WIDTH)
                                                for l in range(len(layouts_data['grades'][w]))), 2),
        "cost_cut": np.round((1+speed)*cost_per_cut_meter*\
                             sum(layouts_data['perimeter'][w][l]*\
                                 optimization_data['variables']['z'][w][l]
                                 for w in WIDTH for l in range(len(layouts_data['grades'][w]))), 2),
        "cost_setup": np.round((1+speed)*cost_setup*\
                               sum(optimization_data['variables']['z'][w][l]
                                   for w in WIDTH for l in range(len(layouts_data['grades'][w]))), 2),
        "results": {"spreads": {}}
    }

    for w in WIDTH:
        if sum(optimization_data['variables']['z'][w][l]
               for l in range(len(layouts_data['grades'][w])))>0.0:
            output_json['results']['spreads'][w] = []
            for l in range(len(layouts_data['grades'][w])):
                if optimization_data['variables']['z'][w][l]>0.0:
                    output_json['results']['spreads'][w].append({
                        'grades': layouts_data['grades'][w][l],
                        'layers': int(sum(optimization_data['variables']['x'][c][w][l]
                                          for c in DEMANDS)),
                        'spread_quantity': int(optimization_data['variables']['z'][w][l]),
                        'colorways': {c:int(optimization_data['variables']['x'][c][w][l])
                                        for c in DEMANDS
                                            if optimization_data['variables']['x'][c][w][l]>0.0},
                        'saving': layouts_data['saving'][w][l],
                        'spread_length': np.round(1e3*layouts_data['length'][w][l], 2),
                        'total_perimeter': np.round(1e3*layouts_data['perimeter'][w][l], 2),
                    })

    output_json['results']['total'] = {}
    for c in DEMANDS:
        output_json['results']['total'][c] = {
            'production': [{s:int(sum(layouts_data['grades'][w][l][p][s]*\
                                      optimization_data['variables']['x'][c][w][l]
                                        for w in WIDTH for l in range(len(layouts_data['grades'][w]))))
                                            for s in DEMANDS[c][p]}
                                                for p in range(len(DEMANDS[c]))],
            'over': [{s:int(sum(layouts_data['grades'][w][l][p][s]*\
                                optimization_data['variables']['x'][c][w][l]
                                    for w in WIDTH
                                        for l in range(len(layouts_data['grades'][w]))) - DEMANDS[c][p][s])
                                            for s in DEMANDS[c][p]} for p in range(len(DEMANDS[c]))]
        }
    return output_json


def add_operating_results(input_json, results_json):
    operating_results = {}
    operating_results['spreads'] = []
    for width in results_json['results']['spreads']:
        for spread in results_json['results']['spreads'][width]:
            spread_model = {
                'cut_order_fabric_id': input_json['fabric']['cut_order_fabric_id'],
                'width': int(width),
                'colorways': [
                    {'id': color_id, 'layers': spread['colorways'][color_id]} for color_id in spread['colorways']
                ],
                'grades': [
                    {
                        "cut_order_pattern_id": input_json['patterns'][i]['cut_order_pattern_id'],
                        "grade": size,
                        "quantity": grade[size]
                    } for i, grade in enumerate(spread['grades']) for size in grade if grade[size]>0
                ]
            }

            operating_results['spreads'].append(spread_model)

    results_json['operating_results'] = operating_results
    return results_json


def report(input_json, optimization_data, layouts_data):
    """Report.

    Args:
        input_json (dict): Input Json file.
        optimization_data (dict): Info and Variables of optimization.
        layouts_data (dict): grid data.

    Returns:
        dict: Results.
    """

    WIDTH =  [width['width'] for width in input_json['fabric']['widths']]
    DEMANDS = input_json['demands']
    #Settings
    overproduction_percentage = input_json['settings']['overproduction_percentage']
    solver_time_limit = input_json['settings']['solver_time_limit']
    cost_overproduction_allowed = input_json['settings']['cost_overproduction_allowed']
    speed = input_json['settings']['speed']
    #Fabric
    max_layers = input_json['fabric']['max_layers']
    price_per_linear_meter = [width['cost_per_meter'] for width in input_json['fabric']['widths']] #W
    #Cost Operations
    cost_per_cut_meter = input_json['settings']['cost_cut']*layouts_data['price_fabric_meter']
    cost_setup = input_json['settings']['cost_setup']*layouts_data['price_fabric_meter']

    # print(15*'-'+'ENTRADA'+15*'-')
    # print(f'N° maximo de camadas: {max_layers}')
    # print(f'Largura de: {WIDTH} mm')
    # print(f'Satisfazer a demanda de:')
    # print(json.dumps(DEMANDS, indent=2, ensure_ascii=False))
    # print(f'Considerando o excesso de: {overproduction_percentage}')
    # print(f'Limite de tempo: {solver_time_limit} (s)')

    # print()
    # print(f'''Inicialmente encontrando {len(input_json['spread_results'])} possibidades de grades''')
    # print(f'Utilizando as possibidades de grades:')
    # for w in WIDTH:
    #     print(f'''\tNa largura {w}: {len(layouts_data['grades'][w])} possibilidades''')
        
    # print()
    # print(15*'-'+'PARAMETROS e OBJETIVO'+15*'-')
    # print(f'Proporção de excesso permitido de peças: {cost_overproduction_allowed:.2f}')
    # print(f'Custo do tecido (por largura): {price_per_linear_meter} (R$/m)')
    # print(f'Custo de tempo do corte/risco relacionado ao perimetro de corte/risco: {cost_per_cut_meter:.2f} (R$/m)')
    # print(f'Custo de setup da mesa: {cost_setup:.2f} (R$)')
    # print(f'Velocidade: {speed:.2f}')

    # print()
    # print(15*'-'+'RESULTADO'+15*'-')
    # for w in WIDTH:
    #     if sum(optimization_data['variables']['z'][w][l]
    #            for l in range(len(layouts_data['grades'][w])))>0.0:
    #         print(f'''Deve preparar a mesa, com largura {w} mm:''')
    #         for l in range(len(layouts_data['grades'][w])):
    #             if optimization_data['variables']['z'][w][l]>0.0:
    #                 print(f'''\t{int(optimization_data['variables']['z'][w][l])} vez(es) da grade {layouts_data['grades'][w][l]} totalizando {int(sum(optimization_data['variables']['x'][c][w][l] for c in DEMANDS))} camadas''')
    #                 for c in DEMANDS:
    #                     if optimization_data['variables']['x'][c][w][l]>0.0:
    #                         print(f'''\t\t{c} = {int(optimization_data['variables']['x'][c][w][l])} camadas''')

    # print()
    # print('Total de itens produzidos:')
    # for c in DEMANDS:
    #     print(f'\tda variante/cor {c}')
    #     for p in range(len(DEMANDS[c])):
    #         print(f'''\t\tdo molde N° {p} - {input_json['patterns'][p]['name']}''')
    #         for s in DEMANDS[c][p]:
    #             production = sum(layouts_data['grades'][w][l][p][s]*\
    #                              optimization_data['variables']['x'][c][w][l]
    #                                 for w in WIDTH
    #                                     for l in range(len(layouts_data['grades'][w])))
    #             print(f'''\t\t\tProdução do item {s}: {int(production)} / {DEMANDS[c][p][s]} -> [excesso: {int(production - DEMANDS[c][p][s])}]''')

    # print()
    # print(15*'-'+'RESULTADO EM NUMEROS'+15*'-')
    # print(f'''Status: {optimization_data['status']}''')
    # print(f'''Objetivo: {optimization_data['objective']:.4f}''')
    # print(f'''Tempo de otimização: {optimization_data['runtime']:.2f} segundos''')

    # print()
    # cost_overproduction_allowed_value = cost_overproduction_allowed*\
    #                                     sum(optimization_data['variables']['u'][c][p][s]*layouts_data['cost_piece'][p][s] 
    #                                         for c in DEMANDS
    #                                         for p in range(len(DEMANDS[c]))
    #                                         for s in DEMANDS[c][p])
    # print(f'''Custo do excesso: {cost_overproduction_allowed_value:.2f} R$ -> ({100*cost_overproduction_allowed_value/optimization_data['objective']:.2f} %)''')
    
    # cost_fabric_value = sum(price_per_linear_meter[id_w]*layouts_data['length'][w][l]*\
    #                         sum(optimization_data['variables']['x'][c][w][l] for c in DEMANDS)
    #                         for id_w,w in enumerate(WIDTH)
    #                         for l in range(len(layouts_data['grades'][w])))
    # print(f'''Custo do tecido: {cost_fabric_value:.2f} R$ -> ({100*cost_fabric_value/optimization_data['objective']:.2f} %)''')

    # cost_cut_value = (1+speed)*cost_per_cut_meter*\
    #                 sum(layouts_data['perimeter'][w][l]*\
    #                 optimization_data['variables']['z'][w][l]
    #                 for w in WIDTH
    #                 for l in range(len(layouts_data['grades'][w])))
    # print(f'''Custo do corte: {cost_cut_value:.2f} R$ -> ({100*cost_cut_value/optimization_data['objective']:.2f} %)''')

    # cost_setup_value = (1+speed)*cost_setup*\
    #                     sum(optimization_data['variables']['z'][w][l]
    #                     for w in WIDTH
    #                     for l in range(len(layouts_data['grades'][w])))
    # print(f'''Custo do setup: {cost_setup_value:.2f} R$ -> ({100*cost_setup_value/optimization_data['objective']:.2f} %)''')

    # print()

    # for c in DEMANDS:
    #     print(f'Para a variante/cor {c}:')
    #     ex1= [{s:optimization_data['variables']['u'][c][p][s]
    #            for s in DEMANDS[c][p]}
    #             for p in range(len(DEMANDS[c]))]
    #     print(f'''\tCusto de excesso permitido: {cost_overproduction_allowed}*{ex1} = {cost_overproduction_allowed*sum(optimization_data['variables']['u'][c][p][s]*layouts_data['cost_piece'][p][s] for p in range(len(DEMANDS[c])) for s in DEMANDS[c][p]):.2f} (R$)''')

    # print()
    # for id_w,w in enumerate(WIDTH):
    #     if sum(optimization_data['variables']['z'][w][l]
    #            for l in range(len(layouts_data['grades'][w])))>0.0:
    #         print(f'''Custo do tecido (camadas) utilizando largura de {w} mm:''')
    #         for l in range(len(layouts_data['grades'][w])):
    #             if optimization_data['variables']['z'][w][l]>0.0:
    #                 print(f'''\t{price_per_linear_meter[id_w]:.2f}*{layouts_data['length'][w][l]:.2f}*{sum(optimization_data['variables']['x'][c][w][l] for c in DEMANDS)} = {price_per_linear_meter[id_w]*layouts_data['length'][w][l]*sum(optimization_data['variables']['x'][c][w][l] for c in DEMANDS):.2f} (R$) -> {layouts_data['grades'][w][l]}''')

    # print()
    # for w in WIDTH:
    #     if sum(optimization_data['variables']['z'][w][l]
    #            for l in range(len(layouts_data['grades'][w])))>0.0:
    #         print(f'''Custo de tempo de corte/risco (perimetro) utilizando largura de {w} mm:''')
    #         for l in range(len(layouts_data['grades'][w])):
    #             if optimization_data['variables']['z'][w][l]>0.0:
    #                 print(f'''\t{(1+speed)*cost_per_cut_meter:.2f}*{layouts_data['perimeter'][w][l]:.2f}*{optimization_data['variables']['z'][w][l]} = {(1+speed)*cost_per_cut_meter*layouts_data['perimeter'][w][l]*optimization_data['variables']['z'][w][l]:.2f} (R$) -> {layouts_data['perimeter'][w][l]:.2f} m (individual)''')

    # print()
    # print(f'''Custo de setup (preparo da mesa): {(1+speed)*cost_setup:.2f}*{sum(optimization_data['variables']['z'][w][l] for w in WIDTH for l in range(len(layouts_data['grades'][w])))} = {(1+speed)*cost_setup*sum(optimization_data['variables']['z'][w][l] for w in WIDTH for l in range(len(layouts_data['grades'][w]))):.2f} (R$)''')
    # print()


def grids_optimization_pulp(input_json):
    """Grids Optimization using Pulp.

    Args:
        input_json (dict): Input Json file.

    Returns:
        dict: Results.
    """

    start_time = time.time()
    WIDTH = [width['width'] for width in input_json['fabric']['widths']] #W (width)
    DEMANDS = input_json['demands'] #CxPxS (colors x models x sizes)
    GRADES_BASE = [list(grade.keys())
                    for grade in input_json['demands'][next(iter(input_json['demands']))]]
    
    #Layouts (L)
    GRADES = {} #WxLxPxS
    LENGTH = {} #WxL (mm) -> (m)
    SAVING = {} #WxL
    PERIMETER = {} #WxL (mm)  -> (m)
    for width in WIDTH:
        GRADES[width] = []
        LENGTH[width] = []
        SAVING[width] = []
        PERIMETER[width] = []
        for layout in input_json['layouts'][width]:
            GRADES[width].append(layout['grades'])
            LENGTH[width].append(1e-3 * layout['spread_length'])
            SAVING[width].append(layout['saving'])
            PERIMETER[width].append(1e-3 * layout['total_perimeter'])
    
    #Settings
    overproduction_percentage = input_json['settings']['overproduction_percentage']
    optimality_gap = input_json['settings']['optimality_gap']
    solver_time_limit = input_json['settings']['solver_time_limit']
    cost_overproduction_allowed = input_json['settings']['cost_overproduction_allowed']
    speed = input_json['settings']['speed']
    #Fabric
    max_layers = input_json['fabric']['max_layers']
    price_per_linear_meter = [width['cost_per_meter'] for width in input_json['fabric']['widths']] #W

    price_fabric_meter = np.mean([1e3/int(WIDTH[w])*price_per_linear_meter[w] for w in range(len(WIDTH))]) #R$/m2
    COST_PIECE = [{size:sum(1e-6*panel['quantity']*panel['area']*price_fabric_meter
                            for panel in input_json['patterns'][i]['grades'][size]['panels'])
                            for size in grade}
                            for i,grade in enumerate(GRADES_BASE)]

    #Cost Operations
    cost_per_cut_meter = input_json['settings']['cost_cut']*price_fabric_meter
    cost_setup = input_json['settings']['cost_setup']*price_fabric_meter

    layouts_data = {
        'grades': GRADES,
        'length': LENGTH,
        'saving': SAVING,
        'perimeter': PERIMETER,
        'cost_piece': COST_PIECE,
        'price_fabric_meter': price_fabric_meter
    }


    #Modelo Linear
    model = pulp.LpProblem('MPlanGrade', sense=pulp.LpMinimize)
    #x[c][w][l] - integer: Quantidade do grades/layout 'l' cortado no tecido de variante/cor 'c' e largura 'w'.
    x = pulp.LpVariable.dicts(name='cut',indices=((c,w,l)
                                                  for c in DEMANDS
                                                  for w in WIDTH
                                                  for l in range(len(GRADES[w]))), lowBound=0, cat=pulp.LpInteger)
    #u[c][p][s] - Excesso (dentro da margem) da peça 'p' de tamanho 's' de vairante/cor 'c'.
    u = pulp.LpVariable.dicts(name='margem', indices=((c,p,s)
                                                      for c in DEMANDS
                                                      for p in range(len(DEMANDS[c]))
                                                      for s in DEMANDS[c][p]),lowBound=0, cat=pulp.LpInteger)
    #z[w][l] - Prepaparacao da mesa utilizando o layout/grade 'l' na largura 'w'.
    z = pulp.LpVariable.dicts(name='preparation',indices=((w,l)
                                                          for w in WIDTH
                                                          for l in range(len(GRADES[w]))), lowBound=0, cat=pulp.LpInteger)

    # Add Constraints
    #Respeitar as Demandas/cores de cada Tamanho
    for c in DEMANDS:
        for p in range(len(DEMANDS[c])):
            for s in DEMANDS[c][p]:
               model.addConstraint(pulp.lpSum(GRADES[w][l][p][s]*x[(c,w,l)]
                                       for w in WIDTH
                                       for l in range(len(GRADES[w]))) >= DEMANDS[c][p][s], name=f'demanda_{c}_{p}_{s}')

    #Excesso da demanda
    for c in DEMANDS:
        for p in range(len(DEMANDS[c])):
            for s in DEMANDS[c][p]: 
                model.addConstraint(pulp.lpSum(GRADES[w][l][p][s]*x[(c,w,l)]
                                        for w in WIDTH
                                        for l in range(len(GRADES[w]))) <= DEMANDS[c][p][s] + u[(c,p,s)], name=f'demanda_excesso_{c}_{p}_{s}')
    
    #Excesso da soma de todas as peças
    for c in DEMANDS:
        for p in range(len(DEMANDS[c])):
            model.addConstraint(pulp.lpSum(u[(c,p,s)]
                                    for s in DEMANDS[c][p]) <= pulp.lpSum(DEMANDS[c][p].values())*overproduction_percentage, name=f'excesso_soma_{c}_{p}')

    #Prepaparacao da mesa
    for w in WIDTH:
        for l in range(len(GRADES[w])):
            model.addConstraint(pulp.lpSum(x[(c,w,l)]
                                    for c in DEMANDS) <= z[(w,l)]*max_layers, name=f'preparacao1_{w}_{l}')

    obj = (
        #PENALIDADE DE EXCESSO PERMITIDO (PEÇAS)
        + cost_overproduction_allowed*pulp.lpSum(COST_PIECE[p][s]*u[(c,p,s)]
                                          for c in DEMANDS
                                          for p in range(len(DEMANDS[c]))
                                          for s in DEMANDS[c][p]) 
        #CUSTO DE USO DO TECIDO / DESPERDICIO (AREA DE DESPERDICIO)
        + pulp.lpSum(price_per_linear_meter[id_w]*LENGTH[w][l]*pulp.lpSum(x[(c,w,l)]
                                                                   for c in DEMANDS)
                                                                   for id_w,w in enumerate(WIDTH)
                                                                   for l in range(len(GRADES[w])))
        #CUSTO DE CORTE/RISCO (PERIMETRO)
        + (1+speed)*cost_per_cut_meter*pulp.lpSum(PERIMETER[w][l]*z[(w,l)]
                                 for w in WIDTH
                                 for l in range(len(GRADES[w]))) 
        # PREPARO DA MESA/Enfesto
        + (1+speed)*cost_setup*pulp.lpSum(z[(w,l)]
                         for w in WIDTH
                         for l in range(len(GRADES[w])))
    )

    model.setObjective(obj)

    # print('Preparo das variaveis e restricoes (s)', np.round(time.time() - start_time, 4))
    # print('Iniciando a otimizacao!')

    # Otimizacao
    start_time_solve = time.time()
    model.solve(pulp.PULP_CBC_CMD(msg=False, timeLimit=solver_time_limit, gapRel=optimality_gap))
    runtime = time.time()-start_time_solve
    status = pulp.LpStatus[model.status]
    print(f'Status: {status}, resolvido em: {runtime:.2f} segundos')

    X = {c:{w:[x[(c,w,l)].value()
               for l in range(len(GRADES[w]))]
               for w in WIDTH}
               for c in DEMANDS}
    Z = {w:[z[(w,l)].value()
            for l in range(len(GRADES[w]))]
            for w in WIDTH}
    U = {c:[{s:u[(c,p,s)].value()
             for s in DEMANDS[c][p]}
             for p in range(len(DEMANDS[c]))]
             for c in DEMANDS}
    
    optimization_data = {
        'runtime': runtime,
        'status': status,
        'objective': model.objective.value(),
        'variables': {
            'x': X,
            'z': Z,
            'u': U
        }
    }

    report(input_json=input_json,
            optimization_data=optimization_data,
            layouts_data=layouts_data)

    results = output_json(input_json=input_json,
                          optimization_data=optimization_data,
                          layouts_data=layouts_data)
    
    return add_operating_results(input_json=input_json,
                                 results_json=results)

