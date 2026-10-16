<a id="refs-params"></a>

# List of Parameters

Below is a full list of the parameters that the `create_network` function can take, along with a description of the values required.

## arrival_distributions

*Required*

Describes the inter-arrival distributions for each node and customer class. This is a dictionary, with keys as customer classes, and values are lists containing the inter-arrival distribution objects for each node. If only one class of customer is required it is sufficient to simply enter a list of inter-arrival distributions. For more details on inputting distributions, see [How to Set Arrival & Service Distributions](../Guides/Distributions/set_distributions.md#set-dists).

An example is shown:

``` python
arrival_distributions={'Class 0': [hciw.dists.Exponential(rate=2.4),
                                   hciw.dists.Uniform(lower=0.3, upper=0.5)],
                       'Class 1': [hciw.dists.Exponential(rate=3.0),
                                   hciw.dists.Deterministic(value=0.8)]}
```

An example where only one class of customer is required:

``` python
arrival_distributions=[hciw.dists.Exponential(rate=2.4),
                       hciw.dists.Exponential(rate=2.0)]
```

## batching_distributions

*Optional*

Describes the discrete distributions of size of the batch arrivals for each node and customer class. This is a dictionary, with keys as customer classes, and values are lists containing the batch distribution objects for each node. If only one class of customer is required it is sufficient to simply enter a list of batch distributions. For more details on batching, see [How to Set Batch Arrivals](../Guides/Arrivals/batching.md#batch-arrivals).

An example is shown:

``` python
batching_distributions={'Class 0': [hciw.dists.Deterministic(value=1),
                                    hciw.dists.Sequential(sequence=[1, 1, 2])],
                        'Class 1': [hciw.dists.Deterministic(value=3),
                                    hciw.dists.Deterministic(value=2)]}
```

An example where only one class of customer is required:

``` python
batching_distributions=[hciw.dists.Deterministic(value=2),
                        hciw.dists.Deterministic(value=1)]
```

## baulking_functions

*Optional*

A dictionary of baulking functions for each customer class and each node. It describes the baulking mechanism of the customers. For more details see [How to Simulate Baulking Customers](../Guides/CustomerBehaviour/baulking.md#baulking-functions). If left out, then no baulking occurs.

Example:

``` python
baulking_functions={'Class 0': [probability_of_baulking]}
```

## class_change_matrices

*Optional*

A dictionary of class change matrices for each node. For more details see [How to Change Customer Class After Service](../Guides/CustomerClasses/change-class-after-service.md#changeclass-afterservice).

An example for a two node network with two classes of customer:

``` python
class_change_matrices=[
    {'Class 0': {'Class 0': 0.3, 'Class 1': 0.4, 'Class 2': 0.3},
     'Class 1': {'Class 0': 0.1, 'Class 1': 0.9, 'Class 2': 0.0},
     'Class 2': {'Class 0': 0.5, 'Class 1': 0.1, 'Class 2': 0.4}},
    {'Class 0': {'Class 0': 1.0, 'Class 1': 0.0, 'Class 2': 0.0},
     'Class 1': {'Class 0': 0.4, 'Class 1': 0.5, 'Class 2': 0.1},
     'Class 2': {'Class 0': 0.2, 'Class 1': 0.2, 'Class 2': 0.6}}
]
```

## class_change_time_distributions

*Optional*

A dictionary of distributions representing the time it takes to change from one class into another while waiting. For more details see [How to Change Customer Class While Queueing](../Guides/CustomerClasses/change-class-while-queueing.md#changeclass-whilequeueing).

An example of a two class network where customers of class 0 change to customers of class 1 according to an exponential distribution:

``` python
class_change_dist_dict = {
    'Class 0': {'Class 1': hciw.dists.Exponential(rate=5)}
}
```

## customer_class_benchmarks

*Optional*

A dictionary mapping each customer class to a numerical target maximum waiting time (its *benchmark*). The benchmark is read by the benchmark-aware service disciplines, such as [`wait_time_over_benchmark`](../Guides/Services/service_disciplines.md#benchmark-service-disciplines), which serves the customer furthest past their own class's benchmark next. Classes with no benchmark are given a value of `None`.

Example of a two class network where class 0 has a target wait of 1 time unit and class 1 a target of 5:

``` python
customer_class_benchmarks={'Class 0': 1.0,
                           'Class 1': 5.0}
```

## number_of_servers

*Required*

A list of the number of parallel servers at each node. If a server schedule is used, the schedule is given instead of a number. For more details on server schedules, see [How to Set Server Schedules](../Guides/Services/server_schedule.md#server-schedule). A value of `float('inf')` may be given is infinite servers are required.

Example:

``` python
number_of_servers=[1, 2, float('inf'), 1, [[1, 10], [2, 15]]]
```

## priority_classes

*Optional*

A dictionary mapping customer classes to priorities. For more information see [How to Set Priority Classes](../Guides/CustomerClasses/priority.md#priority-custs). If left out, no priorities are used, that is all customers have equal priorities.

Example:

``` python
priority_classes={'Class 0': 0,
                  'CLass 1': 1,
                  'Class 2': 1}
```

## ps_thresholds

A list of thresholds for capacitated processor sharing queues. For more information see [How to Simulate Processor Sharing](../Guides/Services/processor-sharing.md#processor-sharing).

Example:

``` python
ps_thresholds=[3]
```

## queue_capacities

*Optional*

A list of maximum queue capacities at each node. If omitted, default values of `float('inf')` for every node are given. For more details see [How to Set Maximium Queue Capacities](../Guides/Queues/queue_capacities.md#queue-capacities).

Example:

``` python
queue_capacities=[5, float('inf'), float('inf'), 10]
```

## reneging_destinations

*Optional*

A dictionary of lists representing the destination a customer goes to when they renege, or abandon the queue, while waiting. For more details see [How to Simulate Reneging Customers](../Guides/CustomerBehaviour/reneging.md#reneging-customers).

An example of a one node, two class network where customers of class 0 renege to node 2, and customers of class 1 renege and leave the system:

``` python
reneging_destinations = {
    'Class 0': [2],
    'Class 1': [-1]
}
```

## reneging_time_distributions

*Optional*

A dictionary of distributions representing the time it takes for a customer to renege, or abandon the queue, while waiting. For more details see [How to Simulate Reneging Customers](../Guides/CustomerBehaviour/reneging.md#reneging-customers).

An example of a one node, two class network where customers of class 0 renege after a 5 time units, and customers of class 1 do not renege:

``` python
reneging_time_distributions = {
    'Class 0': [hciw.dists.Deterministic(value=5)],
    'Class 1': [None]
}
```

## routing

*Required for more than 1 node*

*Optional for 1 node*

Describes how each customer class routes around the system. This may be a routing matrix for each customer class, or a routing object, see [How to Use Routing Objects](../Guides/Routing/routing_objects.md#routing-objects).

This is a dictionary, with keys as customer classes, and values are routing objects (or lists of of lists, matrices, containing the routing probabilities). If only one class of customer is required it is sufficient to simply enter single routing object or matrix.

An example of using a routing object:

``` python
routing = hciw.routing.NetworkRouting(
    routers=[
        hciw.routing.Direct(to=2),
        hciw.routing.Leave()
    ]
)
```

And an example of using transition matrices is shown:

``` python
routing={'Class 0': [[0.1, 0.3],
                     [0.0, 0.8]],
         'Class 1': [[0.0, 1.0],
                     [0.0, 0.0]]}
```

## server_priority_functions

*Optional*

A function for each node that decides how to choose between multiple servers in the same node. For more details see [How to Set Server Priorities](../Guides/Services/server_priority.md#server-priority).

Example:

``` python
server_priority_functions=[custom_server_priority]
```

## service_disciplines

*Optional*

A list of service discipline functions, that describe the order in which customers are taken from the queue and served. For more details see [How to Change Service Discipline](../Guides/Services/service_disciplines.md#service-disciplines).

If omitted, FIFO service disciplines are assumed.

Example of a 3 node network, one using FIFO, one using LIFO, and one using SIRO:

``` python
service_disciplines=[hciw.disciplines.FIFO,
                     hciw.disciplines.LIFO,
                     hciw.disciplines.SIRO]
```

## service_distributions

*Required*

Describes the service distributions for each node and customer class. This is a dictionary, with keys as customer classes, and values are lists containing the service distribution objects for each node. If only one class of customer is required it is sufficient to simply enter a list of service distributions. For more details on inputting distributions, see [How to Set Arrival & Service Distributions](../Guides/Distributions/set_distributions.md#set-dists).

An example is shown:

``` python
service_distributions={'Class 0': [hciw.dists.Exponential(rate=4.4),
                                   hciw.dists.Uniform(lower=0.1, upper=0.9)],
                       'Class 1': [hciw.dists.Exponential(rate=6.0),
                                   hciw.dists.Lognormal(mean=0.5, sd=0.6)]}
```

An example where only one class of customer is required:

``` python
service_distributions=[hciw.dists.Exponential(rate=4.8),
                       hciw.dists.Exponential(rate=5.2)]
```

## system_capacity

*Optional*

The maximum queue capacity for the system. If omitted, a default value of `float('inf')` is given. For more details see [How to Set a Maximium Capacity for the Whole System](../Guides/Queues/system_capacity.md#system-capacity).

Example:

``` python
system_capacity=12
```
