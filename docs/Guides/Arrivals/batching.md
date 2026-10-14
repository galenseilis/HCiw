<a id="batch-arrivals"></a>

# How to Set Batch Arrivals

HCiw allows batch arrivals, that is more than one customer arriving at the same time. This is implemented using the `batching_distributions`. Similar to `arrival_distributions` and `service_distributions`, this takes in distribution objects for each node and customer class that will sample the size of the batch. Only discrete distributions are allowed, that is distributions that sample integers.

Let's show an example:

``` python
>>> import hciw
>>> N = hciw.create_network(
...     arrival_distributions=[hciw.dists.Deterministic(value=18.5)],
...     service_distributions=[hciw.dists.Deterministic(value=3.0)],
...     batching_distributions=[hciw.dists.Deterministic(value=3)],
...     number_of_servers=[1]
... )
```

If this system is simulated for 30 time units, only one arrival event will occur. However, 3 customers will arrive at that node simultaneously. As there is only one server, two of those customers will have to wait:

``` python
>>> Q = hciw.Simulation(N)
>>> Q.simulate_until_max_time(30.0)
>>> recs = Q.get_all_records()

>>> [r.arrival_date for r in recs]
[18.5, 18.5, 18.5]
>>> [r.waiting_time for r in recs]
[0.0, 3.0, 6.0]
```

Just like arrival and service distributions, batching distributions can be defined for multiple nodes and multiple customer classes, using lists and dictionaries:

``` python
batching_distributions={
    'Class 0': [hciw.dists.Deterministic(value=3),
                hciw.dists.Deterministic(value=1)],
    'Class 1': [hciw.dists.Deterministic(value=2),
                hciw.dists.Deterministic(value=2)]},
```

Note:  
- *Only discrete distributions may be used,* currently implemented are:  
  - `Deterministic`
  - `Empirical`
  - `Pmf`
  - `Sequential`
  - `Poisson`
  - `Geometric`
  - `Binomial`

- If the keyword `batching_distributions` is omitted, then no batching is assumed. That is only one customer arrives at a time. Equivalent to `hciw.dists.Deterministic(1)`.

- If some nodes/customer classes require no batching, but others do, please use `hciw.dists.Deterministic(1)`.

- Batch arrivals may lead to [simultaneous events](../../Background/mechanisms.md#simultaneous_events), please take care.

## How to Set Time Dependent Batches

HCiw allows batching distributions to be time dependent. That is the batch size, the number of customers arriving simultaneously, is sampled from a distribution that varies with time.

Let's show an example, we wish to have batch sizes of 2 for the first 10 time units, but batch sizes of 1 thereafter. Define a time dependent batching distribution by inheriting from the generic `Distribution` object:

``` python
>>> class TimeDependentBatches(hciw.dists.Distribution):
...     def sample(self, t, ind=None):
...         if t < 10.0:
...             return 2
...         return 1
```

This requires a `sample` method, that taking in the parameter `t`, the current time.

Now use this when defining a network:

``` python
>>> import hciw
>>> N = hciw.create_network(
...     arrival_distributions=[hciw.dists.Deterministic(value=3.0)],
...     service_distributions=[hciw.dists.Deterministic(value=0.5)],
...     batching_distributions=[TimeDependentBatches()],
...     number_of_servers=[1]
... )
```

We'll simulate this for 16 time units. Now at times 3, 6, and 9 we would expect 2 customers arriving (a total of 6). And at times 12 and 15 we would expect 1 customer arriving (a total of 2). So 8 customers in total should finish service:

``` python
>>> Q = hciw.Simulation(N)
>>> Q.simulate_until_max_time(16.0)
>>> len(Q.nodes[-1].all_individuals)
8
```
