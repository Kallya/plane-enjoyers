import model as md

def calc_flow_centrality(G, sources, sinks, flow_func):
    """
    Calculates the portion of each edge's aggregate flow from all source/sink
    pairs over the aggregate total flow between all source/sink pairs

    Returns a dictionary mapping each edge to its calculated portion (the 
    centrality index)
    """

    # @audit what impact does the fact that max flow are not unique have on this?
    # @audit could updating this with changes in the graph help in efficiently
    # aggregating a measure over a dynamic graph

    # calculate aggregate max flow between all sources and sinks
    # for each edge calculate the sum of its flow values for every source,sink pair
    edge_flow_sums = {}
    aggregate_max_flow = 0
    for u in sources:
        for v in sinks:
            G_m = flow_func(G, [u], [v])
            aggregate_max_flow += md.calc_max_flow_vals(G_m, [v])[v]
            for e in G_m.edges:
                if e not in edge_flow_sums:
                    edge_flow_sums[e] = 0
                edge_flow_sums[e] += G_m.edges[e]["flow"]
    
    # normalise each sum by dividing by the aggregate max flow to get the portion
    # of flow accounted for by the edge
    for e in edge_flow_sums:
        edge_flow_sums[e] /= aggregate_max_flow

    return edge_flow_sums
    

def rank_flow_centrality(index_mapping):
    """
    Transform to an ordered list ranked by the centrality (highest to lowest)

    index_mapping should be output from calc_flow_centrality
    """

    return sorted(index_mapping.items(), key=lambda x: x[1], reverse=True)

# @audit this seems to be buggy (doesn't run the last iteration), also doesn't seem to be really useful in increasing max flow
def path_reversal(G):
    """
    Minimises the outdegree of the nodes in the graph G by reversing paths

    G should be the subgraph of the flow network with the source and sinks removed

    Original algo: https://catalog.lib.kyushu-u.ac.jp/opac_download_md/14869/IJFCS-revision.pdf

    We assume G is simple and directed

    Returns a new graph with the old weights and new orientation
    """

    # we should already have a random orientation
    G = G.copy()

    outdegree = {n: d for n, d in G.out_degree()}
    pred = {n: -1 for n in G.nodes()}
    visited = {n: False for n in G.nodes()}

    def dfs_setup():
        for n in pred:
            pred[n] = -1
            visited[n] = False

    while True:
        # find a node with max outdegree
        max_outdegree = max(outdegree.values())

        # we can't find any more reversible paths since the ending node
        # would have to have negative outdegree
        if max_outdegree <= 1:
            break

        def dfs(u, v):
            pred[v] = u 
            if outdegree[v] <= max_outdegree - 2:
                return v
            visited[v] = True

            for n in G.neighbors(v):
                if visited[n]:
                    continue
                res = dfs(v, n)
                if res:
                    return res
            # reset the predecessor so we don't end up with weird cycles
            pred[v] = -1            

            return None

        did_reverse = False
        for n in outdegree:
            if outdegree[n] != max_outdegree:
                continue

            dfs_setup()
            v = dfs(-1, n)

            # stop if no nodes with low enough outdegree
            # (ie. all reachable nodes have outdegree >= max_outdegree - 1)
            if v is None:
                continue

            # flag that there was reversal for one of the max outdegree nodes 
            did_reverse = True

            # outdegree of end node increases since we're reversing away from it
            # outdegree of every intermediate node doesn't change
            outdegree[v] += 1
            outdegree[n] -= 1

            # trace the path and reverse the edges
            while pred[v] != -1:
                attr = G[pred[v]][v]
                G.remove_edge(pred[v], v)
                G.add_edge(v, pred[v], **attr)
                v = pred[v]
        
        # if there were no reversals, then we can't find any more
        if not did_reverse:
            break
    
    return G