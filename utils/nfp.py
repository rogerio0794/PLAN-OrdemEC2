#import json
from shapely.geometry import Polygon
import numpy as np
import time
from shapely import affinity
from copy import deepcopy
#from grid_optimization.nfp.calculate.plot_nfp import plot


def least_bb(origin_A, bbox_A, bbox_B, list_origem_B, width=float('inf')):
    area = float('inf')
    dist = float('inf')
    for i,list_origem_B_ in enumerate(list_origem_B):
        for x,y in list_origem_B_[:-1]:
            xi=min(origin_A[0], x)
            yi=min(origin_A[1], y)
            xf=max(origin_A[0]+bbox_A[0], x+bbox_B[i][0])
            yf=max(origin_A[1]+bbox_A[1], y+bbox_B[i][1])
            area_calc = (xf-xi)
            dist_calc = np.sqrt((origin_A[0]-x)**2 + (origin_A[1]-y)**2)
            if ((yf-yi)<=width+2) and (area_calc<area or (area_calc==area and dist_calc<dist)):
                area = area_calc
                dist = dist_calc
                ref = [x,y,i]
    return ref


def minkowski_sum_details(A, B, B_details):
    points = []
    for i,b_ in enumerate(B):
        result = None
        points.append([])
        for x, y in b_.exterior.coords:
            shifted = Polygon([(xa - x, ya - y) for xa, ya in A.exterior.coords])
            result = shifted if result is None else result.union(shifted)
        if result.geom_type == "MultiPolygon":
            for pol in result.geoms:
                points[i].extend(pol.exterior.coords)
        else:
            points[i].extend(result.exterior.coords)

    points_details = []
    for i,b_ in enumerate(B_details):
        result_details = None
        points_details.append([])
        for x, y in b_.exterior.coords:
            shifted = Polygon([(xa - x, ya - y) for xa, ya in A.exterior.coords])
            result_details = shifted if result_details is None else result_details.union(shifted)
        points_details[i].extend(result_details.exterior.coords)

    new_points = [[p for p in points_details[i] if p in points[i]] for i in range(len(B))]
    return [Polygon(new_points[i]) for i in range(len(B))]


def details_polygon(polygon,step=20):
    N = len(polygon)
    pol = np.array(polygon)
    new_polygon = []
    for i,point in enumerate(pol):
        dist = np.sqrt((pol[i%N][0]-pol[(i+1)%N][0])**2 + (pol[i%N][1]-pol[(i+1)%N][1])**2)
        if dist>step:
            vec = pol[(i+1)%N]-pol[i%N]
            mag = np.linalg.norm(vec)
            vec_unit = vec/mag
            for space in np.arange(0,dist,step):
                new_polygon.append(pol[i%N]+space*vec_unit)
        else:
            new_polygon.append(pol[i%N])
    return np.array(new_polygon)


def unir(poligonos):
    bounds = poligonos.geoms[1].bounds
    centroide = ((bounds[2]+bounds[0])/2, (bounds[3]+bounds[1])/2)
    result = poligonos.geoms[0].union(Polygon([x+1e-4*(x-centroide[0])/abs(x-centroide[0]),
                                               y+1e-4*(y-centroide[1])/abs(y-centroide[1])]
                                                for x,y in poligonos.geoms[1].exterior.coords[:-1]))
    return result


