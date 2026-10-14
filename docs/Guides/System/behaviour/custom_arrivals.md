# State-dependent Arrivals

In this example we will consider a network where customers are arrive to different nodes depending on the system state. We will look at a system without this behaviour first, and then the system with the desired behaviour, for comparison.

## Without desired behaviour

Consider the following two node network, where arrivals only occur at the first node, and there is a queueing capacity of 10. The second node is redundant in this scenario:

``` python
>>> import hciw
>>> from collections import Counter

>>> N = hciw.create_network(
...     arrival_distributions=[hciw.dists.Exponential(rate=6.0),
...                            None],
...     service_distributions=[hciw.dists.Exponential(rate=5.0),
...                            hciw.dists.Exponential(rate=5.0)],
...     routing=[[0.0, 0.0],
...              [0.0, 0.0]],
...     number_of_servers=[1, 1],
...     queue_capacities=[10, float('inf')]
... )
```

Now we run the system for 100 time units, and see that we get 494 services at the first node, and none at the second node:

``` python
>>> hciw.seed(1)
>>> Q = hciw.Simulation(N)
>>> Q.simulate_until_max_time(100)

>>> service_nodes = [r.node for r in Q.get_all_records(only=["service"])]
>>> Counter(service_nodes)
Counter({1: 494})
```

## With desired behaviour

We will now create a new `CustomArrivalNode` such that any customers who arrive when the first node has 10 or more customers present will be sent to the second node. First create the `CustomArrivalNode` that inherits from `hciw.ArrivalNode`, and overwrites the `send_individual` method:

``` python
>>> class CustomArrivalNode(hciw.ArrivalNode):
...     def send_individual(self, next_node, next_individual):
...         """
...         Sends the next_individual to the next_node
...         """
...         self.number_accepted_individuals += 1
...         if len(next_node.all_individuals) <= 10:
...             next_node.accept(next_individual)
...         else:
...             self.simulation.nodes[2].accept(next_individual)
```

To run the same system, we need to remove the keyword `queue_capacities` when creating a network, so that customers are not rejected before reaching the `send_individual` method:

``` python
>>> N = hciw.create_network(
...     arrival_distributions=[hciw.dists.Exponential(rate=6.0),
...                            None],
...     service_distributions=[hciw.dists.Exponential(rate=5.0),
...                            hciw.dists.Exponential(rate=5.0)],
...     routing=[[0.0, 0.0],
...              [0.0, 0.0]],
...     number_of_servers=[1, 1]
... )
```

Now rerun the same system, telling HCiw to use the new `arrival_node_class` to use. We'll see nearly that the same amount of services take place at Node 1, however rejected customers now have services taking place at Node 2:

``` python
>>> hciw.seed(1)
>>> Q = hciw.Simulation(N, arrival_node_class=CustomArrivalNode)
>>> Q.simulate_until_max_time(100)

>>> service_nodes = [r.node for r in Q.get_all_records(only=["service"])]
>>> Counter(service_nodes)
Counter({1: 503, 2: 84})
```
