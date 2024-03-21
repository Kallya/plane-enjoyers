import networkx as nx
import matplotlib.pyplot as plt
from copy import deepcopy

def draw(G, attribute="capacity"):
    pos = nx.spring_layout(G, k=1, iterations=20)
    nx.draw(G, pos=pos, with_labels=True, node_color="lightblue", node_size=500, edge_color="gray", font_weight="bold")
    nx.draw_networkx_edge_labels(G, pos=pos, edge_labels=nx.get_edge_attributes(G, attribute))

class MultiSinkSrcDiGraph(nx.DiGraph):
    def __init__(self, incoming_graph_data, sources, sinks, **attr):
        """
        Wrapper for solving max flow over multiple sources and sinks
        incoming_graph_data must define edges with attribute "capacity"
        "source" and "sink" are reserved keywords and cannot be used as vertices
        """

        assert("source" not in sources)
        assert("sink" not in sinks)
        # a vertex cannot be both a sink and a source
        assert(set(sources).isdisjoint(sinks))

        super().__init__(incoming_graph_data, **attr)
        self.sources = set(sources)
        self.sinks = set(sinks)
        self.max_flow_vals = None
        self.max_flow_graph = None

    def draw(self):
        draw(self, "capacity")
    
    def draw_max_flow(self):
        assert(self.max_flow_graph is not None)
        draw(self.max_flow_graph, "flow")

    def get_sink_max_flow(self, sink):
        assert(self.max_flow_vals is not None)
        assert(sink in self.sinks)
        return self.max_flow_vals[sink]
    
    def compute_max_flow(self, flow_func=nx.algorithms.flow.preflow_push):
        G = deepcopy(self)
        G.add_node("source")
        G.add_node("sink")
 
        for source in self.sources:
            # infinite capacity
            G.add_edge("source", source)

        for sink in self.sinks:
            # infinity capacity
            G.add_edge(sink, "sink")

        max_flow_val, max_flow = nx.maximum_flow(G, "source", "sink", flow_func=flow_func)

        # construct the max flow graph
        for i in max_flow:
            for j in max_flow[i]:
                max_flow[i][j] = {"flow": max_flow[i][j]}
        
        self.max_flow_graph = nx.DiGraph(max_flow)
        self.max_flow_graph.remove_nodes_from(["source", "sink"])
        self._compute_max_flow_vals()

    def _compute_max_flow_vals(self):
        self.max_flow_vals = {sink: 0 for sink in self.sinks}
        for e in self.max_flow_graph.edges(data=True):
            if e[1] in self.sinks:
                self.max_flow_vals[e[1]] += e[2]["flow"]

if __name__ == "__main__":
    G = MultiSinkSrc([], ["a", "b", "c"], ["x", "y", "z"])
    G.add_edge("a", "x", capacity=3)
    G.add_edge("a", "y", capacity=2)
    G.add_edge("b", "x", capacity=1)
    G.add_edge("b", "z", capacity=1)
    G.add_edge("c", "y", capacity=1)
    G.add_edge("c", "z", capacity=3)
    G.draw()
    G.compute_max_flow()
    G.draw_max_flow()
    plt.savefig("multi_sink_src.png")