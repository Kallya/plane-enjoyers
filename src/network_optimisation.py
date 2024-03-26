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

    return 
    

def rank_flow_centrality(index_mapping):
    """
    Transform to an ordered list ranked by the centrality (highest to lowest)

    index_mapping should be output from calc_flow_centrality
    """

    return sorted(index_mapping.items(), key=lambda x: x[1], reverse=True)