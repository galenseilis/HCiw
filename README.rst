HCiw
====

A discrete event simulation library for open queueing networks, forked from `Ciw <https://github.com/CiwPython/Ciw>`_.
------------------------------------------------------------------------------------------------------------------------

.. image:: https://img.shields.io/badge/docs-GitHub%20Pages-blue
   :target: https://galenseilis.github.io/HCiw/
   :alt: Documentation

HCiw simulates **queueing networks** — systems of servers, buffers, and customers (patients, telephone calls, jobs, data packets) whose behaviour is driven by randomness. Given a description of arrivals, service, routing, capacity, and customer behaviour, HCiw advances the system event by event and records what happens, so that performance measures such as waiting times, queue lengths, and utilisation can be estimated when the closed-form formulae of queueing theory do not apply.

HCiw is a fork of the `Ciw <https://github.com/CiwPython/Ciw>`_ library and continues its codebase under the MIT licence. Its core capabilities are networks of queues, multiple customer classes, priorities, and Type I blocking for restricted networks, with a large range of features on top (see below). The model and simulation algorithm behind the library are described in the `documentation overview <https://galenseilis.github.io/HCiw/Background/overview/>`_; the project's direction is recorded in `ROADMAP.md <ROADMAP.md>`_.

Who it is for
-------------

- **Researchers** in operations research, industrial engineering, computer science, and applied probability, who need a programmable, reproducible simulator for queueing-network models.
- **Practitioners** in healthcare, telecommunications, manufacturing, and service operations, who need to evaluate the performance of a real system before changing it.
- **Teachers and students**, as a readable implementation to accompany a course in simulation, queueing theory, or applied probability.

Quick example
-------------

To define an M/M/3 queue, with arrival rate λ = 0.2 and per-server service rate μ = 0.1::

    >>> import hciw
    >>> N = hciw.create_network(
    ...     arrival_distributions=[hciw.dists.Exponential(rate=0.2)],
    ...     service_distributions=[hciw.dists.Exponential(rate=0.1)],
    ...     number_of_servers=[3]
    ... )

Set a seed, create a Simulation object, and simulate for 1440 time units::

    >>> hciw.seed(1)
    >>> Q = hciw.Simulation(N)
    >>> Q.simulate_until_max_time(1440)

Collect the records and compute the average waiting time::

    >>> recs = Q.get_all_records()
    >>> waits = [r.waiting_time for r in recs]
    >>> sum(waits) / len(waits)
    4.2305...

A single run is one realisation of a random process; realistic analyses use
multiple replications with warm-up and cool-down periods. The
`simulation practice guide <https://galenseilis.github.io/HCiw/Background/simulationpractice/>`_
explains how, and the
`tutorials <https://galenseilis.github.io/HCiw/Tutorial/>`_ introduce the API.

What you can model
------------------

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
+ Warm starts from an existing backlog of customers

Where it is used
----------------

Queueing-network simulation is widely used across operations research and
industrial engineering. Representative applications include:

- **Healthcare** — modelling emergency departments and patient flow, where
  queueing networks have been used to design fast-track policies and reduce
  patients leaving without being seen. HCiw's warm-start facility can begin a
  simulation from a pre-existing patient backlog.
- **Call centres and service operations** — staffing decisions under
  time-varying demand, modelled with multi-server queues.
- **Telecommunications and computer networks** — dimensioning radio access
  networks, link capacities, and server pools.
- **Manufacturing and production lines** — throughput limited by finite buffers
  and blocking between machines.

These areas, with references, are surveyed in the
`documentation overview <https://galenseilis.github.io/HCiw/Background/overview/>`_.

Documentation
-------------

The full documentation is built from the `docs/ <docs/>`_ directory and
published at https://galenseilis.github.io/HCiw/. It follows the Diátaxis
structure: `tutorials <https://galenseilis.github.io/HCiw/Tutorial/>`_ for
learning, `how-to guides <https://galenseilis.github.io/HCiw/Guides/>`_ for
tasks, `reference <https://galenseilis.github.io/HCiw/Reference/>`_ for
parameters and results, and
`explanation <https://galenseilis.github.io/HCiw/Background/>`_ for the ideas
behind the library. HCiw inherits the feature surface of Ciw, whose
`documentation <https://ciw.readthedocs.io>`_ also applies.

Installation
------------

HCiw requires Python 3.12 and is managed with `uv <https://docs.astral.sh/uv/>`_ (see ``pyproject.toml`` and ``uv.lock``). The project is not yet published to PyPI; install it from source::

    git clone https://github.com/galenseilis/HCiw.git
    cd HCiw
    uv sync

Citing and contributing
-----------------------

To cite the library, please cite the underlying Ciw library; see the `citation page <https://galenseilis.github.io/HCiw/Project/citation/>`_. HCiw is a descendant of the ArC and Ciw line of queueing network simulation libraries. The `Ciw library <https://github.com/CiwPython/Ciw>`_ is released under the MIT licence; HCiw preserves that licence and credits the Ciw contributors in `AUTHORS.md <AUTHORS.md>`_ and `CHANGES.md <CHANGES.md>`_.

Contributions and a release checklist are documented in `CONTRIBUTING.md <CONTRIBUTING.md>`_ and `new_release_checklist.md <new_release_checklist.md>`_. This project was also previously a healthcare-oriented wrapper around Ciw, named HCiw; that code is archived under :code:`old/` and its future is described in `ROADMAP.md <ROADMAP.md>`_.
