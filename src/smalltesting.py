from gen_graph import gen_graph_max_flow
import model as md
import networkx as nx
import random
from algorithm import *
from target_edges import *

def small_graph_experiments(iterations, budget_increment, budget_max, mincap, maxcap, graph_count, nodes, min_edges, max_edges):
    experiment_results = []

    edge_funcs = [get_guaranteed_edges]  # Assuming get_guaranteed_edges is your only edge_func
    edge_select_funcs = [
        get_lowest_ev_edge, 
        get_highest_ev_edge, 
        get_lowest_prob_edge, 
        get_highest_prob_edge
    ]

    for graph_index in range(graph_count):
        # Create the graph with randomized capacities and static attributes
        curr_density = random.randint(min_edges, max_edges)
        G, sources, sinks = gen_graph_max_flow(mincost=1, maxcost=1, supply=0,
                                               mincap=mincap, maxcap=maxcap, fname='test.net',
                                               nodes=nodes, density=curr_density,
                                               seed=random.randint(0, 10000))

        # Set random slowing_prob and slowing_factor
        md.set_random_probabilistic_attrs(G)

        # Calculate initial max flow and get residual graph
        total = 0
        for j in range(10000):
            original_max, R = md.get_intermediate_residual_graph(G, sources, sinks, nx.flow.preflow_push)
            total = total + original_max
        original_max =  total / 10000

        for edge_func in edge_funcs:
            for edge_select_func in edge_select_funcs:
                # Conduct experiments for each budget increment
                for budget in range(1, budget_max + 1, budget_increment):
                    # Apply the actual budget distribution function with the current combination
                    dist, R_c = distribute_budget(R, budget, edge_func, edge_select_func)

                    # Clean the modified residual graph using a function from the model
                    md.clean_residual_graph(R_c)

                    # Calculate the probabilistic max flow value on the cleaned residual graph
                    new_total = 0
                    for j in range(10000):
                        new_total = new_total + md.get_probabilistic_slowing_max_flow(R_c, sources, sinks, flow_func=md.get_max_flow_val)
                    new_Max = new_total/10000

                    # Record the results with graph details and the combination used
                    improvement = new_Max - original_max
                    experiment_results.append({
                        'graph_index': graph_index + 1,
                        'nodes': nodes,
                        'edges': curr_density,
                        'budget': budget,
                        'original_max_flow': original_max,
                        'new_max_flow': new_Max,
                        'improvement': improvement,
                        'edge_func': edge_func.__name__,
                        'edge_select_func': edge_select_func.__name__
                    })

    return experiment_results

#some random stuff
results = small_graph_experiments(
    iterations=10000,
    budget_increment=10,
    budget_max=500,
    mincap=5,
    maxcap=10,
    graph_count=10,
    nodes=20,
    min_edges=30,
    max_edges=40
)

# Print the results in a formatted way
for result in results:
    print(f"Graph {result['graph_index']} | Nodes: {result['nodes']} | Edges: {result['edges']} | "
          f"Budget: {result['budget']} | Original Max Flow: {result['original_max_flow']} | "
          f"New Max Flow: {result['new_max_flow']} | Improvement: {result['improvement']} | "
          f"Edge Func: {result['edge_func']} | Edge Select Func: {result['edge_select_func']}")
