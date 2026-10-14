<a id="reneging-customers"></a>

# How to Simulate Reneging Customers

HCiw allows customers to renege, that is leave a queue after a certain amount of time waiting for service. In HCiw, this works by sampling from a `reneging_time_distribution`, giving the date that that customer will renege if their service has not started by that time.

For example, let's say we have an [M/M/1](../../Background/kendall.md#kendall-notation), $\lambda = 5$ and $\mu = 2$, queue where customers renege if they have spend more than 6 time units in the queue:

``` python
>>> import hciw
>>> N = hciw.create_network(
...     arrival_distributions=[hciw.dists.Exponential(5)],
...     service_distributions=[hciw.dists.Exponential(2)],
...     number_of_servers=[1],
...     reneging_time_distributions=[hciw.dists.Deterministic(6)]
... )

>>> hciw.seed(0)
>>> Q = hciw.Simulation(N, exact=5)
>>> Q.simulate_until_max_time(10)
```

Reneging events are recorded as `DataRecords` and so are collected along with service records with the `get_all_records` method. They are distinguished by the `record_type` field (services have `service` record type, while reneging events have `renege` record types).

For the above example, we see that no customer receiving service waited longer than 6 time units, as expected. We also see that all four reneging events happened after the customer waited 6 time units:

``` python
>>> recs = Q.get_all_records()
>>> max([r.waiting_time for r in recs if r.record_type == 'service'])
Decimal('5.8880')

>>> [r.waiting_time for r in recs if r.record_type == 'renege']
[Decimal('6.0000'), Decimal('6.0000'), Decimal('6.0000'), Decimal('6.0000')]
```

By default, when a customer reneges, they leave the network, that is they are sent to the exit node.

**Note**: Similarly to all other customer-level keyword arguments, `reneging_time_distributions` can take either a list of distributions indicating which reneging distribution to use at each node in the network; or dictionary mapping customer classes to these lists, allowing different reneging time distributions for each customer class.
