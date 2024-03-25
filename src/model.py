import networkx as nx

###################### Helpers ######################
def draw(G, attribute="capacity"):
    pos = nx.circular_layout(G, scale=5)
    # pos = nx.spring_layout(G, k=1, iterations=20)
    nx.draw(G, pos=pos, with_labels=True, node_color="lightblue", node_size=500, edge_color="gray", font_weight="bold")
    nx.draw_networkx_edge_labels(G, pos=pos, edge_labels=nx.get_edge_attributes(G, attribute))

###################### Base max flow ######################
def get_max_flow(G, sources, sinks):
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
    
    _, max_flow = nx.maximum_flow(G, "source", "sink")

    for i in max_flow:
        for j in max_flow[i]:
            max_flow[i][j] = {"flow": max_flow[i][j]}
    
    G = nx.DiGraph(max_flow)
    G.remove_nodes_from(["source", "sink"])

    return G

def calc_max_flow_vals(G, sinks):
    # compute max flow vals for each sink
    max_flow_vals = {sink: 0 for sink in sinks}
    for e in G.edges(data=True):
        if e[1] in sinks:
            max_flow_vals[e[1]] += e[2]["flow"]

    return max_flow_vals

def get_max_flow_with_v_capacity(G, sources, sinks):
    G_c = G.copy()
    aux_sources = [n + "_in" for n in sources]
    aux_sinks = [n + "_out" for n in sinks]

    # add vertex capacities to the graph
    for n in G.nodes:
        G_c.add_node(n + "_in")
        G_c.add_node(n + "_out")

        # connect each incoming edge to the 'in' vertex
        for e in G_c.in_edges(n, data=True):
            G_c.add_edge(e[0], n + "_in", capacity=e[2]["capacity"])
        # connect each outgoing edge to the 'out' vertex
        for e in G_c.out_edges(n, data=True):
            G_c.add_edge(n + "_out", e[1], capacity=e[2]["capacity"])
        
        # connect the 'in' vertex to the 'out' vertex with the vertex
        # capacity as the capacity of the edge
        G_c.add_edge(n + "_in", n + "_out", capacity=G.nodes[n]["capacity"])

        # remove the original vertex
        G_c.remove_node(n)
    
    G_c = get_max_flow(G_c, aux_sources, aux_sinks)

    for n in G.nodes:
        G_c.add_node(n)
        for e in G_c.in_edges(n + "_in", data=True):
            G_c.add_edge(e[0], n, flow=e[2]["flow"])
        for e in G_c.out_edges(n + "_out", data=True):
            G_c.add_edge(n, e[1], flow=e[2]["flow"])
        G_c.remove_node(n + "_in")
        G_c.remove_node(n + "_out")
    
    return G_c

def get_base_max_flow(G, sources, sinks):
    """
    Get max flow taking into account vertex capacities and demand

    G should define vertex capacity and demand, and edge capacity

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
        for e in G_c.in_edges(n, data=True):
            G_c.add_edge(e[0], n + "_in", **e[2])
        # connect each outgoing edge to the 'out' vertex
        for e in G_c.out_edges(n, data=True):
            G_c.add_edge(n + "_out", e[1], **e[2])
        
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