<a id="system-capacity"></a>

# How to Set a Maximium Capacity for the Whole System

We have seen that [node capacities](../../Tutorial/tutorial_iii.md#tutorial-iii) can define restricted queueing networks. HCiw also allows for a whole system capacity to be set. When a system capacity is set, when the total number of customers present in *all* the nodes of the system is equal to the system capacity, then newly arriving customers will be rejected. Once the total number of customers drops back below the system capacity, then customers will be accepted into the system again.

In order to implement this, we use the `system_capacity` keyworks when creating the network:

``` python
>>> import hciw
>>> N = hciw.create_network(
...     arrival_distributions=[hciw.dists.Exponential(rate=2),
...                            hciw.dists.Exponential(rate=1)],
...     service_distributions=[hciw.dists.Exponential(rate=1),
...                            hciw.dists.Exponential(rate=1)],
...     routing=[[0.0, 0.5],
...              [0.0, 0.0]],
...     number_of_servers=[3, 2],
...     system_capacity=4
... )
```

In this case, the total capacity of nodes 1 and 2 is 4, and the system will never have more than 4 individuals. To see this, let's run this with a [state tracker](../System/state_trackers.md#state-trackers) and see that the system never reaches more than 4 people:

``` python
>>> hciw.seed(0)
>>> Q = hciw.Simulation(N, tracker=hciw.trackers.SystemPopulation())
>>> Q.simulate_until_max_time(100)
>>> state_probs = Q.statetracker.state_probabilities()
>>> state_probs
{0: 0.03369..., 1: 0.15927..., 2: 0.18950..., 3: 0.29834..., 4: 0.31917...}
```
