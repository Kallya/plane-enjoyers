import networkx as nx
import random as rand
from math import ceil

###################### Helpers ######################
def draw(G, attribute="capacity"):
    pos = nx.circular_layout(G, scale=5)
    # pos = nx.spring_layout(G, k=1, iterations=20)
    nx.draw(G, pos=pos, with_labels=True, node_color="lightblue", node_size=500, edge_color="gray", font_weight="bold")
    nx.draw_networkx_edge_labels(G, pos=pos, edge_labels=nx.get_edge_attributes(G, attribute))

def calc_max_flow_vals(G, sinks):
    # compute max flow vals for each sink
    max_flow_vals = {}
    for n in sinks:
        max_flow_vals[n] = sum([attr["flow"] for _, _, attr in G.in_edges(n, data=True)])

    return max_flow_vals

def clean_graph(G):
    # remove edges with 0 flow
    G.remove_edges_from([e for e in G.edges if G.edges[e]["flow"] == 0])
    # remove isolated vertices (those with no edges incident on them)
    G.remove_nodes_from(list(nx.isolates(G))) 

###################### Base max flow ######################
def get_max_flow(G, sources, sinks, max_flow_func=nx.maximum_flow):
    """
    Base multi sink/source max flow where each edge has a capacity
    Returns the max flow graph
    """

    G = G.copy() 
    G.add_node("source")
    G.add_node("sink")

    for source in sources:
        # infinite capacity
        G.add_edge("source", source)

    for sink in sinks:
        # infinity capacity
        G.add_edge(sink, "sink")

    if max_flow_func == nx.maximum_flow:
        _, max_flow = max_flow_func(G, "source", "sink")
    else:
        max_flow = max_flow_func(G, "source", "sink")

    for i in max_flow:
        for j in max_flow[i]:
            max_flow[i][j] = {"flow": max_flow[i][j]}
    
    G = nx.DiGraph(max_flow)
    G.remove_nodes_from(["source", "sink"])
    clean_graph(G)

    return G

def get_max_flow_val(G, sources, sinks):
    """
    Base multi sink/source max flow where each edge has a capacity
    Returns the max flow graph
    """

    G = G.copy() 
    G.add_node("source")
    G.add_node("sink")

    for source in sources:
        # infinite capacity
        G.add_edge("source", source)

    for sink in sinks:
        # infinity capacity
        G.add_edge(sink, "sink")

    max_flow_val, _ = nx.maximum_flow(G, "source", "sink")
    
    return max_flow_val 

def get_max_flow_with_v_capacity(G, sources, sinks, max_flow_func=nx.maximum_flow):
    """
    Get max flow of a network with vertex capacities

    Must have "capacity" defined for each vertex in G

    Ensure "weight" is defined in G for each edge if calculating min cost max flow.
    In this case max_flow_func=nx.max_cost_min_flow.
    """
    aux_sources = [n + "_in" for n in sources]
    aux_sinks = [n + "_out" for n in sinks]

    G_c = G.copy()

    # add vertex capacities to the graph
    for n in G.nodes:
        G_c.add_node(n + "_in")
        G_c.add_node(n + "_out")

        # connect each incoming edge to the 'in' vertex
        for u, _, attr in G_c.in_edges(n, data=True):
            G_c.add_edge(u, n + "_in", **attr)
        # connect each outgoing edge to the 'out' vertex
        for _, v, attr in G_c.out_edges(n, data=True):
            G_c.add_edge(n + "_out", v, **attr)
        
        # connect the 'in' vertex to the 'out' vertex with the vertex
        # capacity as the capacity of the edge
        G_c.add_edge(n + "_in", n + "_out", capacity=G.nodes[n]["capacity"])

        # remove the original vertex
        G_c.remove_node(n)
    
    G_c = get_max_flow(G_c, aux_sources, aux_sinks, max_flow_func)

    for n in G.nodes:
        G_c.add_node(n)
        for e in G_c.in_edges(n + "_in", data=True):
            G_c.add_edge(e[0], n, flow=e[2]["flow"])
        for e in G_c.out_edges(n + "_out", data=True):
            G_c.add_edge(n, e[1], flow=e[2]["flow"])
        G_c.remove_node(n + "_in")
        G_c.remove_node(n + "_out")
    
    # cleanup 
    clean_graph(G_c)
    
    return G_c

