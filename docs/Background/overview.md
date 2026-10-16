<a id="overview"></a>

# Overview

HCiw is a **discrete-event simulation (DES)** library for **open queueing
networks**. It lets you describe a system of servers, buffers, and customers —
where "customers" may be patients, telephone calls, jobs, vehicles, or data
packets — and then simulate its evolution over time under randomness
[PKHH19](references.md#PKHH19).

This page explains the model HCiw simulates, the algorithm it uses, and where
the approach is applied in research and industry. It is the conceptual
companion to the [tutorials](../Tutorial/index.md), the
[how-to guides](../Guides/index.md), and the
[API reference](../Reference/index.md). For the notation used below, see
[Kendall's Notation](kendall.md#kendall-notation) and the
[Bibliography](references.md#bibliography-page).

## Why simulate queues?

A queueing system is characterised by customers arriving, waiting, and being
served. When arrivals and services are random, the lengths of queues, waiting
times, and utilisation are *random variables*, and the quantities of interest
are their distributions or long-run averages.

Queueing theory provides exact answers, but only for a restricted class of
models. Simulation is the general-purpose fallback: it can represent almost any
arrival process, service-time distribution, network topology, capacity,
discipline, and form of customer behaviour, at the cost of producing statistical
rather than closed-form results [SR14](references.md#SR14),
[WS09](references.md#WS09). HCiw is designed for the cases where the textbook
formulae no longer apply.

## The queueing-network model

### A single queue

A single queueing node is described by *Kendall's notation*,
$A/B/C/X/Y/Z$ [WS09](references.md#WS09), where $A$ is the inter-arrival-time
distribution, $B$ the service-time distribution, $C$ the number of servers, $X$
the queueing capacity, $Y$ the population size, and $Z$ the queueing discipline
(see [Kendall's Notation](kendall.md#kendall-notation)).

A network is a collection of such nodes joined by a *routing* rule: on
completion of service a customer moves to another node — or leaves the system —
according to fixed probabilities, a routing object, or a custom process. This
combination of queueing nodes and routing defines an **open queueing network**.

Two structural quantities recur throughout the analysis:

- the **traffic intensity** (utilisation), for a single-server node
  $\rho = \lambda/\mu$ and for a $c$-server node $\rho = \lambda/(c\mu)$, where
  $\lambda$ is the arrival rate and $\mu$ the per-server service rate. The system
  is *stable* when $\rho < 1$; otherwise queues grow without bound.
- **Little's law**, $L = \lambda W$ [Lit61](references.md#Lit61), which relates
  the long-run average number of customers in the system, $L$, to the arrival
  rate, $\lambda$, and the average time a customer spends in the system, $W$.
  Little's law is distribution-free and holds for any system in steady state.

For the simplest models these quantities can be written in closed form. For an
$M/M/1$ queue with $\rho < 1$:

$$
L = \frac{\rho}{1 - \rho}, \qquad
W = \frac{1}{\mu - \lambda}, \qquad
W_q = \frac{\rho}{\mu - \lambda},
$$

where $W_q$ is the mean time spent waiting before service. For an $M/M/c$ queue
the Erlang-C formula gives the probability that an arriving customer must wait;
these and related formulae are collected in standard references
[WS09](references.md#WS09).

### Networks of queues

The classical analytical result for *networks* is **Jackson's theorem**
[JJ57](references.md#JJ57): for an open network of exponential-service nodes
with Poisson arrivals and probabilistic routing, the stationary distribution of
the queue-length vector factorises into a product of per-node distributions, and
each node behaves as if it were an independent $M/M/c$ queue. This product-form
property was extended to multiple customer classes, general service disciplines
(including processor sharing and last-come-first-served), and phase-type service
times by the BCMP theorem [BCMP75](references.md#BCMP75), and to closed networks
with a fixed number of customers by [GN67](references.md#GN67). Reversibility
and further product-form results are developed in
[Kel79](references.md#Kel79).

### Where analysis stops

Product-form results are elegant but fragile. They require exponential or
phase-type service, Poisson arrivals, and no capacity restrictions or blocking.
Many realistic systems violate these assumptions:

- general (non-exponential) service or inter-arrival distributions;
- finite buffers and hence **blocking** between nodes;
- priorities, pre-emption, and processor sharing with heterogeneous customers;
- customers who **baulk** (refuse to join), **renege** (leave before service),
  or **jockey** (switch queues);
- customers who **change class** while queueing or after service;
- server **schedules**, shift changes, and slotted services;
- **time-varying** (e.g. daily) arrival rates;
- state-dependent behaviour and feedback that can cause **deadlock**.

HCiw is built precisely to simulate these features. Where a closed form does
exist, it is often still used as a sanity check on a simulation model.

## The discrete-event simulation algorithm

### Event scheduling

HCiw follows the **event-scheduling** (or three-phase) approach
[Toc63](references.md#Toc63), [SR14](references.md#SR14). Rather than advancing
time in fixed increments, the simulation jumps from one event to the next:

1. **Initialise** the system: set the clock to $0$, create the servers, and
   schedule the first arrivals.
2. **Advance** the clock to the time of the next scheduled event.
3. **Execute** the event — an external arrival, a service completion, or a
   server shift change (a **B-event**).
4. **Execute** the consequential **C-events** that the B-event triggers, such as
   a customer starting service, being released, or being blocked.
5. Repeat steps 3-4 until no events remain at the current time, then repeat from
   step 2 until a stopping criterion is met (a maximum time or a number of
   customers).

This is described in more detail in
[Notes on HCiw's Mechanisms](mechanisms.md#hciw-mechanisms). Because several
events can be scheduled for the same instant, HCiw breaks ties by choosing
uniformly at random among the simultaneous events, so that no event type is
systematically favoured where the ordering would otherwise matter
[SR14](references.md#SR14).

### Randomness and reproducibility

Each stochastic component — an inter-arrival time, a service time, a routing
decision, a baulk or renege — is generated by drawing a random number and
transforming it into a sample from the relevant distribution (inverse
transform, phase-type expansion, rejection, and so on)
[Banks10](references.md#Banks10), [WS09](references.md#WS09). HCiw exposes a
global seed so that a run can be reproduced exactly; see
[How to Set a Seed](../Guides/Simulation/seed.md) and the
[distribution guides](../Guides/Distributions/index.md) for the sampling
methods it supports.

### Interpreting the output

A single run is one realisation of a random process, so its summary statistics
are themselves random. Valid analysis therefore uses multiple independent
replications with different seeds, discards an initial **warm-up** period while
the system leaves its artificial empty state, and, when needed, uses a
**cool-down** period to capture the experience of customers still in the system
at the end of the observation window [SR14](references.md#SR14),
[Banks10](references.md#Banks10). These techniques are demonstrated in
[Simulation Practice](simulationpractice.md) and
[Part 4 of Tutorial I](../Tutorial/GettingStarted/part_4.md#tutorial-i-p4).

## What HCiw simulates

The table maps the modelling features above to the relevant parts of the
documentation. The library implements open queueing networks with multiple
customer classes, the mechanisms of the Ciw library [PKHH19](references.md#PKHH19)
(priorities, baulking, reneging, batching, schedules, slotted services, and
processor sharing), plus HCiw's own additions such as warm starts.

| Feature | Where it is documented |
| --- | --- |
| Open queueing networks & routing | [Routing guides](../Guides/Routing/index.md) |
| Multiple, priority, and changing classes | [Customer class guides](../Guides/CustomerClasses/index.md) |
| Baulking, reneging, jockeying | [Customer behaviour guides](../Guides/CustomerBehaviour/index.md) |
| Batch arrivals | [Batch arrivals guide](../Guides/Arrivals/batching.md) |
| Queue capacities & system capacity | [Queue guides](../Guides/Queues/index.md) |
| Schedules, slotted services, pre-emption, processor sharing | [Service guides](../Guides/Services/index.md) |
| State-dependent behaviour | [Custom behaviour guides](../Guides/System/behaviour/index.md) |
| Deadlock detection | [Deadlock guide](../Guides/System/deadlock.md) |
| Warm starts from an existing backlog | [Warm-start guide](../Guides/Simulation/warm_start.md) |

## Applications in research and industry

Queueing-network simulation is a workhorse of operations research and industrial
engineering, and healthcare is a particularly active area — which is where the
**H** in HCiw comes from. The examples below are small, but each reflects a real
body of work.

### Healthcare: emergency departments and patient flow

An emergency department (ED) is a queueing network: patients arrive (often by
ambulance or walk-in), are triaged, wait for a bed or a clinician, receive
treatment, and are then discharged or admitted to a ward. Multi-class queueing
networks have been used to analyse fast-track policies and reduce the number of
patients who leave without being seen [CR09](references.md#CR09), and the
queueing-theoretic view of EDs and patient flow more broadly is surveyed in
[EW22](references.md#EW22). Simulating rather than solving such models allows
non-exponential treatment times, priority classes, and finite capacity to be
represented directly.

HCiw's **warm start** facility is especially useful here: a simulation can begin
from a pre-existing backlog of patients with realistic arrival dates, rather
than from an empty department. The backlog is supplied to the
[`Simulation`](../Reference/api.md) via `initial_individuals`; see
[How to Warm-Start a Simulation](../Guides/Simulation/warm_start.md).

### Call centres and service operations

Staffing a call centre is a classic queueing problem: how many agents are needed
to keep waiting times acceptable? Large call centres are well approximated by
$M/M/c$ systems, and asymptotic results give near-optimal staffing levels that
trade off agent cost against service quality [BMR04](references.md#BMR04).
Because demand varies predictably over the day, staffing must account for
**non-stationary** arrivals, an area developed extensively for call centres and
other service systems [GKW07](references.md#GKW07). Time-varying arrival rates,
baulking, reneging, and multiple agent/skill classes are all directly
expressible in HCiw.

### Telecommunications and computer networks

Communication systems have been modelled with queueing networks since Erlang's
early work on telephone exchanges. Modern examples include the dimensioning of
radio access networks, where [XL09](references.md#XL09) uses queueing models to
size a 3G UMTS network. The same machinery models packet buffers, link
utilisation, and server pools; loss systems (finite buffers with no waiting
room) and multi-server delay systems both map onto HCiw's finite-capacity nodes.

### Manufacturing and production lines

A production line is a network of machines (servers) connected by buffers of
finite capacity, and its throughput is often limited by **blocking**: when a
buffer is full, an upstream machine cannot pass on a finished job. This is the
same Type I blocking that HCiw implements for restricted networks
[PKHH19](references.md#PKHH19). Stochastic models of manufacturing systems
[BS93](references.md#BS93) and the "factory physics" framework
[HS11](references.md#HS11) both rely on queueing networks, with variability,
blocking, and batching as central concerns.

### A worked example

The following simulation models an $M/M/3$ queue — exponential arrivals at rate
$0.2$, exponential service at rate $0.1$ per server, three servers — and reports
the average waiting time over 1440 time units:

```python
>>> import hciw
>>> N = hciw.create_network(
...     arrival_distributions=[hciw.dists.Exponential(rate=0.2)],
...     service_distributions=[hciw.dists.Exponential(rate=0.1)],
...     number_of_servers=[3]
... )
>>> hciw.seed(1)
>>> Q = hciw.Simulation(N)
>>> Q.simulate_until_max_time(1440)
>>> recs = Q.get_all_records()
>>> waits = [r.waiting_time for r in recs]
>>> sum(waits) / len(waits)
4.2305...
```

Replacing the distributions with deterministic or phase-type alternatives, or
adding priorities or finite capacity, needs no change to the simulation
machinery — only to the model description.

## Where to go next

- Work through the [tutorials](../Tutorial/index.md) for a guided introduction.
- Use the [how-to guides](../Guides/index.md) for specific features.
- Consult the [reference](../Reference/index.md) for parameters and results.
- Read [Simulation Practice](simulationpractice.md) before drawing conclusions
  from a model.
- See how to [cite the library](../Project/citation.md).
