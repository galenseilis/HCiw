"""Custom distributions to be used with Ciw."""

from typing import List, Union

import ciw
import numpy as np


class SeqPMFNaive(ciw.dists.Distribution):
    """
    Samples from a sequence of PMFs or uses a naive extrapolation assumption.

    Input times are rounded.

    The naive forecast assumption is that the probability mass function in the future of the sequence is the same as the last element of the sequence.
    The naive backcast assumption is that the probability mass function in the past of the sequence is the same as the first element of the sequence.
    These naive extrapolation assumptions are not intended to be accurate and are meant as a placeholder.

    Attributes:
        distseq (List[ciw.dists.Pmf]): A sequence of probability mass functions (PMFs).

    Methods:
        __init__(self, distseq: List[ciw.dists.Pmf]):
            Initializes the SeqPMFNaive distribution with the provided sequence of PMFs.

        sample(self, t: float, ind=None) -> Union[int, float]:
            Samples from the sequence of PMFs or uses naive extrapolation if the given time is outside the sequence.

    Examples:
        >>> pmf_sequence = [ciw.dists.Pmf(...), ciw.dists.Pmf(...), ciw.dists.Pmf(...)]
        >>> seq_pmf_naive = SeqPMFNaive(pmf_sequence)
        >>> sample_result = seq_pmf_naive.sample(t=8.5)
        >>> print(sample_result)
        3.2
    """

    def __init__(self, distseq: List[ciw.dists.Pmf]):
        """
        Initializes the SeqPMFNaive distribution.

        Args:
            distseq (List[ciw.dists.Pmf]): A sequence of probability mass functions (PMFs).
        """
        if not all(isinstance(o, ciw.dists.Pmf) for o in distseq):
            raise ValueError("Not all inputs of distseq were of type ciw.dists.Pmf")
        self.distseq = distseq

    def sample(self, t: float, ind=None) -> Union[int, float]:
        """
        Samples from the sequence of PMFs or uses naive extrapolation if the given time is outside the sequence.

        Args:
            t (float): The current simulation time.
            ind: Unused individual parameter.

        Returns:
            Union[int, float]: The sampled value from the sequence or the result of naive extrapolation.

        Raises:
            ValueError: If the provided time is not supported or if the sequence of PMFs is not valid.
        """
        time = round(t)  # TODO: Remove once probability interpolation is implemented.
        if time in self.distseq:
            return self.distseq[time].sample(time, ind)
        elif time > max(self.distseq):
            return self.distseq[max(self.distseq)].sample(time, ind)
        elif time < min(self.distseq):
            return self.distseq[min(self.distseq)].sample(time, ind)
        else:  # TODO: Linearly interpolate probabilities wrt t
            raise ValueError(f"Unsupported sampling time of {t} in SeqPMFNaive.")


class DeterministicSeqNaive(ciw.dists.Distribution):
    """
    Samples from a sequence of constant random variables or uses a naive extrapolation assumption.

    The naive forecast assumption is that the constant value in the future of the sequence is the same as the last element of the sequence.
    The naive backcast assumption is that the constant value in the past of the sequence is the same as the first element of the sequence.
    These naive extrapolation assumptions are not intended to be accurate and are meant as a placeholder.

    Attributes:
        distseq (List[ciw.dists.Deterministic]): A sequence of deterministic distributions.

    Methods:
        __init__(self, distseq: List[ciw.dists.Deterministic]):
            Initializes the DeterministicSeqNaive distribution with the provided sequence of deterministic distributions.

        sample(self, t: float, ind=None) -> Union[int, float]:
            Samples from the sequence of deterministic distributions or uses naive extrapolation if the given time is outside the sequence.

    Examples:
        >>> deterministic_sequence = [ciw.dists.Deterministic(...), ciw.dists.Deterministic(...), ciw.dists.Deterministic(...)]
        >>> det_seq_naive = DeterministicSeqNaive(deterministic_sequence)
        >>> sample_result = det_seq_naive.sample(t=8.5)
        >>> print(sample_result)
        2.0
    """

    def __init__(self, distseq: List[ciw.dists.Deterministic]):
        """
        Initializes the DeterministicSeqNaive distribution.

        Args:
            distseq (List[ciw.dists.Deterministic]): A sequence of deterministic distributions.
        """
        if not all(isinstance(o, ciw.dists.Deterministic) for o in distseq):
            raise ValueError(
                "Not all inputs of distseq were of type ciw.dists.Deterministic"
            )
        self.distseq = distseq

    def sample(self, t: float, ind=None) -> Union[int, float]:
        """
        Samples from the sequence of deterministic distributions or uses naive extrapolation if the given time is outside the sequence.

        Args:
            t (float): The current simulation time.
            ind: Unused individual parameter.

        Returns:
            Union[int, float]: The sampled value from the sequence or the result of naive extrapolation.

        Raises:
            ValueError: If the provided time is not supported or if the sequence of deterministic distributions is not valid.
        """
        time = round(t)
        if time in self.distseq:
            return self.distseq[time].sample(time, ind)
        elif time > max(self.distseq):
            return self.distseq[max(self.distseq)].sample(time, ind)
        elif time < min(self.distseq):
            return self.distseq[min(self.distseq)].sample(time, ind)
        else:
            raise ValueError(
                f"Unsupported sampling time of {t} in DeterministicSeqNaive."
            )


