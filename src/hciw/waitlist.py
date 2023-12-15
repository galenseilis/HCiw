"""Initial waitlist construction module.

This module provides functionality for constructing and managing a waitlist of individuals in a simulation.
It includes functions for accepting new customers into the queue, initiating their service, and occupying
the simulation instance with individuals based on provided data.

Note:
    - The functions in this module interact with the `ciw` (Python Coded In vitro World) simulation library.

TODO:
    - Change `typing.NoReturn` to `typing.Never` when Python 3.11 is the oldest LTS.

Classes:
    None

Functions:
    - begin_service_if_possible_accept(node: ciw.Node, next_individual: ciw.Individual) -> NoReturn:
        Begins the service of the next individual at the acceptance point.

    - accept(individual_id: ciw.Individual, individual_class: Any, arrival_date: float,
             node: ciw.Node, simulation: ciw.Simulation) -> NoReturn:
        Accepts a new customer to the queue and updates relevant information at the arrival point.

    - create_existing_customers_from_list(backlog: List[list], simulation: ciw.Simulation) -> NoReturn:
        Occupies the instance of simulation with individuals based on provided data.

Examples:
    >>> backlog_data = [
    ...     [1, 'Class_A', 5.0, 0],
    ...     [2, 'Class_B', 7.0, 1],
    ...     # ... additional rows ...
    ... ]
    >>> simulation_instance = ciw.Simulation()
    >>> create_existing_customers_from_list(backlog_data, simulation_instance)
"""

import math
from typing import Any, List, NoReturn

# TODO: Change `typing.NoReturn` to `typing.Never` when Python 3.11 is oldest LTS.

import ciw


# TODO: Change `typing.NoReturn` to `typing.Never` when Python 3.11 is oldest LTS.
def begin_service_if_possible_accept(
    node: ciw.Node, next_individual: ciw.Individual
) -> NoReturn:
    """
    Begins the service of the next individual at the acceptance point.

    Args:
        node (ciw.Node): The simulation node where the service is initiated.
        next_individual (ciw.Individual): The individual to begin service for.

    Returns:
        None

    Raises:
        No specific exceptions are raised.

    Notes:
        - Sets the arrival date of the individual to the current simulation time.
        - If there is a free server or the simulation has infinite servers:
            - Attaches the server to the individual (only when servers are not infinite).
        - Determines service start time, service time, and service end time.
        - Updates the server's end date (only when servers are not infinite).
    """
    free_server = node.find_free_server(next_individual)

    if free_server is None and math.isinf(node.c) is False:
        node.decide_preempt(next_individual)

    if free_server is not None or math.isinf(node.c):
        if math.isinf(node.c) is False:
            node.attach_server(free_server, next_individual)

        next_individual.service_start_date = 0
        next_individual.service_time = node.get_service_time(next_individual)
        next_individual.service_end_date = next_individual.service_time

        if not math.isinf(node.c):
            free_server.next_end_service_date = next_individual.service_end_date


def accept(
    individual_id: ciw.Individual,
    individual_class: Any,
    arrival_date: float,
    node: ciw.Node,
    simulation: ciw.Simulation,
) -> NoReturn:
    """
    Accepts a new customer to the queue and updates relevant information at the arrival point.

    Args:
        individual_id (ciw.Individual): The unique identifier for the new individual.
        individual_class (Any): The class/type of the new individual.
        arrival_date (float): The arrival date of the new individual.
        node (ciw.Node): The simulation node where the individual is accepted.
        simulation (ciw.Simulation): The simulation instance containing the current state.

    Returns:
        None

    Raises:
        No specific exceptions are raised.

    Notes:
        - Updates the simulation's current time to the provided arrival date.
        - Creates a new individual with the given attributes.
        - Assigns the node ID to the individual and records the queue size at arrival as "Unknown".
        - Appends the new individual to the node's list of individuals for the corresponding class.
        - Increments the total number of individuals and updates the state tracker.
        - Sets the arrival date for the new individual.
        - Initiates service for the new individual using the `begin_service_if_possible_accept` function.
        - Updates statistics at the simulation level and node level.

    """
    simulation.current_time = arrival_date

    next_individual = ciw.Individual(
        id_number=individual_id,
        customer_class=individual_class,
        priority_class=simulation.network.priority_class_mapping[individual_class],
        simulation=simulation,
    )

    next_individual.node = node.id_number

    next_individual.queue_size_at_arrival = "Unknown"

    node.individuals[next_individual.priority_class].append(next_individual)

    node.number_of_individuals += 1

    node.simulation.statetracker.change_state_accept(node, next_individual)

    next_individual.arrival_date = arrival_date

    begin_service_if_possible_accept(node, next_individual)

    simulation.nodes[0].number_of_individuals += 1

    simulation.nodes[0].number_of_individuals_per_class[
        next_individual.customer_class
    ] += 1

    simulation.nodes[0].number_accepted_individuals += 1

    simulation.nodes[0].number_accepted_individuals_per_class[
        next_individual.customer_class
    ] += 1


def create_existing_customers_from_list(
    backlog: List[list], simulation: ciw.Simulation
) -> NoReturn:
    """
    Occupies the instance of simulation with individuals based on provided data.

    Args:
        backlog (List[list]): A list of data for each individual to be added.
            Each item in the list should contain the following information:
                - Customer ID
                - Customer Class
                - Customer Arrival Date
                - Customer Node (index of the simulation node)

        simulation (ciw.Simulation): An instance of ciw.Simulation representing the simulation environment.

    Returns:
        None

    Raises:
        No specific exceptions are raised.

    Notes:
        - Iterates through the provided backlog data to create and accept individuals into the simulation.
        - Each row in the backlog corresponds to an individual and contains essential information.
        - Calls the `accept` function for each individual, initializing their attributes and starting the service.

    Examples:
        >>> backlog_data = [
        ...     [1, 'Class_A', 5.0, 0],
        ...     [2, 'Class_B', 7.0, 1],
        ...     # ... additional rows ...
        ... ]
        >>> simulation_instance = ciw.Simulation()
        >>> create_existing_customers_from_list(backlog_data, simulation_instance)

    """
    customer_count = 1

    for row in backlog:
        customer_id = row[0]

        customer_class = row[1]

        customer_arrival_date = row[2]

        customer_node = row[3]

        accept(
            customer_id,
            customer_class,
            customer_arrival_date,
            simulation.nodes[customer_node],
            simulation,
        )

        customer_count += 1
