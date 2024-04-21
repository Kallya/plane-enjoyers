from gen_graph import gen_graph_max_flow
import model as md
import networkx as nx
import random
from algorithm import *
from target_edges import *
import pprint

edge_select_funcs = [
    get_lowest_ev_edge,
    get_highest_ev_edge,
    get_lowest_prob_edge,
    get_highest_prob_edge,
    get_edge_and_cap_inc_by_cap,
    get_random_edge,
]

def calc_prob_max_flow(G, sources, sinks, iterations):
    total = 0
    for _ in range(iterations):
        total += md.get_probabilistic_slowing_max_flow(G, sources, sinks)
    return total / iterations

def test_one_graph(iterations, budget_increment, budget_min, budget_max, mincap, maxcap, nodes, density):
    G, sources, sinks = gen_graph_max_flow(mincost=1, maxcost=1, supply=0,
                                           mincap=mincap, maxcap=maxcap, fname='test.net',
                                           nodes=nodes, density=density,
                                           seed=-1)
    md.set_random_probabilistic_attrs(G)

    res = {"graph": G, "results": {}}

    original_max = calc_prob_max_flow(G, sources, sinks, iterations)

    _, R = md.get_intermediate_residual_graph(G, sources, sinks, nx.flow.preflow_push)
    budget = budget_min
    for edge_select_func in edge_select_funcs:
        res["results"][edge_select_func.__name__] = []
        if edge_select_func == get_edge_and_cap_inc_by_cap:
            # Use a different budget distribution function for this specific function
            dist, R_c = distribute_budget_fair(R, budget, get_guaranteed_edges, edge_select_func)
        else:
            dist, R_c = distribute_budget(R, budget, get_guaranteed_edges, edge_select_func)

        md.clean_residual_graph(R_c)
        new_max = calc_prob_max_flow(R_c, sources, sinks, iterations)
        improvement = new_max - original_max

        res["results"][edge_select_func.__name__].append({
            'original_max_flow': original_max,
            'density': density,
            'new_max_flow': new_max,
            'improvement': improvement,
        })
    
    return res

if __name__ == "__main__":
    res = test_one_graph(
        iterations=100,
        budget_increment=10,
        budget_min= 50,
        budget_max= 1100,
        mincap=5,
        maxcap=15,
        nodes=20,
        density=100
        ,
    )
    pprint.pprint(res)
