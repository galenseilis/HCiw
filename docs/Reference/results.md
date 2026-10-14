<a id="refs-results"></a>

# List of Available Results

Each time an individual completes service at a service station, a data record of that service is kept. Data records are Named Tuples with the following attributes:

| Attribute | Description |
|----|----|
| `id_number` | The unique identification number for that customer. |
| `customer_class` | The number of that customer's customer class. If dynamic customer classes are used, this is the customer's class that they were when they received service at that node. |
| `original_customer_class` | The number of the customer's class when they arrived at the node. |
| `node` | The number of the node at which the service took place. |
| `arrival_date` | The date of arrival to that node, the date which the customer joined the queue. |
| `waiting_time` | The amount of time the customer spent waiting for service at that node. |
| `service_start_date` | The date at which service began at that node. |
| `service_time` | The amount of time spent in service at that node. |
| `service_end_date` | The date which the customer finished their service at that node. |
| `time_blocked` | The amount of time spent blocked at that node. That is the time between finishing service at exiting the node. |
| `exit_date` | The date which the customer exited the node. This may be immediately after service if no blocking occured, or after some period of being blocked. |
| `destination` | The number of the customer's destination, that is the next node the customer will join after leaving the current node. If the customer leaves the system, this will be -1. |
| `queue_size_at_arrival` | The size of the queue at the customer's arrival date. Does not include the individual themselves. |
| `queue_size_at_departure` | The size of the queue at the customer's exit date. Does not include the individual themselves. |
| `server_id` | The unique identification number of the server that served that customer. |
| `record_type` | Indicates what type of data record this is. See below. |

The attribute `record_type` can be one of:  
- `"service"`: a completed service
- `"interrupted service"`: an interrupted service
- `"renege"`: the waiting time while a customer waited before reneging
- `"baulk"`: the record of a customer baulking
- `"rejection"`: the record of a customer being rejected due to the queue being full

You may access these records as a list of named tuples, using the Simulation's `get_all_records` method:

``` python
>>> recs = Q.get_all_records() # doctest:+SKIP
```

By default, all record types are included. However, we may only want some of the record types, and these can be filtered by passing a list of desired record types to the `only` keyword argument. For example, to only receive service and reneging customers, we can use:

``` python
>>> recs = Q.get_all_records(only=["service", "renege"]) # doctest:+SKIP
```
