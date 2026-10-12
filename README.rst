HCiw
====

A discrete event simulation library for queueing networks, forked from `Ciw <https://github.com/CiwPython/Ciw>`_.
---------------------------------------------------------------------------------------------------------------

.. image:: https://img.shields.io/badge/docs-GitHub%20Pages-blue
   :target: https://galenseilis.github.io/HCiw/
   :alt: Documentation

HCiw is a fork of the `Ciw <https://github.com/CiwPython/Ciw>`_ discrete event simulation library for open queueing networks. Development of Ciw has slowed, so HCiw takes over that codebase as its starting point in order to keep developing it. The HCiw repository is at `github.com/galenseilis/HCiw <https://github.com/galenseilis/HCiw>`_.
Its core features include the capability to simulate networks of queues, multiple customer classes, and implementation of Type I blocking for restricted networks.

HCiw is a descendant of the ArC and Ciw line of queueing network simulation libraries. The `Ciw library <https://github.com/CiwPython/Ciw>`_ is released under the MIT licence; HCiw preserves that licence and credits the Ciw contributors in `AUTHORS.rst <AUTHORS.rst>`_ and `CHANGES.rst <CHANGES.rst>`_.

This project was also previously a healthcare-oriented wrapper around Ciw, named HCiw. That code is archived under :code:`old/` and its future is described in `ROADMAP.md <ROADMAP.md>`_.

Usage
-----

Import HCiw::

    >>> import hciw

To define an M/M/3 queue, with λ = 0.2 and μ = 0.1::

    >>> N = hciw.create_network(
    ...     arrival_distributions=[hciw.dists.Exponential(rate=0.2)],
    ...     service_distributions=[hciw.dists.Exponential(rate=0.1)],
    ...     number_of_servers=[3]
    ... )

Now set a seed, create a Simulation object, and simulate for 1440 time units::

    >>> hciw.seed(1)
    >>> Q = hciw.Simulation(N)
    >>> Q.simulate_until_max_time(1440)

Collect results::

    >>> recs = Q.get_all_records()

Manipulate results to get useful statistics, e.g. average waiting time::

    >>> waits = [r.waiting_time for r in recs]
    >>> sum(waits) / len(waits)
    4.2305...


Features
--------

A number of features are implemented, including:

+ Type I blocking
+ A large range of sampling distributions
+ Phase-Type distributions
+ Time-dependent and state-dependent distributions
+ Batch arrivals
+ Baulking customers
+ Reneging customers
+ Processor sharing
+ Multiple customer classes
+ Priorities
+ Server priorities
+ Service disciplines
+ Customers changing classes while queueing
+ Customers changing classes after service
+ Server schedules
+ Slotted services
+ State tracking
+ Stopping the simulation after a certain amount of customers
+ Process-based routing
+ Logical routing
+ Deadlock detection

The full documentation is built from the `docs/ <docs/>`_ directory and the `upstream Ciw documentation <https://ciw.readthedocs.io>`_ describes the features inherited from Ciw.

Installation
------------

HCiw requires Python 3.12 and is managed with `uv <https://docs.astral.sh/uv/>`_ (see ``pyproject.toml`` and ``uv.lock``). The project is not yet published to PyPI; install it from source::

    git clone https://github.com/galenseilis/HCiw.git
    cd HCiw
    uv sync

Contributions and a release checklist are documented in `CONTRIBUTING.rst <CONTRIBUTING.rst>`_ and `new_release_checklist.md <new_release_checklist.md>`_.