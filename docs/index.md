# Welcome to HCiw

**HCiw** is a discrete-event simulation (DES) library for **open queueing
networks**. Describe a system of servers, buffers, and customers — where
"customers" may be patients, telephone calls, jobs, or data packets — and HCiw
advances it event by event and records what happens, so that waiting times,
queue lengths, and utilisation can be estimated when closed-form queueing theory
does not apply.

HCiw is a fork of the [Ciw](https://github.com/CiwPython/Ciw) queueing-network
simulation library and continues the Ciw 3.2.7 codebase under the same MIT
licence. The name **HCiw** takes the **H** from healthcare (the project was
originally a healthcare-oriented wrapper around Ciw) and combines it with
**Ciw**, the Welsh word for a queue.

## The model and the algorithm

A queueing node is described using [Kendall's notation](Background/kendall.md):
inter-arrival times, service times, the number of servers, capacity, population,
and queueing discipline. Nodes are joined by [routing](Guides/Routing/index.md)
to form a network. Because arrivals and services are random, the quantities of
interest — waiting times, queue lengths, utilisation — are random variables, and
simulation estimates their distributions or long-run averages
[SR14](Background/references.md#SR14).

HCiw uses the **event-scheduling** approach: the clock jumps from one event
(an arrival, a service completion, a shift change) to the next, rather than
advancing in fixed steps. This is explained in the
[Overview](Background/overview.md) and
[Notes on HCiw's Mechanisms](Background/mechanisms.md); the
[glossary](Reference/glossary.md) defines the terminology used throughout.

Analytical results — [Jackson's theorem](Background/references.md#JJ57) for
exponential networks, [Little's law](Background/references.md#Lit61), and the
Erlang formulae — cover only the simplest models. HCiw is built for everything
beyond them: general distributions, finite buffers and
[blocking](Tutorial/tutorial_iii.md), priorities, baulking and reneging,
[time-varying demand](Guides/Distributions/time_dependent.md), schedules, and
state-dependent behaviour.

## Who it is for

- **Researchers** in operations research, industrial engineering, computer
  science, and applied probability, who need a programmable, reproducible
  simulator.
- **Practitioners** in healthcare, telecommunications, manufacturing, and
  service operations, evaluating a system before changing it.
- **Teachers and students**, as a readable implementation accompanying a course
  in simulation or queueing theory.

## A first simulation

```python
import hciw

N = hciw.create_network(
    arrival_distributions=[hciw.dists.Exponential(rate=0.2)],
    service_distributions=[hciw.dists.Exponential(rate=0.1)],
    number_of_servers=[3],
)

hciw.seed(1)
Q = hciw.Simulation(N)
Q.simulate_until_max_time(1440)

recs = Q.get_all_records()
waits = [r.waiting_time for r in recs]
print(sum(waits) / len(waits))
```

## Explore the documentation

The documentation follows the [Diátaxis](https://diataxis.fr/) structure:

- [**Tutorials**](Tutorial/index.md) — learning-oriented, start with
  [Getting Started](Tutorial/GettingStarted/index.md).
- [**Guides**](Guides/index.md) — task-oriented, e.g.
  [how to warm-start a simulation](Guides/Simulation/warm_start.md).
- [**Reference**](Reference/index.md) — the API, parameters, results, and
  distributions.
- [**Background**](Background/index.md) — explanation, including the
  [Overview](Background/overview.md) of the model and
  [applications in research and industry](Background/overview.md#applications-in-research-and-industry).

## Citing and contributing

To cite the library, please cite the underlying Ciw library — see
[Citing the Library](Project/citation.md). Installation instructions are in
[Installing HCiw](Guides/installation.md), and the full list of sources cited
here is in the [Bibliography](Background/references.md#bibliography-page).

HCiw is currently supported for and regularly tested on Python 3.12.
