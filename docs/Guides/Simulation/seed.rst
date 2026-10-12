.. _set-seed:

=================
How to Set a Seed
=================

To ensure reproducibility of results users can set a seed for all the random number streams that HCiw uses.
This can be done using the HCiw functon :code:`hciw.seed`::
    
    >>> import hciw
    >>> hciw.seed(5)

Note that due to sampling on initialisation, the seed will need to be set **before** the :code:`hciw.Simulation` object is created.

As an example, take the following network::

    >>> N = hciw.create_network(
    ...     arrival_distributions=[hciw.dists.Exponential(rate=5)],
    ...     service_distributions=[hciw.dists.Exponential(rate=10)],
    ...     number_of_servers=[1]
    ... )

Now let's run the system for 20 time units, using a seed of 1, and get the average waiting time::

    >>> hciw.seed(1)
    >>> Q = hciw.Simulation(N)
    >>> Q.simulate_until_max_time(20)
    >>> waits = [r.waiting_time for r in Q.get_all_records()]
    >>> sum(waits)/len(waits)
    0.0824058654563...

Using the same seed again, the exact same average waiting time result will occur::

    >>> hciw.seed(1)
    >>> Q = hciw.Simulation(N)
    >>> Q.simulate_until_max_time(20)
    >>> waits = [r.waiting_time for r in Q.get_all_records()]
    >>> sum(waits)/len(waits)
    0.0824058654563...

Now using a different seed, a different result will occur::

    >>> hciw.seed(2)
    >>> Q = hciw.Simulation(N)
    >>> Q.simulate_until_max_time(20)
    >>> waits = [r.waiting_time for r in Q.get_all_records()]
    >>> sum(waits)/len(waits)
    0.1691349404558...
