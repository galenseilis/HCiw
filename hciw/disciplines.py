"""Service disciplines for selecting the next individual from a queue."""

from hciw.auxiliary import random_choice
from hciw.individual import Individual


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
