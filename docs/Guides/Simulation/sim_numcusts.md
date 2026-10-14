<a id="until-numcusts"></a>

# How to Simulate For a Certain Number of Customers

A simulation run may be terminated once a certain number of customers have passed through. This can be done using the `simulate_until_max_customers` method. The method takes in a variable `max_customers`. There are three methods of counting customers:

> - `'Complete'`: Simulates until `max_customers` has reached the Exit Node due to completing their journey through the system.
> - `'Finish'`: Simulates until `max_customers` has reached the Exit Node, regardless if the customer reaches there without completing their journey, for example by [baulking](../CustomerBehaviour/baulking.md#baulking-functions) or [reneging](../CustomerBehaviour/reneging.md#reneging-customers).
> - `'Arrive'`: Simulates until `max_customers` have spawned at the Arrival Node.
> - `'Accept'`: Simulates until `max_customers` have been spawned and accepted (not rejected) at the Arrival Node.

The method of counting customers is specified with the optional keyword argument `method`. The default value is is `'Complete'`.

Consider an [M/M/1/3](../../Background/kendall.md#kendall-notation) queue:

``` python
>>> import hciw
>>> N = hciw.create_network(
...     arrival_distributions=[hciw.dists.Exponential(rate=10)],
...     service_distributions=[hciw.dists.Exponential(rate=5)],
...     number_of_servers=[1],
...     queue_capacities=[3]
... )
```

To simulate until 30 customers have completed:

``` python
>>> hciw.seed(1)
>>> Q = hciw.Simulation(N)
>>> Q.simulate_until_max_customers(30, method='Complete')
>>> recs = Q.get_all_records()
>>> len([r for r in recs if r.record_type=="service"])
30
```

To simulate until 30 customers have finished:

``` python
>>> hciw.seed(1)
>>> Q = hciw.Simulation(N)
>>> Q.simulate_until_max_customers(30, method='Finish')
>>> recs = Q.get_all_records()
>>> len(recs)
30
```

To simulate until 30 customers have arrived:

``` python
>>> hciw.seed(1)
>>> Q = hciw.Simulation(N)
>>> Q.simulate_until_max_customers(30, method='Arrive')
>>> recs = Q.get_all_records()
>>> (
...     len([r for r in recs if r.record_type=="service"]),
...     len(Q.nodes[1].all_individuals),
...     len([r for r in recs if r.record_type=="rejection"])
... )
(13, 4, 13)
```

To simulate until 30 customers have been accepted:

``` python
>>> hciw.seed(1)
>>> Q = hciw.Simulation(N)
>>> Q.simulate_until_max_customers(30, method='Accept')
>>> recs = Q.get_all_records()
>>> (
...     len([r for r in recs if r.record_type=="service"]),
...     len(Q.nodes[1].all_individuals)
... )
(27, 3)
```
