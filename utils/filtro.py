import numpy as np
import pulp
import time
import json
from utils.class_validation import FilterConfig


def get_divisors(n):
    divs = []
    for i in range(1, int(np.sqrt(n)) + 1):
        if n % i == 0:
            divs.append(i)
            if i != n // i:
                divs.append(n // i)
    return sorted(divs)


def get_multi_grades(scalar, grades, length_est, settings):
    max_length = settings['max_length']
    divisors = get_divisors(scalar)
    multi_grades = []

    for scalar_option in divisors[1:]:
        if (scalar_option*length_est > max_length):
            break
        multi_grades.append(
            (scalar_option,[{s:scalar_option*size for s,size in grade.items()} for grade in grades])
        )
    return multi_grades


def get_area_individual(candidate, input_json):
    area_total = [{size:sum(number*panel['quantity']*panel['area']
                            for panel in input_json['patterns'][i]['grades'][size]['panels'])
                            for size,number in grade.items()}
                            for i,grade in enumerate(candidate)]         
    return area_total


def get_area(candidate, input_json):
    area_total = sum(number*panel['quantity']*panel['area']
                        for i,grade in enumerate(candidate)
                            for size,number in grade.items()
                                for panel in input_json['patterns'][i]['grades'][size]['panels'])
    return area_total


def length_estimate(candidate, input_json):
    widths = [width['width'] for width in input_json['fabric']['widths']]
    width_max = max(widths)
    area = get_area(candidate, input_json)
    saving = 0.95
    length = area/(saving*width_max)
    return length


def diophantine_double_decomposition_milp(target, S_max, settings):
    solver_time_limit = settings['solver_time_limit']
    optimality_gap = settings['optimality_gap']

    K = 2
    B = int(np.ceil(np.log2(S_max + 1)))
    M = S_max

    model = pulp.LpProblem("Sistema_Diofantino_Vetorial", pulp.LpMinimize)

    # Variáveis
    v = pulp.LpVariable.dicts(name='vetor', indices=((k,i,s) for k in range(K) for i,grade in enumerate(target) for s in grade.keys()), lowBound=0, cat=pulp.LpInteger)
    z = pulp.LpVariable.dicts(name='componente_binario', indices=((k,b) for k in range(K) for b in range(B)), lowBound=0, cat=pulp.LpBinary)
    w = pulp.LpVariable.dicts(name='produto_vetor_escalar', indices=((k,b,i,s) for k in range(K) for b in range(B) for i,grade in enumerate(target) for s in grade.keys()), lowBound=0, cat=pulp.LpInteger)

    # Restrições diofantinas
    for i,grade in enumerate(target):
        for s in grade.keys():
            model.addConstraint(pulp.lpSum((2**b) * w[(k,b,i,s)] for k in range(K) for b in range(B)) ==  target[i][s], name=f'diofantina_{i}_{s}')

    # Linearização: w = z * v
    for k in range(K):
        for b in range(B):
            for i,grade in enumerate(target):
                for s in grade.keys():
                    model.addConstraint(w[(k,b,i,s)] <= v[(k,i,s)], name=f'produto1_{k}_{b}_{i}_{s}')
                    model.addConstraint(w[(k,b,i,s)] <= M*z[(k,b)], name=f'produto2_{k}_{b}_{i}_{s}')
                    model.addConstraint(w[(k,b,i,s)] >= v[(k,i,s)] - M*(1-z[(k,b)]), name=f'produto3_{k}_{b}_{i}_{s}')

    # Função objetivo: soma coletiva dos vetores
    obj = pulp.lpSum(v[(k,i,s)] for k in range(K) for i,grade in enumerate(target) for s in grade.keys())

    model.setObjective(obj)

    # Optimize
    start_time_solve = time.time()
    model.solve(pulp.PULP_CBC_CMD(msg=False, timeLimit=solver_time_limit, gapRel=optimality_gap))
    # print(f'Otimizando (decomposicao): {target}')
    runtime = time.time()-start_time_solve
    status = pulp.LpStatus[model.status]
    # print(f'\tStatus: {status}, resolvido em: {runtime:.2f} segundos') 
    objValue = model.objective.value()
    # print(f'\tObjetivo: {objValue:.2f}')

    vector = [[{s:int(v[(k,i,s)].value()) for s in grade.keys()} for i,grade in enumerate(target)] for k in range(K)]
    scalar = [sum(int((2**b) * z[(k,b)].value()) for b in range(B)) for k in range(K)]

    optimization_data= {
        'runtime': np.round(runtime,2),
        'status': status,
        'objective': int(objValue),
        'variables': {
            'vector': vector,
            'scalar': scalar,
            'rebuilding': [{s:sum(int(scalar[k] * vector[k][i][s]) for k in range(K)) for s in grade.keys()} for i,grade in enumerate(target)]
        }
    }

    return optimization_data


def diophantine_half_decomposition_milp(target, vector_base, S_max, settings):
    solver_time_limit = settings['solver_time_limit']
    optimality_gap = settings['optimality_gap']
    
    B = int(np.ceil(np.log2(S_max + 1)))
    M = S_max

    model = pulp.LpProblem("Aproximacao_Diofantina_Metade", pulp.LpMinimize)

    # Variáveis
    v = pulp.LpVariable.dicts(name='vetor', indices=((i,s) for i,grade in enumerate(target) for s in grade.keys()), lowBound=0, cat=pulp.LpInteger)
    z = pulp.LpVariable.dicts(name='componente_binario', indices=((b) for b in range(B)), lowBound=0, cat=pulp.LpBinary)
    w = pulp.LpVariable.dicts(name='produto_vetor_escalar', indices=((b,i,s) for b in range(B) for i,grade in enumerate(target) for s in grade.keys()), lowBound=0, cat=pulp.LpInteger)
    c = pulp.LpVariable('escalar', lowBound=0, cat=pulp.LpInteger)

    # Restrições de cobertura
    for i,grade in enumerate(target):
        for s in grade.keys():
            model.addConstraint(pulp.lpSum((2**b) * w[(b,i,s)] for b in range(B)) + c*vector_base[i][s] ==  target[i][s], name=f'diofantina_{i}_{s}')

    # Linearização w = z * v
    for b in range(B):
        for i,grade in enumerate(target):
            for s in grade.keys():
                model.addConstraint(w[(b,i,s)] <= v[(i,s)], name=f'produto1_{b}_{i}_{s}')
                model.addConstraint(w[(b,i,s)] <= M*z[b], name=f'produto2_{b}_{i}_{s}')
                model.addConstraint(w[(b,i,s)] >= v[(i,s)] - M*(1-z[b]), name=f'produto3_{b}_{i}_{s}')


    # Objetivo: minimizar vetor base total
    obj = pulp.lpSum(v[(i,s)] for i,grade in enumerate(target) for s in grade.keys())

    model.setObjective(obj)

    # Optimize
    start_time_solve = time.time()
    model.solve(pulp.PULP_CBC_CMD(msg=False, timeLimit=solver_time_limit, gapRel=optimality_gap))
    # print(f'Otimizando (resto): {target}')
    runtime = time.time()-start_time_solve
    status = pulp.LpStatus[model.status]
    # print(f'\tStatus: {status}, resolvido em: {runtime:.2f} segundos') 
    objValue = model.objective.value()
    # print(f'\tObjetivo: {objValue:.2f}')

    vector = [{s:int(v[(i,s)].value()) for s in grade.keys()} for i,grade in enumerate(target)]
    scalar = sum(int((2**b) * z[b].value()) for b in range(B))
    
    optimization_data= {
        'runtime': np.round(runtime,2),
        'status': status,
        'objective': int(objValue),
        'variables': {
            'vector': vector,
            'scalar': scalar,
            'scalar_base': int(c.value()),
            'rebuilding': [{s:int(scalar * vector[i][s] + c.value()*vector_base[i][s]) for s in grade.keys()} for i,grade in enumerate(target)]
        }
    }

    return optimization_data


def diophantine_single_decomposition_milp(target, S_max, settings):
    solver_time_limit = settings['solver_time_limit']
    optimality_gap = settings['optimality_gap']
    overproduction_percentage = max(0.05, settings['overproduction_percentage'])

    B = int(np.ceil(np.log2(S_max + 1)))
    M = S_max

    model = pulp.LpProblem("Aproximacao_Diofantina_Excesso", pulp.LpMinimize)

    # Variáveis
    v = pulp.LpVariable.dicts(name='vetor', indices=((i,s) for i,grade in enumerate(target) for s in grade.keys()), lowBound=0, cat=pulp.LpInteger)
    z = pulp.LpVariable.dicts(name='componente_binario', indices=((b) for b in range(B)), lowBound=0, cat=pulp.LpBinary)
    w = pulp.LpVariable.dicts(name='produto_vetor_escalar', indices=((b,i,s) for b in range(B) for i,grade in enumerate(target) for s in grade.keys()), lowBound=0, cat=pulp.LpInteger)
    e = pulp.LpVariable.dicts(name='excesso', indices=((i,s) for i,grade in enumerate(target) for s in grade.keys()), lowBound=0, cat=pulp.LpInteger)

    # Restrições de cobertura
    for i,grade in enumerate(target):
        for s in grade.keys():
            model.addConstraint(pulp.lpSum((2**b) * w[(b,i,s)] for b in range(B)) - e[(i,s)] ==  target[i][s], name=f'diofantina_{i}_{s}')

    # Linearização w = z * v
    for b in range(B):
        for i,grade in enumerate(target):
            for s in grade.keys():
                model.addConstraint(w[(b,i,s)] <= v[(i,s)], name=f'produto1_{b}_{i}_{s}')
                model.addConstraint(w[(b,i,s)] <= M*z[b], name=f'produto2_{b}_{i}_{s}')
                model.addConstraint(w[(b,i,s)] >= v[(i,s)] - M*(1-z[b]), name=f'produto3_{b}_{i}_{s}')

    #Limite do excesso
    model.addConstraint(pulp.lpSum(e[(i,s)] for i,grade in enumerate(target) for s in grade.keys()) <= overproduction_percentage*sum(sum(grade.values()) for grade in target), name=f'over') 

    # Objetivo: minimizar excesso total
    peso = 0.5*sum(len(grade.values()) for grade in target)
    obj = pulp.lpSum(v[(i,s)] + peso*e[(i,s)] for i,grade in enumerate(target) for s in grade.keys())

    model.setObjective(obj)

    # Optimize
    start_time_solve = time.time()
    model.solve(pulp.PULP_CBC_CMD(msg=False, timeLimit=solver_time_limit, gapRel=optimality_gap))
    # print(f'Otimizando (unico): {target}')
    runtime = time.time()-start_time_solve
    status = pulp.LpStatus[model.status]
    # print(f'\tStatus: {status}, resolvido em: {runtime:.2f} segundos') 
    objValue = model.objective.value()
    # print(f'\tObjetivo: {objValue:.2f}')

    vector = [{s:int(v[(i,s)].value()) for s in grade.keys()} for i,grade in enumerate(target)]
    scalar = sum(int((2**b) * z[b].value()) for b in range(B))
    
    opt_data_single= {
        'runtime': np.round(runtime,2),
        'status': status,
        'objective': int(objValue),
        'variables': {
            'vector': [[vector]],
            'scalar': [[scalar]],
            'error': sum(int(e[(i,s)].value()) for i,grade in enumerate(target) for s in grade.keys()),
            'rebuilding': [{s:scalar * vector[i][s] for s in grade.keys()} for i,grade in enumerate(target)],
            'leftover': [{s:scalar * vector[i][s] - target[i][s] for s in grade.keys()} for i,grade in enumerate(target)]
        }
    }

    if opt_data_single['variables']['error'] == 0:
        return opt_data_single

    opt_data_half = diophantine_half_decomposition_milp(target=target,
                                                        vector_base=vector,
                                                        S_max=S_max,
                                                        settings=settings)
    
    optimization_data= {
        'runtime': opt_data_half['runtime'] + opt_data_single['runtime'],
        'status': status,
        'objective': [opt_data_half['objective'], opt_data_single['objective']],
        'variables': {
            'vector': [[vector, opt_data_half['variables']['vector']], [vector]],
            'scalar': [[opt_data_half['variables']['scalar_base'], opt_data_half['variables']['scalar']], [scalar]],
            'rebuilding': opt_data_single['variables']['rebuilding'],
            'leftover': opt_data_single['variables']['leftover']
        }
    }
    
    return optimization_data


def unitary_decomposition_milp(target, area, settings):
    solver_time_limit = settings['solver_time_limit']
    optimality_gap = settings['optimality_gap']

    model = pulp.LpProblem("Decomposicao_Unitaria", pulp.LpMinimize)

    # Variáveis
    u = pulp.LpVariable.dicts(name='vetor', indices=((i,s) for i,grade in enumerate(target) for s in grade.keys()), lowBound=0, cat=pulp.LpBinary)
    d = pulp.LpVariable('diferenca', lowBound=0, cat=pulp.LpContinuous)

    # Restrições de igualdade
    for i,grade in enumerate(target):
        for s in grade.keys():
            model.addConstraint(u[(i,s)] <= target[i][s], name=f'igualdade_{i}_{s}')
    
    # Restricoes do Equilibrio
    peso_u = pulp.lpSum(area[i][s]*u[(i,s)] for i,grade in enumerate(target) for s in grade.keys())
    peso_v = pulp.lpSum(area[i][s]*(target[i][s] - u[(i,s)]) for i,grade in enumerate(target) for s in grade.keys())
    model.addConstraint(d >= peso_u - peso_v, name=f'diferenca_pos')
    model.addConstraint(d >= peso_v - peso_u, name=f'diferenca_neg')
    
    # Objetivo
    obj = d
    model.setObjective(obj)

    # Optimize
    start_time_solve = time.time()
    model.solve(pulp.PULP_CBC_CMD(msg=False, timeLimit=solver_time_limit, gapRel=optimality_gap))
    # print(f'Otimizando (unitario): {target}')
    runtime = time.time()-start_time_solve
    status = pulp.LpStatus[model.status]
    # print(f'\tStatus: {status}, resolvido em: {runtime:.2f} segundos') 
    objValue = model.objective.value()
    # print(f'\tObjetivo: {objValue:.2f}')

    u_vector = [{s:int(u[(i,s)].value()) for s in grade.keys()} for i,grade in enumerate(target)]
    v_vector = [{s:int(target[i][s] - u[(i,s)].value()) for s in grade.keys()} for i,grade in enumerate(target)]

    sum_u = sum(area[i][s]*u_vector[i][s] for i,grade in enumerate(target) for s in grade.keys())
    sum_v = sum(area[i][s]*v_vector[i][s] for i,grade in enumerate(target) for s in grade.keys())

    optimization_data= {
        'runtime': np.round(runtime,2),
        'status': status,
        'objective': int(objValue),
        'variables': {
            'vector': [u_vector, v_vector],
            'weights': [sum_u, sum_v],
            'difference': abs(sum_u - sum_v)
        }
    }

    return optimization_data


def expand_multiple(candidate_parent, candidate_child, length_est, settings, candidate_grades, tree):
    candidate_grades.append(candidate_child[1])
    for scalar_multi, vector_multi in get_multi_grades(scalar=candidate_child[0],
                                                        grades=candidate_child[1],
                                                        length_est=length_est,
                                                        settings=settings):
        if vector_multi != candidate_parent[1]:
            candidate_grades.append(vector_multi)
            tree.append([candidate_parent, [int(candidate_child[0]/scalar_multi), vector_multi], {'type':'multiple', 'color':'green'}])
    return candidate_grades, tree


def expand_decomposition(candidate, queue, queue_unitary, memory, opt_memory_decomposition, candidate_grades, tree, input_json):
    max_length = input_json['fabric']['max_length']
    settings = input_json['settings'].copy()
    settings.update({'max_length': max_length})

    S_max = max(max(grade.values()) for grade in candidate[1])
    #Dois vetores
    if not candidate[1] in opt_memory_decomposition['grades']:
        opt_data = diophantine_double_decomposition_milp(target=candidate[1],
                                                            S_max=S_max,
                                                            settings=settings)
        vector = opt_data['variables']['vector']
        scalar = opt_data['variables']['scalar']
        opt_memory_decomposition['grades'].append(candidate[1])
        opt_memory_decomposition['result'].append({'vector':vector,
                                                   'scalar':scalar})
    else:
        ind_element = opt_memory_decomposition['grades'].index(candidate[1])
        vector = opt_memory_decomposition['result'][ind_element]['vector']
        scalar = opt_memory_decomposition['result'][ind_element]['scalar']

    if sum(scalar) != 1:
        for i in range(len(vector)):
            sum_total = sum(sum(grade.values()) for grade in vector[i])
            if (sum_total < 1) or ([candidate[0]*scalar[i],vector[i]] in memory):
                continue
            memory.append([candidate[0]*scalar[i],vector[i]])
            
            length_est = length_estimate(candidate=vector[i], input_json=input_json)
            if (length_est > max_length/2):
                if check_unitary(vector[i]):
                    queue_unitary.append([candidate[0]*scalar[i], vector[i]])
                else:
                    queue.append([candidate[0]*scalar[i], vector[i]])
            
            if (length_est <= max_length):
                (candidate_grades,
                 tree) = expand_multiple(candidate_parent=candidate,
                                         candidate_child=[candidate[0]*scalar[i], vector[i]],
                                         length_est=length_est,
                                         settings=settings,
                                         candidate_grades=candidate_grades,
                                         tree=tree)

            if check_unitary(vector[i]):
                tree.append([candidate, [candidate[0]*scalar[i], vector[i]], {'type':'unitary', 'color':'gray'}])
            else:  
                tree.append([candidate, [candidate[0]*scalar[i], vector[i]], {'type':'decomposition', 'color':'blue'}])
    
    return queue, queue_unitary, memory, opt_memory_decomposition, candidate_grades, tree


def expand_single(candidate, queue_both, queue_decomposition, queue_unitary, memory, opt_memory_single, candidate_grades, tree, input_json):
    max_length = input_json['fabric']['max_length']
    settings = input_json['settings'].copy()
    settings.update({'max_length': max_length})
    
    S_max = max(max(grade.values()) for grade in candidate[1])
    #Vetor unico
    if not candidate[1] in opt_memory_single['grades']:
        opt_data = diophantine_single_decomposition_milp(target=candidate[1],
                                                        S_max=S_max,
                                                        settings=settings)
        vector = opt_data['variables']['vector']
        scalar = opt_data['variables']['scalar']
        opt_memory_single['grades'].append(candidate[1])
        opt_memory_single['result'].append({'vector':vector,
                                            'scalar':scalar})
    else:
        ind_element = opt_memory_single['grades'].index(candidate[1])
        vector = opt_memory_single['result'][ind_element]['vector']
        scalar = opt_memory_single['result'][ind_element]['scalar']

    for k in range(len(vector)):
        if sum(scalar[k]) != 1:
            for i in range(len(vector[k])):
                sum_total = sum(sum(grade.values()) for grade in vector[k][i])
                if (sum_total < 1) or ([candidate[0]*scalar[k][i],vector[k][i]] in memory):
                    continue

                memory.append([candidate[0]*scalar[k][i],vector[k][i]])
                length_est = length_estimate(candidate=vector[k][i], input_json=input_json)

                if (length_est > max_length/2):
                    if check_unitary(vector[k][i]):
                        queue_unitary.append([candidate[0]*scalar[k][i], vector[k][i]])
                    else:
                        if k == 0:
                            queue_both.append([candidate[0]*scalar[k][i], vector[k][i]])
                        else:
                            queue_decomposition.append([candidate[0]*scalar[k][i], vector[k][i]])
                
                if (length_est <= max_length):
                    (candidate_grades,
                    tree) = expand_multiple(candidate_parent=candidate,
                                            candidate_child=[candidate[0]*scalar[k][i], vector[k][i]],
                                            length_est=length_est,
                                            settings=settings,
                                            candidate_grades=candidate_grades,
                                            tree=tree)
                
                if check_unitary(vector[k][i]):
                    tree.append([candidate, [candidate[0]*scalar[k][i], vector[k][i]], {'type':'unitary', 'color':'gray'}])
                else:
                    if k == 0:
                        tree.append([candidate, [candidate[0]*scalar[k][i], vector[k][i]], {'type':'decomposition_single', 'color':'purple'}])
                    else: 
                        tree.append([candidate, [candidate[0]*scalar[k][i], vector[k][i]], {'type':'single', 'color':'red'}])
    
    return queue_both, queue_decomposition, queue_unitary, memory, opt_memory_single, candidate_grades, tree


def expand_unitary(candidate, queue, memory, opt_memory_unitary, candidate_grades, tree, input_json):
    max_length = input_json['fabric']['max_length']
    settings = input_json['settings'].copy()
    settings.update({'max_length': max_length})
    area = get_area_individual(candidate[1], input_json)
    
    #Unitario
    if not candidate[1] in opt_memory_unitary['grades']:
        opt_data = unitary_decomposition_milp(target=candidate[1],
                                              area=area,
                                              settings=settings)

        vector = opt_data['variables']['vector']
        scalar = [candidate[0], candidate[0]]
        opt_memory_unitary['grades'].append(candidate[1])
        opt_memory_unitary['result'].append({'vector':vector,
                                            'scalar':scalar})
    else:
        ind_element = opt_memory_unitary['grades'].index(candidate[1])
        vector = opt_memory_unitary['result'][ind_element]['vector']
        scalar = opt_memory_unitary['result'][ind_element]['scalar']

    for i in range(len(vector)):
        sum_total = sum(sum(grade.values()) for grade in vector[i])
        if (sum_total < 1) or ([scalar[i],vector[i]] in memory):
            continue
        memory.append([scalar[i],vector[i]])
        
        length_est = length_estimate(candidate=vector[i], input_json=input_json)
        if (length_est > max_length/2):
            queue.append([scalar[i], vector[i]])
 
        if (length_est <= max_length):
            (candidate_grades,
            tree) = expand_multiple(candidate_parent=candidate,
                                        candidate_child=[scalar[i], vector[i]],
                                        length_est=length_est,
                                        settings=settings,
                                        candidate_grades=candidate_grades,
                                        tree=tree)

        tree.append([candidate, [scalar[i], vector[i]], {'type':'unitary', 'color':'gray'}])
    
    return queue, memory, opt_memory_unitary, candidate_grades, tree


def check_unitary(grades):
    return all(quantity==1 for grade in grades for quantity in grade.values() if quantity>0)


def check_equal(grades):
    list_aux = [quantity for grade in grades for quantity in grade.values() if quantity>0]
    return all(list_aux[0]==value for value in list_aux)


def completing_grades(input_json):
    DEMANDS = input_json['demands']
    # print(DEMANDS)
    max_length = input_json['fabric']['max_length']

    spread_results = []
    arvore = {} 
    for colorway, grades in DEMANDS.items():
        # print(f'VARIANTE: {colorway}')
        candidate_grades = []
        
        if check_unitary(grades):
            just_unitary = [[1,grades]]
            both = []
            just_decomposition = []
            just_single = []
        elif check_equal(grades):
            just_unitary = []
            both = []
            just_decomposition = []
            just_single = [[1,grades]]
        else:
            just_unitary = []
            both = [[1,grades]]
            just_decomposition = []
            just_single = []
        

        memory = []
        opt_memory_decomposition = {'grades':[],
                                    'result':[]}
        opt_memory_single = {'grades':[],
                             'result':[]}
        opt_memory_unitary = {'grades':[],
                              'result':[]}
        arvore[colorway] = []

        while (just_unitary) or (both) or (just_decomposition) or (just_single):
            #Aceita as duas operacoes
            if both:
                candidate_both = both.pop(0)
                #Decomposicao
                (both,
                just_unitary,
                memory,
                opt_memory_decomposition,
                candidate_grades,
                arvore[colorway]) = expand_decomposition(candidate=candidate_both,
                                                        queue=both,
                                                        queue_unitary=just_unitary,
                                                        memory=memory,
                                                        opt_memory_decomposition=opt_memory_decomposition,
                                                        candidate_grades=candidate_grades,
                                                        tree=arvore[colorway],
                                                        input_json=input_json)
 
                #Vetor unico
                (both,
                 just_decomposition,
                 just_unitary,
                 memory,
                 opt_memory_single,
                 candidate_grades,
                 arvore[colorway]) = expand_single(candidate=candidate_both,
                                                    queue_both=both,
                                                    queue_decomposition=just_decomposition,
                                                    queue_unitary=just_unitary,
                                                    memory=memory,
                                                    opt_memory_single=opt_memory_single,
                                                    candidate_grades=candidate_grades,
                                                    tree=arvore[colorway],
                                                    input_json=input_json)
               
            #Aceita apenas a operacao de dividir
            if just_decomposition:
                candidate_decomposition = just_decomposition.pop(0)
                (just_decomposition,
                 just_unitary,
                 memory,
                 opt_memory_decomposition,
                 candidate_grades,
                 arvore[colorway]) = expand_decomposition(candidate=candidate_decomposition,
                                                        queue=just_decomposition,
                                                        queue_unitary=just_unitary,
                                                        memory=memory,
                                                        opt_memory_decomposition=opt_memory_decomposition,
                                                        candidate_grades=candidate_grades,
                                                        tree=arvore[colorway],
                                                        input_json=input_json)
            
            #Apenas para simplificacao
            if just_single:
                candidate_single = just_single.pop(0)
                (both,
                 just_decomposition,
                 just_unitary,
                 memory,
                 opt_memory_single,
                 candidate_grades,
                 arvore[colorway]) = expand_single(candidate=candidate_single,
                                                    queue_both=both,
                                                    queue_decomposition=just_decomposition,
                                                    queue_unitary=just_unitary,
                                                    memory=memory,
                                                    opt_memory_single=opt_memory_single,
                                                    candidate_grades=candidate_grades,
                                                    tree=arvore[colorway],
                                                    input_json=input_json)

            #Unitario
            if just_unitary:
                candidate_unitary = just_unitary.pop(0)
                (just_unitary,
                 memory,
                 opt_memory_unitary,
                 candidate_grades,
                 arvore[colorway])= expand_unitary(candidate=candidate_unitary,
                                                   queue=just_unitary,
                                                   memory=memory,
                                                   opt_memory_unitary=opt_memory_unitary,
                                                   candidate_grades=candidate_grades,
                                                   tree=arvore[colorway],
                                                   input_json=input_json)

        length_est = length_estimate(candidate=grades, input_json=input_json) 
        if (length_est <= max_length):
            candidate_grades.append(grades)
        
        for candidate in candidate_grades:
            if not (candidate in spread_results):
                spread_results.append(candidate)

    #print(len(spread_results))
    #for branch in arvore[list(DEMANDS.keys())[0]]:
    #    print(branch[0],branch[1],branch[2]['type'])
    #plot_tree(arvore[list(DEMANDS.keys())[0]]) 
    #exit()
    return (spread_results, arvore)


def remove_panels_empty(input_json):
    for i,pattern in enumerate(input_json['patterns']):
        sizes = tuple(pattern['quantity'][next(iter(pattern['quantity']))].keys())
        input_json['patterns'][i]['grades'] = {size:pattern['grades'][size]
                                                for size in pattern['grades']
                                                    if size in sizes}
        for size in pattern['grades']:
            input_json['patterns'][i]['grades'][size]['panels'] = [panel
                                                                    for panel in pattern['grades'][size]['panels']
                                                                        if panel['quantity']>0]
    return input_json


def get_min_contour(input_json):
    min_value = float('inf')
    margem_erro_nfp = 0.98
    for pattern in input_json['patterns']:
        for size in pattern['grades']:
            for panel in pattern['grades'][size]['panels']:
                min_value = min(min_value, margem_erro_nfp*panel['width'], margem_erro_nfp*panel['height'])
    return int(min_value)


def add_data_extra(input_json):
    WIDTH = [width['width'] for width in input_json['fabric']['widths']]
    GRADES_BASE = [list(pattern['quantity'][next(iter(pattern['quantity']))].keys())
                    for pattern in input_json['patterns']]
    COLORS = set([color
                    for pattern in input_json['patterns']
                        for color in pattern['quantity'].keys()])
    n_patterns = len(input_json['patterns'])

    DEMANDS = {color:[{} for i in range(n_patterns)] for color in COLORS}
    for i,pattern in enumerate(input_json['patterns']):
        for color in COLORS:
            DEMANDS[color][i] = pattern['quantity'].get(color, {grade:0 for grade in GRADES_BASE[i]})
    
    input_json['demands'] = DEMANDS
    input_json['layouts'] = {width:[] for width in WIDTH}

    input_json = remove_panels_empty(input_json=input_json)
    input_json['settings']['contour_step'] = get_min_contour(input_json=input_json)

    return input_json


def checking_data_base_filter(input_json):
    if len(input_json['patterns'])==0:
        raise ValueError(f'patterns is empty!')
    
    for pattern in input_json['patterns']:
        if len(pattern['quantity'])==0:
            raise ValueError(f'''patterns.quantity is empty in {pattern['name']}!''')
        
        colors = tuple(pattern['quantity'].keys())
        ref_color = set(pattern['quantity'][colors[0]].keys())
        for id_color in range(1,len(colors)):
            if set(pattern['quantity'][colors[id_color]].keys()) != ref_color:
                raise ValueError(f'The quantities grades (colors in patterns.quantity) are not the same!')
    
        if not ref_color.issubset(pattern['grades'].keys()):
            raise ValueError(f'''The field patterns.grades in {pattern['name']} is missing some grades.''')
        
    return


def preparing_input(input_json):
    input_json = FilterConfig(**input_json).model_dump()
    checking_data_base_filter(input_json=input_json)
    input_json = add_data_extra(input_json=input_json)
    return input_json


def preparing_calculation(input_json):
    settings = input_json['settings']
    fabric = {'widths': input_json['fabric']['widths'], 'max_length': input_json['fabric']['max_length']}
    patterns = [{'grades': input_json['patterns'][i]['grades']} for i in range(len(input_json['patterns']))]

    cases = []
    for colorway in input_json['demands']:
        cases.append({
            'settings': settings,
            'demands': {colorway: input_json['demands'][colorway]},
            'fabric': fabric,
            'patterns': patterns 
        })
    return cases


def calculating(list_inputs):
    list_results = []
    for case in list_inputs:
        list_results.append(completing_grades(input_json=case))
    return list_results


def agregating_results(list_results, input_json):
    input_json['spread_results'] = []
    input_json['tree'] = {}
    for candidate_colorway in list_results:
        for candidate in candidate_colorway[0]:
            if not (candidate in input_json['spread_results']):
                input_json['spread_results'].append(candidate)
    
        input_json['tree'].update(candidate_colorway[1])
    return input_json


def fiter_run(input_json): 
    input_json = preparing_input(input_json=input_json)
    list_inputs = preparing_calculation(input_json=input_json)
    list_results = calculating(list_inputs=list_inputs)
    return agregating_results(list_results=list_results, input_json=input_json)


def lambda_handler(event, context):
    try:
        return preparing_input(event)
    except Exception as e:
        raise Exception(f"Error trying to filter the initial json. Details: {str(e)}")


if __name__ == "__main__":
    file_name = 'local_run/input_test.json'
    with open(file_name, "r", encoding='utf-8') as file:
        exemplo_json = json.load(file)

    start_time = time.time()
    print('INICIANDO...')
    exemplo_json = preparing_input(input_json=exemplo_json)

    list_inputs = preparing_calculation(input_json=exemplo_json)
    
    list_results = calculating(list_inputs=list_inputs) #Paralelo o que está dentro [completing_grades()]
    
    input_json = agregating_results(list_results=list_results, input_json=exemplo_json)
    
    print(f'FILTRO FINALIZADO: {round(time.time()-start_time,2)}...')