def nfp(dict_input_nfp, input_json):
    grades = dict_input_nfp['grades']
    shape_panels = dict_input_nfp['panels']
    width_max = dict_input_nfp['width_max']
    spread_head = dict_input_nfp['spread_head']
    margin_top = dict_input_nfp['margin_top']
    margin_bottom = dict_input_nfp['margin_bottom']

    width_max -= (margin_top + margin_bottom)

    start_time = time.time()

    fixo = shape_panels['panels_bb'][0][0]
    origin = [[0,0,0]]
    for id_panel in range(1,len(shape_panels['panels_bb'])):
        movel = shape_panels['panels_bb'][id_panel]
        movel_details = shape_panels['panels_details'][id_panel]
        mink_AB = minkowski_sum_details(A=fixo,
                                        B=movel,
                                        B_details=movel_details)

        fixo_bb = fixo.bounds
        movel_bb = [movel_.bounds for movel_ in movel]
        ref=least_bb(origin_A=fixo_bb[:2],
                    bbox_A = (fixo_bb[2]-fixo_bb[0], fixo_bb[3]-fixo_bb[1]),
                    bbox_B = [(movel_bb_[2]-movel_bb_[0], movel_bb_[3]-movel_bb_[1])
                                for movel_bb_ in movel_bb],
                    list_origem_B = [mink_AB_.exterior.coords for mink_AB_ in mink_AB],
                    width = width_max)
        origin.append(ref)
        movel = affinity.translate(movel[ref[2]], xoff=ref[0], yoff=ref[1])
        
        fixo = fixo.union(movel)
        if fixo.geom_type == 'MultiPolygon':  
            fixo = unir(poligonos=fixo)

    bounds = fixo.bounds
    off_set = bounds[:2]
    fixo = affinity.translate(fixo, xoff=-off_set[0], yoff=-off_set[1])
    for pos in range(len(origin)):
        origin[pos][0]-=off_set[0]
        origin[pos][1]-=off_set[1]
    
    width_max += (margin_top + margin_bottom)
    spread_length = (bounds[2]-bounds[0] + 2*spread_head)
    saving = sum([panel[0]['area'] for panel in input_json['panels']])/(width_max*spread_length)
    
    return {'grades': grades,
            'saving': saving,
            'runtime': (time.time() - start_time),
            'points': origin,
            'spread_length': spread_length}


def creating_layout(input_json, dict_output_nfp, width):
    perimeter = sum([panel[0]['perimeter'] for panel in input_json['panels']])
    return {
        "saving": np.round(dict_output_nfp['saving'], 4),
        "fabric_width": width, #mm
        "spread_length": np.round(dict_output_nfp['spread_length'], 2), #mm
        "total_perimeter": np.round(perimeter, 2), #mm
        "grades": dict_output_nfp['grades'],
    }


def sort_panels(input_json):
    #Ordenar os paineis globais
    n_patterns = len(input_json['patterns'])
    panels = []
    
    for i in range(n_patterns):
        for size in input_json['spread_results'][i]:
            for panel in input_json['patterns'][i]['grades'][size]['panels']:
                panel.update({'id_patterns':i,
                            'size': size})
                for quantity_grade in range(input_json['spread_results'][i][size]):
                    for quantity in range(panel['quantity']):
                        panels.append(panel)

    for i in range(0,len(panels)-1):
        max_value = max(panels[i]['width'],panels[i]['height'])
        #max_value = panels[i]['width']*panels[i]['height']
        max_id = i
        for j in range(i+1,len(panels)):
            ref_value = max(panels[j]['width'],panels[j]['height'])
            #ref_value = panels[j]['width']*panels[j]['height']
            if ref_value>max_value:
                max_value = ref_value
                max_id = j
        if max_id!=i:
            aux = panels[i]
            panels[i] = panels[max_id]
            panels[max_id] = aux
    
    input_json['panels'] = panels
    return input_json


def rotate_panels(input_json):
    n = len(input_json['panels'])
    for i in range(n):
        input_json['panels'][i]=[
            input_json['panels'][i]
        ]
        try:
            if input_json['panels'][i][0]['rotation']:
                aux = deepcopy(input_json['panels'][i][0])
                #aux['polygon'] = [[point[1], point[0]] for point in input_json['panels'][i][0]['polygon']]
                aux['width'] = input_json['panels'][i][0]['height']
                aux['height'] = input_json['panels'][i][0]['width']
                input_json['panels'][i].append(aux)
        except KeyError:
            continue
    return input_json


