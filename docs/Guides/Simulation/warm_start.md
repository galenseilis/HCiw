# How to Warm-Start a Simulation

By default a simulation starts empty: individuals only enter the system through
the arrival process once the simulation begins. A **warm start** instead seeds
the simulation with a backlog of individuals who are already present at time
zero. This is useful when the system being modelled is already busy, for
example a hospital whose current patients are known from historical data.

The `hciw.waitlist.create_existing_customers_from_list` function takes a
backlog and a simulation, and places each backlogged individual at a node. Each
row of the backlog is a list of four items:

| Position | Meaning |
| --- | --- |
| 0 | The individual's unique identifier |
| 1 | The individual's customer class |
| 2 | The individual's historical arrival date |
| 3 | The index of the node they are waiting at |

Arrival dates should be at or before the simulation start time (that is, less
than or equal to zero). The time an individual spent waiting before the
simulation began is then included in their waiting-time statistics, while their
service starts at time zero.

``` python
>>> import hciw
>>> N = hciw.create_network(
...     arrival_distributions=[hciw.dists.Deterministic(10)],
...     service_distributions=[hciw.dists.Deterministic(5)],
...     number_of_servers=[1],
... )
>>> Q = hciw.Simulation(N)
>>> hciw.waitlist.create_existing_customers_from_list([
...     [1, 'Customer', -7, 1],
...     [2, 'Customer', -3, 1],
... ], Q)

The server is free at time zero, so the first backlogged individual enters
service immediately. The second waits until the server is free. Their waiting
times reflect the time they had already spent waiting before the simulation
started:

``` python
>>> Q.simulate_until_max_time(30)
>>> recs = Q.get_all_records()
>>> for rec in recs[:2]:
...     print(rec.id_number, rec.waiting_time)
1 7
2 8

Individuals seeded from the backlog are given the identifiers supplied in the
backlog. The arrival node's counters are advanced past those identifiers, so
later arrivals are not assigned a duplicate identifier:

``` python
>>> for rec in recs[2:3]:
...     print(rec.id_number, rec.arrival_date)
3 10

Warm-starts should be applied to the simulation *before* it is run. Calling
`hciw.waitlist.create_existing_customers_from_list` resets the simulation's
current time to zero, so it must not be called on a simulation that has already
progressed.
