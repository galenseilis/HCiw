<a id="service-disciplines"></a>

# How to Change Service Discipline

Service disciplines determine the order in which customers are served when waiting in the queue. By default, HCiw assumes a First In First Out (FIFO) service, that is, customers are served in the order they arrive in. HCiw does also allow other service disciplines, for example [priority classes](../CustomerClasses/priority.md#priority-custs) can be set where some classes of customer are server before other classes, regardless of their arrival dates. Note also that [processor sharing](processor-sharing.md#processor-sharing), another service discipline, is available in HCiw, but is implemented in a different way.

HCiw allows for different service disciplines to be used at different nodes. These are implemented by using service discipline functions. There are three pre-written functions available for users that order the queue by arrival position:

- **FIFO**: 'First in first out' (or alternatively 'First come first served'). Here the customer who arrived first is served next. To implement this use `hciw.disciplines.FIFO`.
- **LIFO**: 'Last in first out' (or alternatively 'Last in first served'). Here customer who arrived most recently is served next. This is also sometimes called a 'stack'. To implement this use `hciw.disciplines.LIFO`.
- **SIRO**: 'Service in random order'. Here the a customer is chosen randomly to be served next. To implement this use `hciw.disciplines.SIRO`.

A fourth, benchmark-aware discipline, `hciw.disciplines.wait_time_over_benchmark`, orders the queue by how far each customer is past a per-class target wait; it is described [below](#benchmark-service-disciplines).

As an example, say we have a three node network, and we want to use FIFO discipline at node 1, LIFO at node 2, and SIRO at node 3, then we would create a network using the `service_disciplines` keyword:

``` python
>>> import hciw
>>> N = hciw.create_network(
...     arrival_distributions=[hciw.dists.Exponential(rate=5),
...                            hciw.dists.Exponential(rate=5),
...                            hciw.dists.Exponential(rate=5)],
...     service_distributions=[hciw.dists.Exponential(rate=10),
...                            hciw.dists.Exponential(rate=10),
...                            hciw.dists.Exponential(rate=10)],
...     service_disciplines=[hciw.disciplines.FIFO,
...                          hciw.disciplines.LIFO,
...                          hciw.disciplines.SIRO],
...     number_of_servers=[1, 1, 1],
...     routing=[[0.0, 0.5, 0.5],
...              [0.0, 0.0, 0.5],
...              [0.0, 0.0, 0.0]]
... )
```

**Note:** When using priority classes, service disciplines come into effect *within* a given priority class, but all customers of a higher priority class will be served before any customer of a lower priority service class, whatever service discipline is chosen.

## Benchmark Service Disciplines

A *benchmark* is a target maximum waiting time for a customer class. Benchmarks are set with the `customer_class_benchmarks` keyword, a dictionary mapping each class name to a number. The `wait_time_over_benchmark` discipline then serves the customer furthest past their own class's benchmark next, so that any wait beyond a class's target becomes a first claim on the next free server. This is one way to model a service target such as "no one should wait more than X time units".

For example, here class `'Red'` has a tight one time unit target and class `'Blue'` a loose ten time unit target:

``` python
>>> import hciw
>>> N = hciw.create_network(
...     arrival_distributions={'Blue': [hciw.dists.Exponential(rate=3)],
...                            'Red': [hciw.dists.Exponential(rate=3)]},
...     service_distributions={'Blue': [hciw.dists.Exponential(rate=4)],
...                            'Red': [hciw.dists.Exponential(rate=4)]},
...     number_of_servers=[1],
...     service_disciplines=[hciw.disciplines.wait_time_over_benchmark],
...     customer_class_benchmarks={'Blue': 10.0, 'Red': 1.0},
... )
>>> N.customer_classes['Red'].benchmark
1.0
```

If any customer class reaching a node that uses this discipline has no benchmark, the simulation raises a `ValueError`.

## Custom Disciplines

Other service disciplines can also be implemented by writing a custom service discipline function. These functions take in a list of individuals, and the current time, and returns an individual from that list that represents the next individual to be served. As this is a list of individuals, we can access the individuals' attributes when making the service discipline decision.

For example, say we wish to implement a service discipline that chooses the customers randomly, but with probability proportional to their arrival order, we could write:

``` python
>>> def SIRO_proportional(individuals, t):
...     n = len(inds)
...     denominator = (n * (n + 1)) / 2
...     probs = [(n - i) / denominator for i in range(n)]
...     return hciw.random_choice(individuals, probs=probs)
```
