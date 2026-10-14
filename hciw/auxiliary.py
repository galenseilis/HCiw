"""Auxiliary helper functions used throughout the simulation.

This module provides seeding utilities, weighted random sampling, and
small list helpers used by the simulation engine.
"""

import random

import numpy as np

import hciw


def seed(z):
    """Set all seeds used to generate random number streams.

    Seeds both the standard library ``random`` module and the NumPy
    random generator used by ``hciw``.

    Args:
        z (int): The seed value to use.
    """
    random.seed(z)
    hciw.rng = np.random.default_rng(seed=z)


def random_choice(array, probs=None):
    """Select a random element from an array using optional weights.

    Args:
        array (list): The values to choose from.
        probs (list, optional): Probability weights corresponding to each
            value. If omitted, a uniform choice is made.

    Returns:
        The randomly selected element of ``array``.
    """
    # If no pdf provided, assume uniform dist:
    if probs is None:
        index = int(random.random() * len(array))
        return array[index]

    # A common case, guaranteed to reach the Exit node;
    # No need to sample for this:
    if (set(probs[:-1]) == set([0.0])) and (probs[-1] == 1.0):
        return array[-1]

    # Sample a random value from using pdf
    rdm_num = random.random()
    i, p = 0, probs[0]
    while rdm_num > p:
        i += 1
        p += probs[i]
    return array[i]


def truncated_normal(mean, sd):
    """Sample from a Normal distribution truncated at zero.

    Values less than or equal to zero are resampled until a positive
    value is obtained.

    Args:
        mean (float): The mean of the Normal distribution.
        sd (float): The standard deviation of the Normal distribution.

    Returns:
        float: A positive sample from the truncated Normal distribution.
    """
    sample = random.normalvariate(mean, sd)
    while sample <= 0.0:
        sample = random.normalvariate(mean, sd)
    return sample


def flatten_list(list_of_lists):
    """Flatten a list of lists into a single list.

    Args:
        list_of_lists (list): A list whose elements are themselves lists.

    Returns:
        list: A single list containing all elements of the inner lists.
    """
    flat = []
    for a_list in list_of_lists:
        flat += a_list
    return flat


def no_routing(ind):
    """Send a customer straight to the exit node.

    This process-based routing function is a placeholder used when
    ``NoArrivals`` is used.

    Args:
        ind (Individual): The individual being routed.

    Returns:
        list: An empty list of destinations.
    """
    return []
