# plane-enjoyers

Airline network capacity optimisation.

## Setup

*Note: commands may differ*

- Create a virtual environment.
```bash
$ python3 -m venv .venv
```

- Activate the virtual environment and install libraries specified from 'requirements.txt'.
```bash
$ source .venv/bin/activate
$ (.venv) pip install -r requirements.txt
```

## Examples

### Imports
```python3
from gen_graph import gen_graph_min_cost, gen_graph_max_flow
import model as md
import networkx as nx
```

### Creating a basic test graph for max flow with only edge capacities (mincost=maxcost=1, supply=0 are necessary)
```python3
G, sources, sinks = gen_graph_max_flow(mincost=1, maxcost=1, supply=0, mincap=5, maxcap=10, fname="test.net")
```

### With demand (mincost and maxcost must be different, supply non-zero)
```python3
G, sources, sinks = gen_graph_min_cost(mincost=10, maxcost=20, supply=100, mincap=5, maxcap=10, fname="test.net")
```

### Get the sink max flow values
```python3
# store the max flow graph in G ...
max_flow_vals = calc_max_flow_vals(G, sinks)
```

### Draw the graph
```python3
# draw the test graph
md.draw(G)

# draw the max flow graph
md.draw(G, "flow")
```

### Probabilistic edge removal max flow computation
```python3
# set all vertex capacities to 10
for n in G.nodes:
    G.nodes[n]["capacity"] = 10

# set removal probability of all edges to 10%
for e in G.edges:
    G.edges[e]["blocking_prob"] = 0.1

G_m = md.get_probabilistic_blocking_max_flow(G, sources, sinks)
```

### Probabilistic edge capacity reduction max flow computation
```python3
# set all vertex capacities to 10
for n in G.nodes:
    G.nodes[n]["capacity"] = 10

# set slowing probability of all edges to 10%
for e in G.edges:
    G.edges[e]["slowing_prob"] = 0.1

G_m = md.get_probabilistic_slowing_max_flow(G, sources, sinks, slowing_factor=0.6)
```

### Probabilistic vertex deletion max flow computation
```python3
# set all vertex capacities to 10
# set vertex deletion probability to 10%
for n in G.nodes:
    G.nodes[n]["capacity"] = 10
    G.nodes[n]["blocking_prob"] = 0.1

G_m = md.get_probabilistic_v_blocking_max_flow(G, sources, sinks)
```

Use will most likely involve calculating the max flow value for each sink a large
number of times over a probabilistic max flow computation and averaging over
to determine the effectiveness of a modification
