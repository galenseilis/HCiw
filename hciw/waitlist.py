"""Warm-start a simulation with an initial backlog of individuals.

A *warm start* seeds a simulation with individuals who are already present at
time zero, rather than waiting for them to arrive via the arrival process. This
is useful when simulating a system that is already busy, for example a hospital
whose current patients are known from historical data.

Each backlog entry supplies the individual's identifier, customer class,
historical arrival date, and the node they are waiting at. Arrival dates are
expected to be at or before the simulation start time, so that the time an
individual spent waiting before the simulation began is captured in their
waiting-time statistics.
"""

from __future__ import annotations

import hciw


def accept(
    individual_id: int,
    individual_class: str,
    arrival_date: float,
    node: hciw.Node,
    simulation: hciw.Simulation,
) -> None:
    """Place an individual already present at time zero into a node.

    The individual is accepted by the node using the usual acceptance logic,
    so that service begins immediately if a server is free. Their recorded
    ``arrival_date`` is then overwritten with the supplied historical date so
    that waiting-time statistics include the time spent in the system before
    the simulation started.

    Args:
        individual_id: A unique identifier for the individual.
        individual_class: The customer class the individual belongs to.
        arrival_date: The historical date at which the individual arrived.
            This should be at or before the simulation start time.
        node: The node the individual is waiting at.
        simulation: The simulation the individual belongs to.
    """
    simulation.current_time = 0
    priority_class = simulation.network.priority_class_mapping[individual_class]
    next_individual = simulation.IndividualType(
        individual_id,
        individual_class,
        priority_class,
        simulation=simulation,
    )
    next_individual.starting_node = node.id_number
    simulation.routers[individual_class].initialise_individual(next_individual)
    node.accept(next_individual)
    next_individual.arrival_date = arrival_date
    node.update_next_event_date()
    _update_arrival_node(simulation, individual_id, individual_class)


def _update_arrival_node(
    simulation: hciw.Simulation, individual_id: int, individual_class: str
) -> None:
    """Advance the arrival node's counters to account for a seeded individual.

    The arrival node's ``number_of_individuals`` is also the source of new
    individual identifiers, so it is advanced past the seeded identifier to
    prevent later arrivals from reusing it.

    Args:
        simulation: The simulation being seeded.
        individual_id: The identifier of the seeded individual.
        individual_class: The customer class of the seeded individual.
    """
    arrival_node = simulation.nodes[0]
    arrival_node.number_of_individuals = max(
        arrival_node.number_of_individuals + 1, individual_id
    )
    arrival_node.number_of_individuals_per_class[individual_class] += 1
    arrival_node.number_accepted_individuals += 1
    arrival_node.number_accepted_individuals_per_class[individual_class] += 1


def create_existing_customers_from_list(
    backlog: list[list],
    simulation: hciw.Simulation,
) -> None:
    """Seed a simulation with an initial backlog of individuals.

    Each row of the backlog describes one individual already present at time
    zero. Rows are supplied in the order the individuals should be placed into
    their queues.

    Args:
        backlog: A list of rows, each of the form
            ``[individual_id, customer_class, arrival_date, node_index]``,
            where ``node_index`` is the index of the node in
            ``simulation.nodes``.
        simulation: The simulation to seed.
    """
    for individual_id, customer_class, arrival_date, node_index in backlog:
        accept(
            individual_id,
            customer_class,
            arrival_date,
            simulation.nodes[node_index],
            simulation,
        )
    if backlog:
        _record_initial_state(simulation)


def _record_initial_state(simulation: hciw.Simulation) -> None:
    """Record the state tracker's initial state after seeding.

    The state tracker records its state when ``Simulation`` initialises it,
    before any individual has been seeded. Seeding changes that state at time
    zero, so the tracker's first history entry is refreshed to match, ensuring
    state probabilities cover the whole simulation correctly.

    Args:
        simulation: The simulation that was seeded.
    """
    history = simulation.statetracker.history
    history[0] = [history[0][0], simulation.statetracker.hash_state()]