class SequentialZeroDefault:
    """
    Samples values from a given sequence or uses a default value of t % 1 for non-finite elements.

    Attributes:
        sequence (List[Union[int, float]]): A sequence of numerical values.
        counter (int): Internal counter to track the current position in the sequence.
        seq_len (int): The length of the sequence.

    Methods:
        __init__(self, sequence: List[Union[int, float]]):
            Initializes the SequentialZeroDefault with the provided sequence.

        sample(self, t: float, ind=None) -> Union[int, float]:
            Samples a value from the sequence or uses the default value t % 1 for non-finite elements.

    Examples:
        >>> numerical_sequence = [1.2, 3.4, np.inf, 5.6, np.nan]
        >>> seq_zero_default = SequentialZeroDefault(numerical_sequence)
        >>> sample_result = seq_zero_default.sample(t=8.5)
        >>> print(sample_result)
        0.5
    """

    def __init__(self, sequence: List[Union[int, float]]):
        """
        Initializes the SequentialZeroDefault.

        Args:
            sequence (List[Union[int, float]]): A sequence of numerical values.
        """
        assert not np.all(np.isfinite(sequence))
        self.sequence = sequence
        self.counter = 0
        self.seq_len = len(sequence)

    def sample(self, t: float, ind=None) -> Union[int, float]:
        """
        Samples a value from the sequence or uses the default value t % 1 for non-finite elements.

        Args:
            t (float): The current simulation time.
            ind: Unused individual parameter.

        Returns:
            Union[int, float]: The sampled value from the sequence or the default value t % 1 for non-finite elements.
        """
        skips = 0
        for idx in range(self.counter, self.seq_len):
            selected_value = (
                self.sequence[self.counter]
                if np.isfinite(self.sequence[self.counter])
                else t % 1
            )
            self.counter = (self.counter + 1) % self.seq_len
            return selected_value


class WeekDayServe(ciw.dists.Distribution):
    """
    Custom distribution for simulating service times based on weekdays.

    This class extends the `ciw.dists.Distribution` class to model service times with different behaviors on weekdays.
    The distribution provided in the constructor is used for sampling service times on weekdays (Monday to Friday),
    while fixed values are returned for Saturdays and Sundays.

    Attributes:
        dist (ciw.dists.Distribution): The distribution used for sampling service times on weekdays.
        offset (int): An offset to adjust the start day of the simulation week (default is Monday).

    Methods:
        __init__(self, dist, offset=0, *args, **kwargs):
            Initializes the WeekDayServe distribution with the specified distribution and offset.

        sample(self, t=None, ind=None):
            Samples service times based on weekdays using the provided distribution for weekdays
            and fixed values for Saturdays and Sundays.

    Examples:
        >>> normal_dist = ciw.dists.Normal(5, 2)
        >>> weekday_serve_dist = WeekDayServe(normal_dist, offset=0)
        >>> sample_result = weekday_serve_dist.sample(t=8.5)
        >>> print(sample_result)
        7.8
    """

    def __init__(self, dist: ciw.dists.Distribution, offset: int = 0, *args, **kwargs):
        """
        Initializes the WeekDayServe distribution.

        Args:
            dist (ciw.dists.Distribution): The distribution used for sampling service times on weekdays.
            offset (int, optional): An offset to adjust the start day of the simulation week (default is Monday).
            *args, **kwargs: Additional arguments for the base Distribution class.
        """
        super().__init__(*args, **kwargs)
        self.dist = dist
        self.offset = offset

    def sample(self, t: float = None, ind: ciw.Individual = None) -> float:
        """
        Samples service times based on weekdays using the provided distribution for weekdays
        and fixed values for Saturdays and Sundays.

        Args:
            t (float, optional): The current simulation time.
            ind (ciw.Individual, optional): The individual for which the service time is being sampled.

        Returns:
            float: The sampled service time based on the weekday behavior.
        """
        tau = (np.floor(t) - self.offset + 7) % 7
        if tau < 5:
            return self.dist.sample(t, ind)
        elif tau == 5:
            return 2.0
        else:
            return 1.0
