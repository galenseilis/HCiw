<a id="baulking-functions"></a>

# How to Simulate Baulking Customers

HCiw allows customers to baulk (decide not join the queue) upon arrival, according to baulking functions. These functions take in a parameter `n`, the number of individuals at the node, and returns a probability of baulking.

For example, say we have an [M/M/1](../../Background/kendall.md#kendall-notation) system where customers:

- Never baulk if there are less than 3 customers in the system
- Have probability 0.5 of baulking if there are between 3 and 6 customers in the system
- Always baulk if there are more than 6 customers in the system

We can define the following baulking function:

``` python
>>> def probability_of_baulking(n, Q, next_ind, next_node):
...     if n < 3:
...         return 0.0
...     if n < 7:
...         return 0.5
...     return 1.0
```

Note that the baulking function takes four keyword parameters:  
- `n`: the number of customers currently in the queue,
- `Q`: the simulation object itself (so you have access to the whole state of the system),
- `next_ind`: the individual that we are deciding if they will baulk (so you have access to individualised baulking),
- `next_node`: the node that the individual might baulk from.

When creating the Network object we tell HCiw which node and customer class this function applies to with the `baulking_functions` keyword:

``` python
>>> import hciw
>>> N = hciw.create_network(
...      arrival_distributions={'Class 0': [hciw.dists.Exponential(rate=5)]},
...      service_distributions={'Class 0': [hciw.dists.Exponential(rate=10)]},
...      baulking_functions={'Class 0': [probability_of_baulking]},
...      number_of_servers=[1]
... )
```

When the system is simulated, the baulked customers are recorded as data records, with the attribute `record_type` set to `"baulk"`. They will also have the customers' id numbers, class, node baulked from, and time they baulked too:

``` python
>>> hciw.seed(0)
>>> Q = hciw.Simulation(N)
>>> Q.simulate_until_max_time(45.0)
>>> recs = Q.get_all_records()
>>> baulked_recs = [r for r in recs if r.record_type=="baulk"]
>>> r = baulked_recs[0]
>>> (r.id_number, r.customer_class, r.node, r.arrival_date)
(44, 'Class 0', 1, 9.45892050639...)
```

Note that baulking works and behaves differently to simply setting a queue capacity. Filling a queue's capacity results in arriving customers being *rejected* (and recorded as data records of type `"rejection"`), and transitioning customers to be blocked. Baulking on the other hand does not effect transitioning customers. This means that if you set a deterministic baulking threshold of 5, but do not set a queue capacity, then the number of individuals at that node may exceed 5, due to customers transitioning from other nodes ignoring the baulking threshold. This also means you can use baulking and limited capacities in conjunction with one another.
