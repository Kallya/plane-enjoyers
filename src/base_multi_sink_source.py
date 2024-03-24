import networkx as nx

def draw(G, attribute="capacity"):
    pos = nx.circular_layout(G)
    # pos = nx.spring_layout(G, k=1, iterations=20)
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
        _, max_flow = self.get_max_flow(flow_func=flow_func)

        # construct the max flow graph
        for i in max_flow:
            for j in max_flow[i]:
                max_flow[i][j] = {"flow": max_flow[i][j]}
        
        self.max_flow_graph = nx.DiGraph(max_flow)
        self.max_flow_graph.remove_nodes_from(["source", "sink"])

        # compute max flow vals for each sink
        self.max_flow_vals = {sink: 0 for sink in self.sinks}
        for e in self.max_flow_graph.edges(data=True):
            if e[1] in self.sinks:
                self.max_flow_vals[e[1]] += e[2]["flow"]
    
    def get_max_flow(self, flow_func=nx.algorithms.flow.preflow_push):
        """Get the max flow value and max flow (in dict of dicts format)"""

        self.add_node("source")
        self.add_node("sink")
 
        for source in self.sources:
            # infinite capacity
            self.add_edge("source", source)

        for sink in self.sinks:
            # infinity capacity
            self.add_edge(sink, "sink")

        max_flow_val, max_flow = nx.maximum_flow(self, "source", "sink", flow_func=flow_func)

        self.remove_node("source")
        self.remove_node("sink")

        return max_flow_val, max_flow