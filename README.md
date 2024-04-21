
# plane-enjoyers

  

Airline network capacity optimisation.

  

## Setup

  

*Note: commands may differ*

  

- Create a virtual environment.

```bash

$  python3  -m  venv  .venv

```

  

- Activate the virtual environment and install libraries specified from 'requirements.txt'.

```bash

$  source  .venv/bin/activate

$ (.venv) pip install -r requirements.txt

```

  

## Examples

  

*Note: if using single source/sinks, you need to convert to an iterable for input*

  

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
  

### Running the modification algorithm and calculating the new max flow
1. Create the base graph (setting parameters *mincap* (min capacity), *maxcap* (max capacity), *nodes* (number of nodes), *density* (number of edges), *seed* (for random generation, use fixed to create the same graph, set -1 for random generation) appropriately).
2. Set the *slowing_prob* (value between 0 and 1 inclusive for probability of edge losing capacity) and *slowing_factor* (value between 0 and 1 inclusive representing portion of edge capacity lost if *slowing_prob* triggered) attributes for each edge.
```python3
# manually (probably shouldn't all be the same)
for  e  in  G.edges:
	G.edges[e]["slowing_prob"] =  0.05
	G.edges[e]["slowing_factor"] =  1

# randomly (using model::set_random_probabilistic_attrs)
model.set_random_probabilistic_attrs(G)
```
3. Calculate the initial *static* max flow value and get the resultant residual graph (which includes supersource *"source"* and supersink *"sink"*) using *model::get_intermediate_residual_graph*. When testing, should calculate the initial probabilistic max flow value by averaging probabilistic max flow calculations over 10000+ iterations.
```python3
orig_max_flow_val, R  =  model.get_intermediate_residual_graph(G, sources, sinks, nx.flow.preflow_push)
```
4. Apply the algorithm to get the capacity changes and the new modified residual graph using *algorithm::distribute_budget* or *algorithm::distribute_budget_fair* (you can use different *edge_select_func* and *edge_func* - see the comments for more details). Note that the original residual graph is not modified.
```python3
dist, R_c  =  algorithm.distribute_budget_fair(R, 1000, edge_func=te.get_guaranteed_edges, edge_select_func=ag.get_edge_and_cap_inc_by_ev)
```
5. Clean the modified residual graph using *model::clean_residual_graph* (this is important).
```python3
model.clean_residual_graph(R_c)
```
6. Calculate the probabilistic max flow value on the cleaned residual graph using *model::get_probabilistic_slowing_max_flow*.
```python3
new_max_flow_val = model.get_probabilistic_slowing_max_flow(R_c, sources, sinks, flow_func=md.get_max_flow_val)
```
7. Record the difference from the original to see the approximate increase (and repeat this calculation to converge on a more accurate approximation).

Alternative (from replacing from step 5)

You can just apply the capacity increases in *dist* to the original graph and average probabilistic max flow value over the new graph.
```python3
for e in dist:
	G.edges[e]["capacity"] += dist[e]
```