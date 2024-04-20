from collections import deque
import networkx as nx

def reachable_nodes(R, origin):
    visited = set()
    queue = deque()
    visited.add(origin)
    queue.append(origin)
    while queue:
        node = queue.popleft()
        for neighbor in R.neighbors(node):
            if neighbor not in visited and R[node][neighbor]["capacity"] - R[node][neighbor]["flow"] > 0:
                visited.add(neighbor)
                queue.append(neighbor)
    
    return visited

def get_min_cut_edges(R):
    # the worse one
    s_reachable = reachable_nodes(R, "source")
    t_reachable = reachable_nodes(R, "sink")
    edges = []
    for u, v, attr in R.edges(data=True):
        if u == "source" or v == "sink":
            continue
        if attr["capacity"] > 0 and u in s_reachable and v in t_reachable:
            edges.append((u, v))

    return edges

def get_guaranteed_edges(R):
    # the better one, have to be careful of the additional time taken
    # for edge reversal though
    s_reachable = reachable_nodes(R, "source")
    R_c = nx.DiGraph()
    for u, v, attr in R.edges(data=True):
        R_c.add_edge(v, u, **attr)
    t_reachable = reachable_nodes(R_c, "sink")
    edges = []
    for u, v, attr in R.edges(data=True):
        if u == "source" or v == "sink" or u == "sink" or v == "source":
            continue
        if u in s_reachable and v in t_reachable:
            edges.append((u, v))

    return edges