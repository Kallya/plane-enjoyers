import random as rand
import networkx as nx

from base_multi_sink_source import MultiSinkSrcDiGraph

class BlockingWeatherGraph(MultiSinkSrcDiGraph):
    def __init__(self, incoming_graph_data, sources, sinks, blocking_prob, **attr):
        """
        Multi source and sink with each edge having a probability of being blocked
        (ie. unpassable/unusable) when the max flow is retrieved or computed
        blocking_prob is either an int or float, in which case all edges have the same 
        blocking probability, or a dict mapping each edge to its blocking probability

        each probability must be between 0 and 1 (inclusive)
        """

        super().__init__(incoming_graph_data, sources, sinks, **attr)

        if type(blocking_prob) is int or type(blocking_prob) is float:
            # set all edges to have the same blocking probability
            self.blocking_probs = {e: blocking_prob for e in self.edges}
        else:
            self.blocking_probs = blocking_prob
    
    def get_max_flow(self, flow_func=nx.algorithms.flow.preflow_push):
        # remove edges with probability
        removed_edges = [e for e in self.edges(data=True) if rand.random() < self.blocking_probs[e[:2]]]
        self.remove_edges_from(removed_edges)

        # remove isolated nodes (no in or out edges)
        removed_nodes = nx.isolates(self)
        self.remove_nodes_from(list(removed_nodes))

        original_sources = self.sources
        original_sinks = self.sinks
        self.sources = set(self.sources) - set(removed_nodes)
        self.sinks = set(self.sinks) - set(removed_nodes)

        max_flow_val, max_flow = super().get_max_flow(flow_func=flow_func)

        # reform the graph after calculating max flow
        self.add_nodes_from(removed_nodes)
        self.add_edges_from(removed_edges)
        self.sources = original_sources
        self.sinks = original_sinks

        return max_flow_val, max_flow