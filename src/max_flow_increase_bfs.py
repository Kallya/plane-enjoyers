import networkx as nx
from collections import deque

def bfs(G, source, sink, pred):
    for n in G.nodes:
        pred[n] = -1 
    q = deque()
    # second element refers to the current lowest flow in the path
    q.append((source, float("inf")))

    while q:
        u, curr_flow = q.popleft()
        for v in G[u]:
            capacity = G[u][v]["capacity"]
            flow = G[u][v]["flow"]
            if pred[v] == -1 and capacity > flow:
                pred[v] = u
                new_flow = min(curr_flow, capacity - flow)
                if v == sink:
                    return new_flow
                q.append((v, new_flow))
    
    return 0

def max_flow_increase_bfs(G, source, sink):
    G = G.copy()
    return apply_max_flow_increase_bfs(G, source, sink)


def apply_max_flow_increase_bfs(G, source, sink):
    pred = {n: -1 for n in G.nodes}
    increase = 0
    new_flow = bfs(G, source, sink, pred)
    while new_flow > 0:
        increase += new_flow
        v = sink
        while v != source:
            u = pred[v]
            G[u][v]["flow"] += new_flow
            G[v][u]["flow"] -= new_flow
            v = u
        new_flow = bfs(G, source, sink, pred)
    
    return increase