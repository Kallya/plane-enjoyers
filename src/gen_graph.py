from pynetgen import netgen_generate
from base_multi_sink_source import MultiSinkSrcDiGraph
import networkx as nx

def gen_graph_max_flow(**kwargs):
    """
    Generate a random graph for a basic max flow problem and return it as a networkx graph

    Check the pynetgen documentation for the available parameters
    """

    netgen_generate(**kwargs)

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
    
    return G, set(sources), set(sinks)

def gen_graph_min_cost(**kwargs):
    """
    Generate a random graph for the min cost flow problem satisfying given demands
    and return it as a networkx graph

    In practice we don't actually set cost (for now) and look for a feasible flow
    that satisfies demands

    This could be used for testing the progress towards satisfying existing demands
    that a graph modification could make
    """
    netgen_generate(**kwargs)

    with open("test.net") as f:
        l = f.readline()
        while l[0] != 'n':
            l = f.readline()
        
        sources = {}
        sinks = {}
        while l[0] == 'n':
            _, n, supply = l.split()
            supply = int(supply)
            # flip the sign since we're using demand rather than supply
            if supply > 0:
                sources[n] = -supply
                # @audit how should capacity be set in relation to supply?
            else:
                sinks[n] = -supply
            l = f.readline()
        
        graph = {}
        while l:
            _, u, v, _, capacity, _ = l.split()
            if u not in graph:
                graph[u] = {}
            graph[u][v] = {"capacity": int(capacity)}
            l = f.readline()
    
    G = nx.DiGraph(graph)
    for n in sources:
        G.nodes[n]["demand"] = sources[n]
    for n in sinks:
        G.nodes[n]["demand"] = sinks[n]
    
    return G, set(sources), set(sinks)

