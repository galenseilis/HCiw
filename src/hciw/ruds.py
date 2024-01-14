"""Randomly-unstable data structures (RUDS)."""

from typing import Any, List, NoReturn

import numpy as np
from numpy.typing import NDArray


class RandomDirichletList(list):
    """
    List that contains and resamples from a Dirichlet distribution.

    This class represents a list-like structure that contains and
    resamples from a Dirichlet distribution. It is designed for
    working with probabilistic values that sum to 1, such as probability
    distributions. The Dirichlet distribution is used to generate
    such values.

    Attributes:
        alphas (list or array-like): The alpha parameters of the
            Dirichlet distribution. These parameters control the
            shape of the distribution.

    Methods:
        __init__(self, alphas):
            Initializes the RandomDirichletList with the provided alpha
            parameters. It ensures that the alpha parameters are positive
            and populates the list with Dirichlet-distributed values. The
            probabilities are adjusted to ensure they sum to 1.

        _renormalize_probs(self):
            Private method to renormalize the probabilities. It ensures
            that the probabilities sum to 1 according to the built-in
            sum function. This is important for working with certain
            libraries that require normalized probabilities.

        sample(self):
            Sample new values from the Dirichlet distribution and ensure
            they sum to 1. This method is used to initialize or reinitialize
            the probabilities in the list.

        __getitem__(self, index):
            Resamples from the Dirichlet distribution and returns the
            value at the specified index. This method updates the list
            with newly sampled values and then returns the requested
            item.

        __min__(self):
            Returns the minimum value in the list of probabilities.
            This method provides functionality similar to the built-in
            min() function for RandomDirichletList.

        __max__(self):
            Returns the maximum value in the list of probabilities.
            This method provides functionality similar to the built-in
            max() function for RandomDirichletList.

        __len__(self):
            Returns the length of the list, which corresponds to the
            number of elements in the probability distribution.

        __repr__(self):
            Returns a string representation of the RandomDirichletList
            object, displaying its current list of probabilities.
    """

    def __init__(self, alphas: NDArray) -> NoReturn:
        if np.any(alphas) <= 0:
            raise ValueError("Alpha parameters must be positive")
        else:
            self.alphas = alphas

        self.sample()
        super().__init__(self.probs)

    def _renormalize_probs(self) -> NoReturn:
        """Sum renormalize probabilities.

        NumPy provides probabilities that are close to
        summing to one, but to work with Ciw they need
        to sum 1 according to the built-in sum function.
        """
        self.probs /= sum(self.probs)

    def sample(self) -> NoReturn:
        # Sample new values to get started
        self.probs = np.random.dirichlet(self.alphas)
        self._renormalize_probs()

        # If needed, resample until normalization passes
        while sum(self.probs) != 1.0:
            self.probs = np.random.dirichlet(self.alphas)
            self._renormalize_probs()

    def __getitem__(self, index: int) -> float:
        """Resample and then get item."""
        self.sample()
        return self.probs[index]

    def __min__(self) -> float:
        return min(self.probs)

    def __max__(self) -> float:
        return max(self.probs)

    def __len__(self) -> float:
        return len(self.probs)

    def __repr__(self) -> str:
        return f"RDL{self.probs}"

class DistList(list):
	'''List of distributions sampled by indexing.'''

    def __init__(self, distributions: List[ciw.dists.Distribution]) -> NoReturn:
		'''Initialize instance.'''
        self.distributions = distributions

    def __getitem__(self, idx: int) -> Any:
		'''Sample from an indexed distribution.'''
        return self.distributions[idx].sample()

    def __repr__(self) -> str:
		'''String representation of self.'''
        return str(self.distributions)
