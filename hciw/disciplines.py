"""Service disciplines for selecting the next individual from a queue."""

from typing import List

from hciw.individual import Individual
from hciw.auxiliary import random_choice


def FIFO(individuals: List[Individual], t: float) -> Individual:
    """Select individuals first in, first out.

    Args:
        individuals (List[Individual]): The individuals in the queue.
        t (float): The current simulation time.

    Returns:
        Individual: The individual at the head of the queue.
    """
    return individuals[0]


def SIRO(individuals: List[Individual], t: float) -> Individual:
    """Select individuals in random order.

    Args:
        individuals (List[Individual]): The individuals in the queue.
        t (float): The current simulation time.

    Returns:
        Individual: A randomly selected individual from the queue.
    """
    return random_choice(individuals)


def LIFO(individuals: List[Individual], t: float) -> Individual:
    """Select individuals last in, first out.

    Args:
        individuals (List[Individual]): The individuals in the queue.
        t (float): The current simulation time.

    Returns:
        Individual: The individual who joined the queue most recently.
    """
    return individuals[-1]
