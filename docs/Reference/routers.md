<a id="refs-routing"></a>

# List of Routing Objects

HCiw allows a number network router objects and node router objects. The following network routers are currently supported:

- [The General Network Router](#network_router)
- [The Transition Matrix Router](#trans_mat)
- [The Process Based Router](#pb_route)
- [The Flexible Process Based Routed](#pb_flex)

The following node routers are currently supported:

- [Leave](#leave)
- [Direct](#direct)
- [Probabilistic](#probabilistic)
- [Join Shortest Queue](#jsq)
- [Load Balancing](#load_balancing)
- [Cycle](#cycle)

## Network Routing Objects

<a id="network_router"></a>

### The General Network Router

The general network router allows us to define separate node routing objects for each node. For a two node network:

``` python
hciw.routing.NetworkRouting(
    routers=[
        hciw.routing.NodeRouting(), # should be replaced with one of the node routers below
        hciw.routing.NodeRouting(), # should be replaced with one of the node routers below
        hciw.routing.NodeRouting()  # should be replaced with one of the node routers below
    ]
)
```

<a id="trans_mat"></a>

### The Transition Matrix Router

The [transition matrix](../Guides/Routing/transition_matrix.md#transition-matrix) router takes in a transition matrix, a list of lists, with elements $R_{ij}$ representing the probability of entering node $j$ after service at node $i$. For a two node network:

``` python
hciw.routing.TransitionMatrix(
    transition_matrix=[
        [0.2, 0.8],
        [0.0, 0.3]
    ]
)
```

<a id="pb_route"></a>

### The Process Based Router

The [process based](../Guides/Routing/process_based.md#process-based) router takes in a function that returns a pre-defined list of destinations that a customer will follow in order. E.g. all routing where all customers go to Node 2, then Node 1, then Node 1 again:

``` python
hciw.routing.ProcessBased(
    routing_function=lambda ind, simulation: [2, 1, 1]
)
```

<a id="pb_flex"></a>

### The Flexible Process Based Routed

The flexible process based router is an extension of the above process based router, where the routing function gives a list of sets (defined by lists). For example:

``` python
hciw.routing.FlexibleProcessBased(
    routing_function=lambda ind, simulation: [[2, 1], [1], [1, 2, 3]],
    rule='any',
    choice='jsq'
)
```

Arguments:  
- The `rule` argument can take one of two strings: `'any'` or `'all'`. For each set of nodes in the pre-defined route, using `'any'` means that the customer must visit only one of the nodes in the set; while using `'all'` means that the customer should visit all the nodes in that set, but not necessarily in that order.

- The `choice` argument can take one of a number of strings. When using the `'any'` rule, it determines how a node is chosen from the set. When using the `'all'` rule, it determines at each instance, the choice of next node out of the set. The current options are:  
  - `'random'`: randomly chooses a node from the set.
  - `'jsq'`: chooses the node with the smallest queue from the set (like the [join-shortest-queue](#jsq) router).
  - `'lb'`: chooses the node with the least number of customers present from the set (like the [load-balancing](#load_balancing) router).

## Node Routing Objects

### Leave

Leaves the system after service at the node:

``` python
hciw.routing.Leave()
```

### Direct

The customer goes direct to another node after service at the node. E.g. going to Node 2 direct form the node:

``` python
hciw.routing.Direct(to=2)
```

### Probabilistic

The customer is routed to another node probabilistically after service at the node. E.g. going to Node 1 with probability 0.4, and Node 3 with probability 0.1:

``` python
hciw.routing.Probabilistic(
    destinations=[1, 3],
    probs=[0.4, 0.1]
)
```

<a id="jsq"></a>

### Join Shortest Queue

The customer goes [joins the shortest queue](../Guides/Routing/join_shortest_queue.md#join-shortest-queue) out of a subset of destinations:

``` python
hciw.routing.JoinShortestQueue(destinations=[1, 3], tie_break='random')
```

The `tie_break` argument is optional, and can take one of two strings: `'random'` or `'order'`. When there is a tie between the nodes with the shortest queue, tie breaks are either dealt with by choosing randomly between the ties (`'random'`), or take precedence by the order listed in the `destinations` list (`'order'`). If omitted, random tie-breaking is used.

<a id="load_balancing"></a>

### Load Balancing

The customer goes [joins the node with the least amount of customers present](../Guides/Routing/join_shortest_queue.md#example_lb) out of a subset of destinations:

``` python
hciw.routing.LoadBalancing(destinations=[1, 3], tie_break='random')
```

The `tie_break` argument is optional, and can take one of two strings: `'random'` or `'order'`. When there is a tie between the nodes with the least amount of customers present, tie breaks are either dealt with by choosing randomly between the ties (`'random'`), or take precedence by the order listed in the `destinations` list (`'order'`). If omitted, random tie-breaking is used.

### Cycle

The customers' destinations out of the node cycles through a given list. For example, the first customer is routed to Node 1, the second to Node 1, the third to Node 3, the fourth to Node 2, then henceforth the order cycles, so the fifth is routed to Node 1, the sixth to Node 1, and so on:

``` python
hciw.routing.Cycle(cycle=[1, 1, 3, 2])
```