def calcular_individual_2(input_json):
    input_json = sort_panels(input_json=input_json)
    input_json = rotate_panels(input_json=input_json)
    margem_erro_nfp = 0.98

    shape_panels = {'panels_bb': [[Polygon([[0, 0],
                                  [margem_erro_nfp*rot['width'], 0],
                                  [margem_erro_nfp*rot['width'], margem_erro_nfp*rot['height']],
                                  [0, margem_erro_nfp*rot['height']]])
                                        for rot in input_json['panels'][id_panel]]
                                            for id_panel in range(len(input_json['panels']))]}

    shape_panels['panels_details']=[[Polygon(details_polygon(polygon=[[0, 0],
                                                              [margem_erro_nfp*rot['width'], 0],
                                                              [margem_erro_nfp*rot['width'], margem_erro_nfp*rot['height']],
                                                              [0, margem_erro_nfp*rot['height']]],
                                                            step=input_json['settings']['contour_step']))
                                                                for rot in input_json['panels'][id_panel]]
                                                                    for id_panel in range(len(input_json['panels']))]
    
    dict_input_nfp = {
        'grades': input_json['spread_results'],
        'panels': shape_panels,
        'width_max': input_json['fabric']['widths']['width'],
        'spread_head': input_json['fabric']['widths']['spread_head'],
        'margin_top': input_json['fabric']['widths']['margin_top'],
        'margin_bottom': input_json['fabric']['widths']['margin_bottom']
    }
    dict_output_nfp = nfp(dict_input_nfp=dict_input_nfp,
                          input_json=input_json)
    calculated = creating_layout(input_json=input_json,
                                 dict_output_nfp=dict_output_nfp,
                                 width=input_json['fabric']['widths']['width'])
    
    """
    options_plot = [[{"PP": 1, "P": 2, "M": 2, "G": 1}],
                    [{"PP": 2, "P": 4, "M": 4, "G": 2}],
                    [{"PP": 1, "P": 2, "M": 0, "G": 1}],
                    [{'P': 0, 'M': 1, 'G': 0, 'GG': 2, 'XGG': 3}],
                    [{'P': 1, 'M': 0, 'G': 2, 'GG': 0, 'XGG': 0}],
                    [{'P': 2, 'M': 4, 'G': 4, 'GG': 2}],
                    [{'P': 1, 'M': 2, 'G': 0, 'GG': 1}],
                    [{'P': 1, 'M': 2, 'G': 3, 'GG': 4}],
                    [{'38': 1, '40': 1, '42': 1, '44': 1}],
                    [{'P': 2, 'M': 3, 'G': 3, 'GG': 2}],
                    [{'P': 2}, {'P': 2}, {'M': 1}, {'04': 1}, {'40': 1}],
                    [{'M': 1}],
                    [{'M': 5}],
                    [{'M': 10}],
                    [{'M': 20}],
                    [{'M': 25}]]
    
    if input_json['spread_results'] in options_plot:
        plot(input_json, dict_input_nfp, dict_output_nfp)
    #exit()
    #"""
    
    #Fitro do tamanho da mesa
    margem_erro = 0.985
    length_max = input_json['fabric']['max_length']
    length_min = input_json['settings']['min_length']
    if (calculated['spread_length'] >= length_min and
        margem_erro*calculated['spread_length'] <= length_max): 
        return calculated 
    return None 


def calcular(input_json):
    WIDTH = [width['width'] for width in input_json['fabric']['widths']]
    for id_w,width in enumerate(WIDTH):
        for grades in input_json['spread_results']:
            copia = deepcopy(input_json)
            copia['fabric']['widths'] = input_json['fabric']['widths'][id_w]
            copia['spread_results'] = grades
            layout = calcular_individual_2(input_json=copia)
            if not (layout is None): 
                input_json['layouts'][width].append(layout)
    return input_json


def calcular_individual(input_json,grades,width):
    input_json['spread_results'] = grades
    input_json['fabric']['widths'] = [width_data
                                        for width_data in input_json['fabric']['widths']
                                            if input_json['fabric']['widths']['width']==width][0]
    return calcular_individual_2(input_json=input_json)


def lambda_handler(event, context):
    try:
        return calcular_individual_2(event)
    except Exception as e:
        raise Exception(f"Error trying to execute nfp function. Details: {str(e)}")

