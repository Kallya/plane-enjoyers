import random
import max_flow_increase_bfs as mf

def get_random_edge(G, edges):
    """Gets a random edge out of edges"""

    idx = random.randint(0, len(edges) - 1)
    return edges[idx]

def get_highest_prob_edge(G, edges):
    """Finds the edge with highest slowing probability out of edges"""

    max_prob = -1 
    max_edge = None
    for e in edges:
        if G.edges[e]["slowing_prob"] > max_prob:
            max_prob = G.edges[e]["slowing_prob"]
            max_edge = e
    
    return max_edge

def get_lowest_prob_edge(G, edges):
    """Finds the edge with lowest slowing probability out of edges"""

    min_prob = float("inf") 
    min_edge = None
    for e in edges:
        if G.edges[e]["slowing_prob"] < min_prob:
            min_prob = G.edges[e]["slowing_prob"]
            min_edge = e

    return min_edge

def ev(G, u, v):
    """Expected value of edge (u, v) in graph G"""

    # capacity * (1 - slowing_prob) + capacity * slowing_prob * slowing_factor
    return int(G[u][v]["capacity"] * (1 - G[u][v]["slowing_prob"]) 
               + G[u][v]["capacity"] * G[u][v]["slowing_prob"] * G[u][v]["slowing_factor"])

def get_highest_ev_edge(G, edges):
    """Finds the edge with highest expected capacity out of edges"""

    max_ev = -1 
    max_edge = None
    for e in edges:
        ev_val = ev(G, *e)
        if ev_val > max_ev:
            max_ev = ev_val
            max_edge = e
    
    return max_edge

def get_lowest_ev_edge(G, edges):
    """Finds the edge with lowest expected capacity out of edges"""

    min_ev = float("inf") 
    min_edge = None
    for e in edges:
        ev_val = ev(G, *e)
        if ev_val < min_ev:
            min_ev = ev_val
            min_edge = e
    
    return min_edge

def distribute_budget(R, budget, edge_func, edge_select_func):
    """ 
    edge_func gets all possible edges to consider - can be 
    get_lowest_ev_edge, get_highest_ev_edge, 
    get_lowest_prob_edge, get_highest_prob_edge,

    edge_select_func selects out of edges returned by edge_func - 
    can be get_guaranteed_edges or get_min_cut_edges, though get_guaranteed_edges
    should be default (it is better)
    """
    R = R.copy()
    distribution = {}

    while budget > 0:
        edges = edge_func(R)
        # terminate early if we can't increase capacity anymore (does this even happen?)
        if len(edges) == 0:
            return distribution, R
        u, v = edge_select_func(R, edges)
        R[u][v]["capacity"] += budget 
        # @audit need to change when fully implemented
        increase = mf.apply_max_flow_increase_bfs(R, "source", "sink")
        # @audit this is a point for failure if we aren't using the guaranteed edges
        if increase == 0:
            R[u][v]["capacity"] -= budget
            continue
        if (u, v) not in distribution:
            distribution[(u, v)] = 0
        distribution[(u, v)] += increase
        # cap the increase at the max flow increased
        budget -= increase
        R[u][v]["capacity"] -= budget
    
    return distribution, R

def get_edge_and_cap_inc_by_cap(R, edges):
    """Gets the edge with the lowest capacity and the capacity of the next lowest capacity edge"""

    # get min capacity target edge and capacity of the next min capacity target edge
    min_cap1 = float("inf")
    min_cap2 = float("inf")
    min_e1 = None
    for e in edges:
        cap = R.edges[e]["capacity"]
        if cap < min_cap1:
            min_cap2 = min_cap1
            min_cap1 = cap
            min_e1 = e
        elif cap < min_cap2:
            min_cap2 = cap

    return min_e1, min_cap2

def distribute_budget_fair(R, budget, edge_func, edge_select_func):
    """
    edge_func gets all possible edges to consider - can be 
    get_guaranteed_edges or get_min_cut_edges, though get_guaranteed_edges
    should be default (it is better)

    edge_select_func selects out of edges returned by edge_func -
    can be get_edge_and_cap_inc_by_ev or get_edge_and_cap_inc_by_cap
    """

    R = R.copy()
    distribution = {}

    while budget > 0:
        edges = edge_func(R)
        if len(edges) == 0:
            return distribution, R
        (u, v), cap = edge_select_func(R, edges) 
        cap_inc = min(budget, cap)
        R[u][v]["capacity"] += cap_inc
        # @audit need to change when fully implemented
        increase = mf.apply_max_flow_increase_bfs(R, "source", "sink")
        if increase == 0:
            R[u][v]["capacity"] -= cap_inc
            continue
        if (u, v) not in distribution:
            distribution[(u, v)] = 0
        distribution[(u, v)] += increase
        budget -= increase
        R[u][v]["capacity"] -= cap_inc - increase
    
    return distribution, R