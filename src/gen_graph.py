from pynetgen import netgen_generate
from base_multi_sink_source import MultiSinkSrcDiGraph
import networkx as nx

def gen_graph(seed=1, graph_class=MultiSinkSrcDiGraph, **kwargs):
    """
    Generate a random graph using pynetgen and return it as a networkx graph

    set seed to -1 to generate a random seed

    graph_class is the class to use to represent the graph

    add extra initialisation parameters to the graph_class using kwargs (apart
    from incoming_graph_data, sources, and sinks, which are set by this function)
    """

    netgen_generate(seed=seed, mincost=1, maxcost=1, supply=0, fname="test.net")

    with open("test.net") as f:
        l = f.readline()
        while l[0] != 'a':
            l = f.readline()
        
        graph = {}
        while l:
            _, u, v, capacity = l.split()
            if u not in graph:
                graph[u] = {}
            graph[u][v] = {"capacity": int(capacity)}
            l = f.readline()

    G = nx.DiGraph(graph)
    sources = []
    sinks = []
    for n in G.nodes:
        if G.in_degree(n) == 0:
            sources.append(n)
        elif G.out_degree(n) == 0:
            sinks.append(n)
    
    return graph_class(graph, sources, sinks)
    