def get_min_cost_flow(G, sources, sinks):
    """
    Get satisfying flow taking into account vertex capacities and demand

    G should define vertex capacity and demand (we leave cost constant for our
    purposes for now), and edge capacity

    sources and sinks should both be sets

    demand for a node is negative if they are a source, otherwise positive for a sink 
    """
    G_c = G.copy()

    # construct the aux graph over which we calculate max flow
    for n in G.nodes:
        if n in sources:
            G_c.add_node(n + "_in", demand=G.nodes[n]["demand"])
            G_c.add_node(n + "_out")
        elif n in sinks:
            G_c.add_node(n + "_in")
            G_c.add_node(n + "_out", demand=G.nodes[n]["demand"])
        else:
            G_c.add_node(n + "_in")
            G_c.add_node(n + "_out")

        # connect each incoming edge to the 'in' vertex
        for u, _, attr in G_c.in_edges(n, data=True):
            G_c.add_edge(u, n + "_in", **attr)
        # connect each outgoing edge to the 'out' vertex
        for e in G_c.out_edges(n, data=True):
            G_c.add_edge(n + "_out", e[1], **attr)
        
        # connect the 'in' vertex to the 'out' vertex with the vertex
        # capacity as the capacity of the edge
        # weight not defined as cost is 0
        G_c.add_edge(n + "_in", n + "_out", capacity=G.nodes[n]["capacity"])

        # remove the original vertex
        G_c.remove_node(n)
    
    _, flow = nx.network_simplex(G_c)

    for i in flow:
        for j in flow[i]:
            flow[i][j] = {"flow": flow[i][j]}
    
    G_c = nx.DiGraph(flow)

    for n in G.nodes:
        G_c.add_node(n)
        for e in G_c.in_edges(n + "_in", data=True):
            G_c.add_edge(e[0], n, flow=e[2]["flow"])
        for e in G_c.out_edges(n + "_out", data=True):
            G_c.add_edge(n, e[1], flow=e[2]["flow"])
        G_c.remove_nodes_from([n + "_in", n + "_out"])
    
    return G_c

############# Probabilistic capacity reduction (weather obstruction) ###########
def get_probabilistic_slowing_max_flow(G, sources, sinks, flow_func=get_max_flow_val):
    """
    Multi source and sink with each edge having a probability of being slowed
    (e.g. due to fog, limited visibility etc.)

    G must define "slowing_prob" and "slowing_factor" for each edge
    """
    G = G.copy()

    for u, v, attr in G.edges(data=True):
        if rand.random() < attr["slowing_prob"]:
            # round up so we don't have 0 capacity if not intended
            G.edges[u, v]["capacity"] = int(ceil(attr["capacity"] * (1-attr["slowing_factor"])))
    
    return flow_func(G, sources, sinks)

def get_probabilistic_v_blocking_max_flow(G, sources, sinks, 
                                          base_problem_func=get_max_flow_with_v_capacity):
    """
    Multi source and sink with each vertex having a probability of being blocked
    (ie. all adjacent edges are impassable)

    G must define "blocking_prob" for each vertex
    """

    G = G.copy()

    removed_nodes = [n for n in G.nodes if rand.random() < G.nodes[n]["blocking_prob"]]
    G.remove_nodes_from(removed_nodes)

    sources = set(sources) - set(removed_nodes)
    sinks = set(sinks) - set(removed_nodes)

    # @audit do we want to reroute if some path is lost?
    
    return base_problem_func(G, sources, sinks)


# Generalised probabilistic max flow approximation
def get_expected_capacity_graph(G):
    """
    Gets modified G where capacities are set to their expected capacity
    taking into account their slowing factor and probability

    G must have edges each with attribute "slowing_prob", "slowing_factor", 
    and capacity
    """
    G = G.copy()
    for u, v, attr in G.edges(data=True):
        # expected capacity = slowing_prob * (1 - slowing_factor) * capacity + capacity * (1 - slowing_prob)
        G.edges[(u, v)]["capacity"] = \
            attr["slowing_prob"] * (1 - attr["slowing_factor"]) * attr["capacity"] \
            + attr["capacity"] * (1 - attr["slowing_prob"])
    
    return G

def get_expected_max_flow(G, sources, sinks, flow_func=get_max_flow):
    """
    Calculates the max flow of G with edge capacities set to the expected value
    """
    G = get_expected_capacity_graph(G)
    G = flow_func(G, sources, sinks)

    return calc_max_flow_vals(G, sinks)

def set_random_probabilistic_attrs(G, prob_range=(0, 1), factor_range=(0, 1)):
    """
    Sets random slowing probability and factor for each edge in G
    """

    for u, v in G.edges:
        G.edges[(u, v)]["slowing_prob"] = rand.uniform(*prob_range)
        G.edges[(u, v)]["slowing_factor"] = rand.uniform(*factor_range)

def get_intermediate_residual_graph(G, sources, sinks, flow_func):
    G = G.copy()

    for s in sources:
        G.add_edge("source", s, slowing_prob=0, slowing_factor=0)
    for s in sinks:
        G.add_edge(s, "sink", slowing_prob=0, slowing_factor=0)
    
    R = flow_func(G, "source", "sink")

    nx.set_edge_attributes(R, 0, "slowing_prob")
    nx.set_edge_attributes(R, 0, "slowing_factor")

    for u, v in G.edges:
        R[u][v]["slowing_prob"] = G[u][v]["slowing_prob"]
        R[u][v]["slowing_factor"] = G[u][v]["slowing_factor"]

    max_flow = 0
    for n in R.neighbors("source"):
        max_flow += R["source"][n]["flow"]
    
    return max_flow, R

def clean_residual_graph(R):
    R.remove_nodes_from(["source", "sink"])
    edges = R.edges
    R.remove_edges_from([(u, v) for u, v in R.edges if R[u][v]["flow"] <= 0 or R[u][v]["capacity"] == 0])
    for u, v in list(R.edges):
        if R[u][v]["flow"] <= 0:
            R.remove_edge(u, v)
        if R[u][v]["capacity"] == 0:
            R.remove_edge(u, v)
