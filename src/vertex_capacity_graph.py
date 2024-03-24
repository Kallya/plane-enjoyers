from base_multi_sink_source import MultiSinkSrcDiGraph
import networkx as nx

class VertexCapacityGraph(MultiSinkSrcDiGraph):
    def __init__(self, incoming_graph_data, sources, sinks, v_capacity, **attr):
        """
        Graph that implements constraints on the flow at each vertex

        v_capacity must be an integer or a dictionary mapping each vertex to its capacity
        """

        super().__init__(incoming_graph_data, sources, sinks, **attr)

        # the graph to use for computations (which includes vertex capacities)
        self.comp_graph = MultiSinkSrcDiGraph(self, set(n + "_in" for n in sources), 
                                              set(n + "_out" for n in sinks))

        def add_vertex_capacities(v_capacity):
            # add vertex capacities to the graph
            for n in list(self.comp_graph.nodes):
                self.comp_graph.add_node(n + "_in")
                self.comp_graph.add_node(n + "_out")

                # connect each incoming edge to the 'in' vertex
                for e in self.comp_graph.in_edges(n, data=True):
                    self.comp_graph.add_edge(e[0], n + "_in", capacity=e[2]["capacity"])
                # connect each outgoing edge to the 'out' vertex
                for e in self.comp_graph.out_edges(n, data=True):
                    self.comp_graph.add_edge(n + "_out", e[1], capacity=e[2]["capacity"])
                
                # connect the 'in' vertex to the 'out' vertex with the vertex
                # capacity as the capacity of the edge
                self.comp_graph.add_edge(n + "_in", n + "_out", capacity=v_capacity[n])

                # remove the original vertex
                self.comp_graph.remove_node(n)

        if type(v_capacity) is int:
            v_capacity = {n: v_capacity for n in self.nodes} 
            add_vertex_capacities(v_capacity)
        elif type(v_capacity) is dict:
            add_vertex_capacities(v_capacity)
        else:
            raise ValueError("v_capacity must be an integer or a dictionary")
    
    def get_max_flow(self, flow_func=nx.algorithms.flow.preflow_push):
        return self.comp_graph.get_max_flow(flow_func=flow_func)
    
    def compute_max_flow(self, flow_func=nx.algorithms.flow.preflow_push):
        _, max_flow = self.get_max_flow(flow_func=flow_func)

        # construct the max flow graph
        for i in max_flow:
            for j in max_flow[i]:
                max_flow[i][j] = {"flow": max_flow[i][j]}
        
        self.max_flow_graph = nx.DiGraph(max_flow)
        self.max_flow_graph.remove_nodes_from(["source", "sink"])

        # reform the graph with the original nodes
        for n in list(self.nodes):
            self.max_flow_graph.add_node(n)
            for e in self.max_flow_graph.in_edges(n + "_in", data=True):
                self.max_flow_graph.add_edge(e[0], n, flow=e[2]["flow"])
            for e in self.max_flow_graph.out_edges(n + "_out", data=True):
                self.max_flow_graph.add_edge(n, e[1], flow=e[2]["flow"])
            self.max_flow_graph.remove_node(n + "_in")
            self.max_flow_graph.remove_node(n + "_out")

        # compute max flow vals for each sink
        self.max_flow_vals = {sink: 0 for sink in self.sinks}
        for e in self.max_flow_graph.edges(data=True):
            if e[1] in self.sinks:
                self.max_flow_vals[e[1]] += e[2]["flow"]