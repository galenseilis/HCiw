"""Service disciplines for selecting the next individual from a queue."""

from decimal import Decimal
from typing import TYPE_CHECKING, cast

from hciw.auxiliary import random_choice
from hciw.individual import Individual

if TYPE_CHECKING:
    from hciw.simulation import Simulation


def FIFO(individuals: list[Individual], t: float) -> Individual:
    """Select individuals first in, first out.

    Args:
        individuals (List[Individual]): The individuals in the queue.
        t (float): The current simulation time.

    Returns:
        Individual: The individual at the head of the queue.
    """
    return individuals[0]


def SIRO(individuals: list[Individual], t: float) -> Individual:
    """Select individuals in random order.

    Args:
        individuals (List[Individual]): The individuals in the queue.
        t (float): The current simulation time.

    Returns:
        Individual: A randomly selected individual from the queue.
    """
    return random_choice(individuals)


def LIFO(individuals: list[Individual], t: float) -> Individual:
    """Select individuals last in, first out.

    Args:
        individuals (List[Individual]): The individuals in the queue.
        t (float): The current simulation time.

    Returns:
        Individual: The individual who joined the queue most recently.
    """
    return individuals[-1]


def wait_time_over_benchmark(
    individuals: list[Individual], t: float | Decimal
) -> Individual:
    """Select the individual furthest past their customer class's benchmark.

    Each customer class may declare a target waiting time, set with
    ``create_network(customer_class_benchmarks={...})``. The individual chosen
    is the one for whom ``t - arrival_date - benchmark`` is greatest: that is,
    the individual who has waited furthest beyond their target. This is the
    discipline HCiw uses to express a service target such as "no one should
    wait more than X time units", by treating any wait beyond X as a first
    claim on the next free server.

    Args:
        individuals (list[Individual]): The individuals in the queue.
        t (float or Decimal): The current simulation time.

    Returns:
        Individual: The individual furthest past their benchmark. Ties are
            broken by queue order, so the earliest of the tied individuals is
            served next.

    Raises:
        ValueError: If any individual's customer class has no benchmark set.
    """
    simulation = cast("Simulation", individuals[0].simulation)
    customer_classes = simulation.network.customer_classes
    over_benchmarks = []
    for ind in individuals:
        benchmark = customer_classes[ind.customer_class].benchmark
        if benchmark is None:
            raise ValueError(
                f"Customer class '{ind.customer_class}' has no benchmark set; "
                "pass customer_class_benchmarks to hciw.create_network."
            )
        if isinstance(t, Decimal):
            if not isinstance(benchmark, Decimal):
                benchmark = Decimal(str(benchmark))
            over = t - Decimal(str(ind.arrival_date)) - benchmark
        else:
            over = t - ind.arrival_date - float(benchmark)
        over_benchmarks.append(over)
    return individuals[over_benchmarks.index(max(over_benchmarks))]
