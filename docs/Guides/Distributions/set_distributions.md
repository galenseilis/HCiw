<a id="set-dists"></a>

# How to Set Arrival & Service Distributions

HCiw offeres a variety of inter-arrival and service time distributions. A full list can be found [here](../../Reference/distributions.md#refs-dists). They are objects, that are defined in the `Network` with the `'arrival_distributions'` and `'service_distributions'` keywords.

- `'arrival_distributions'`: This is the distribution that inter-arrival times are drawn from. That is the time between two consecutive arrivals. It is particular to specific nodes and customer classes.
- `'service_distributions'`: This is the distribution that service times are drawn from. That is the amount of time a customer spends with a server (independent of how many servers there are). It is particular for to specific node and customer classes.

The following example, with two nodes and two customer classes, uses eight different arrival and service rate distributions:

``` python
>>> import hciw
>>> N = hciw.create_network(
...     arrival_distributions={'Class 0': [hciw.dists.Deterministic(value=0.4),
...                                        hciw.dists.Empirical(observations=[0.1, 0.1, 0.1, 0.2])],
...                            'Class 1': [hciw.dists.Deterministic(value=0.2),
...                                        hciw.dists.Pmf(values=[0.2, 0.4], probs=[0.5, 0.5])]},
...     service_distributions={'Class 0': [hciw.dists.Exponential(rate=6.0),
...                                        hciw.dists.Lognormal(mean=-1, sd=0.5)],
...                            'Class 1': [hciw.dists.Uniform(lower=0.1, upper=0.7),
...                                        hciw.dists.Triangular(lower=0.2, mode=0.3, upper=0.7)]},
...     routing={'Class 0': [[0.0, 0.0], [0.0, 0.0]],
...              'Class 1': [[0.0, 0.0], [0.0, 0.0]]},
...     number_of_servers=[1, 1]
... )
```

We'll run this (in [exact](../Simulation/exact.md#exact-arithmetic) mode) for 25 time units:

``` python
>>> hciw.seed(10)
>>> Q = hciw.Simulation(N, exact=10)
>>> Q.simulate_until_max_time(50)
>>> recs = Q.get_all_records()
```

The system uses the following eight distribution objects:

- `hciw.dists.Deterministic(value=0.4)`:  
  - Always sample 0.4.

- `hciw.dists.Deterministic(value=0.2)`:  
  - Always sample 0.2.

- `hciw.dists.Empirical(observations=[0.1, 0.1, 0.1, 0.2])`:  
  - Randomly sample from the numbers 0.1, 0.1, 0.1 and 0.2.

- `hciw.dists.Pmf(values=[0.2, 0.4], probs=[0.5, 0.5])`:  
  - Sample 0.2 half the time, and 0.4 half the time.

- `hciw.dists.Exponential(rate=6.0)`:  
  - Sample from the [exponential](https://en.wikipedia.org/wiki/Exponential_distribution) distribution with parameter $\lambda = 6.0$. Expected mean of 0.1666...

- `hciw.dists.Uniform(lower=0.1, upper=0.7)`:  
  - Sample any number between 0.1 and 0.7 with equal probablity. Expected mean of 0.4.

- `hciw.dists.Lognormal(mean=-1, sd=0.5)`:  
  - Sample from the [lognormal](https://en.wikipedia.org/wiki/Log-normal_distribution) distribution with parameters $\mu = -1$ and $\sigma = 0.5$. Expected mean of 0.4724...

- `hciw.dists.Triangular(lower=0.2, mode=0.3, upper=0.7)`:  
  - Sample from the [triangular](https://en.wikipedia.org/wiki/Triangular_distribution) distribution, with mode 0.3, lower limit 0.2 and upper limit 0.7. Expected mean of 0.4.

From the records, collect the service times and arrival dates for each node and each customer class:

``` python
>>> servicetimes_n1c0 = [r.service_time for r in recs if r.node==1 and r.customer_class=='Class 0']
>>> servicetimes_n2c0 = [r.service_time for r in recs if r.node==2 and r.customer_class=='Class 0']
>>> servicetimes_n1c1 = [r.service_time for r in recs if r.node==1 and r.customer_class=='Class 1']
>>> servicetimes_n2c1 = [r.service_time for r in recs if r.node==2 and r.customer_class=='Class 1']
>>> arrivals_n1c0 = sorted([r.arrival_date for r in recs if r.node==1 and r.customer_class=='Class 0'])
>>> arrivals_n2c0 = sorted([r.arrival_date for r in recs if r.node==2 and r.customer_class=='Class 0'])
>>> arrivals_n1c1 = sorted([r.arrival_date for r in recs if r.node==1 and r.customer_class=='Class 1'])
>>> arrivals_n2c1 = sorted([r.arrival_date for r in recs if r.node==2 and r.customer_class=='Class 1'])
```

Now let's see if the mean service time and inter-arrival times of the simulation matches the distributions:

``` python
>>> from decimal import Decimal

>>> sum(servicetimes_n1c0) / len(servicetimes_n1c0) # Expected 0.1666...
Decimal('0.1600313200')

>>> sum(servicetimes_n2c0) / len(servicetimes_n2c0) # Expected 0.4724...
Decimal('0.4250531396')

>>> sum(servicetimes_n1c1) / len(servicetimes_n1c1) # Expected 0.4
Decimal('0.4108660556')

>>> sum(servicetimes_n2c1) / len(servicetimes_n2c1) # Expected 0.4
Decimal('0.3942034906')

>>> set([r2-r1 for r1, r2 in zip(arrivals_n1c0, arrivals_n1c0[1:])]) # Should only sample 0.4
{Decimal('0.4')}

>>> set([r2-r1 for r1, r2 in zip(arrivals_n1c1, arrivals_n1c1[1:])]) # Should only sample 0.2
{Decimal('0.2')}

>>> expected_samples = {Decimal('0.2'), Decimal('0.1')} # Should only sample 0.1 and 0.2
>>> set([r2-r1 for r1, r2 in zip(arrivals_n2c0, arrivals_n2c0[1:])]) == expected_samples
True

>>> expected_samples = {Decimal('0.2'), Decimal('0.4')}#  Should only sample 0.2 and 0.4
>>> set([r2-r1 for r1, r2 in zip(arrivals_n2c1, arrivals_n2c1[1:])]) == expected_samples
True
```

​

## Custom Distributions

A distribution is defined by inheriting from the generic `hciw.dists.Distribution` class. This allows users to define their own distributions.

Consider a distribution that samples the value `3.0` 50% of the time, and samples a uniform random number between 0 and 1 otherwise. That is written by inheriting from the generic class, and defining a new `sample` method:

``` python
>>> import random
>>> class CustomDistribution(hciw.dists.Distribution):
...     def sample(self, t=None, ind=None):
...         if random.random() < 0.5:
...             return 3.0
...         return random.random()
```

This can then be implemented into a `Network` object in the usual way.
