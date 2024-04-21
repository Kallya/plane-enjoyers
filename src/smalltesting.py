from gen_graph import gen_graph_max_flow
import model as md
import networkx as nx
import random
from algorithm import *
from target_edges import *

edge_select_funcs = [
    get_lowest_ev_edge, 
    get_highest_ev_edge, 
    get_lowest_prob_edge, 
    get_highest_prob_edge
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

    res = { "graph": G, "results": {} }

    # Calculate initial max flow and get residual graph
    original_max = calc_prob_max_flow(G, sources, sinks, iterations) 
    _, R = md.get_intermediate_residual_graph(G, sources, sinks, nx.flow.preflow_push)

    for edge_select_func in edge_select_funcs:
        res["results"][edge_select_func.__name__] = []
        # Conduct experiments for each budget increment
        for budget in range(budget_min, budget_max + 1, budget_increment):
            # Apply the actual budget distribution function with the current combination
            dist, R_c = distribute_budget(R, budget, get_guaranteed_edges, edge_select_func)

            # Clean the modified residual graph using a function from the model
            md.clean_residual_graph(R_c)

            # Calculate the probabilistic max flow value on the cleaned residual graph
            new_max = calc_prob_max_flow(R_c, sources, sinks, iterations)

            # Record the results with graph details and the combination used
            improvement = new_max - original_max
            res["results"][edge_select_func.__name__].append({
                'budget': budget,
                'new_max_flow': new_max,
                'improvement': improvement,
            })
    
    return res

if __name__ == "__main__":
    #some random stuff
    res = test_one_graph(
        iterations=100,
        budget_increment=5,
        budget_min=5,
        budget_max=50,
        mincap=5,
        maxcap=20,
        nodes=20,
        density=40,
    )

    # Print the results in a formatted way
    print(res) 