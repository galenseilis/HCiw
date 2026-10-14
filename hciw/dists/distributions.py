"""Distributions available in HCiw."""

import copy
import math
import random
import statistics as st
from itertools import cycle
from math import erf, exp, pi, sqrt
from operator import add, mul, sub, truediv
from random import (
    expovariate,
    gammavariate,
    lognormvariate,
    triangular,
    uniform,
    weibullvariate,
)

import numpy as np

from hciw.auxiliary import *
from hciw.individual import Individual


class Distribution:
    """A general distribution from which all other distributions inherit."""

    def __repr__(self) -> str:
        """Return a string representation of the distribution."""
        return "Distribution"

    def sample(self, t: float | None = None, ind: Individual | None = None) -> float:
        """Sample a value from the distribution.

        Args:
            t (float, optional): The current time. Defaults to None.
            ind (Individual, optional): The individual being sampled. Defaults to None.

        Returns:
            float: A sampled value. The base class implements no sampling.
        """
        ...

    def _sample(self, t=None, ind=None):
        """
        Performs vaildity checks before sampling.
        """
        s = self.sample(t=t, ind=ind)
        if (isinstance(s, (float, int))) and s >= 0:
            return s
        else:
            raise ValueError("Invalid time sampled.")

    def __add__(self, dist):
        """Add two distributions such that sampling is the sum of the samples.

        Args:
            dist (Distribution): The distribution to add.

        Returns:
            CombinedDistribution: A distribution sampling the sum.
        """
        return CombinedDistribution(self, dist, add)

    def __sub__(self, dist):
        """Subtract two distributions such that sampling is the difference.

        Args:
            dist (Distribution): The distribution to subtract.

        Returns:
            CombinedDistribution: A distribution sampling the difference.
        """
        return CombinedDistribution(self, dist, sub)

    def __mul__(self, dist):
        """Multiply two distributions such that sampling is the product.

        Args:
            dist (Distribution): The distribution to multiply by.

        Returns:
            CombinedDistribution: A distribution sampling the product.
        """
        return CombinedDistribution(self, dist, mul)

    def __truediv__(self, dist):
        """Divide two distributions such that sampling is the ratio.

        Args:
            dist (Distribution): The distribution to divide by.

        Returns:
            CombinedDistribution: A distribution sampling the ratio.
        """
        return CombinedDistribution(self, dist, truediv)

    @property
    def mean(self):
        """Return the default mean of a distribution.

        Returns:
            float: The mean, NaN by default.
        """
        return float("nan")

    @property
    def variance(self):
        """Return the default variance of a distribution.

        Returns:
            float: The variance, NaN by default.
        """
        return float("nan")

    @property
    def sd(self):
        """Return the default standard deviation of a distribution.

        Returns:
            float: The square root of the variance.
        """
        return math.sqrt(self.variance)

    @property
    def median(self):
        """Return the default median of a distribution.

        Returns:
            float: The median, NaN by default.
        """
        return float("nan")

    @property
    def upper_limit(self):
        """Return the default upper limit of a distribution.

        Returns:
            float: The upper limit, NaN by default.
        """
        return float("nan")

    @property
    def lower_limit(self):
        """Return the default lower limit of a distribution.

        Returns:
            float: The lower limit, NaN by default.
        """
        return float("nan")


class CombinedDistribution(Distribution):
    """A distribution combining the samples of two other distributions.

    The samples of ``dist1`` and ``dist2`` are combined using ``operator``.

    Attributes:
        d1 (Distribution): A deep copy of the first distribution.
        d2 (Distribution): A deep copy of the second distribution.
        operator (callable): The binary operator used to combine samples.
    """

    def __init__(self, dist1, dist2, operator):
        """Initialize the combined distribution.

        Args:
            dist1 (Distribution): The first distribution.
            dist2 (Distribution): The second distribution.
            operator (callable): The binary operator used to combine samples.
        """
        self.d1 = copy.deepcopy(dist1)
        self.d2 = copy.deepcopy(dist2)
        self.operator = operator

    def __repr__(self):
        """Return a string representation of the combined distribution."""
        return "CombinedDistribution"

    def sample(self, t=None, ind=None):
        """Sample from each distribution and combine the samples.

        Args:
            t (float, optional): The current time. Defaults to None.
            ind (Individual, optional): The individual being sampled. Defaults to None.

        Returns:
            float: The combined sample.
        """
        s1 = self.d1.sample(t, ind)
        s2 = self.d2.sample(t, ind)
        return self.operator(s1, s2)

    @property
    def mean(self) -> float:
        """Return the combined mean of the two distributions.

        Returns:
            float: The mean implied by the operator.
        """
        m1 = self.d1.mean
        m2 = self.d2.mean
        if self.operator == add:
            return m1 + m2
        elif self.operator == sub:
            return m1 - m2
        elif self.operator == mul:
            return m1 * m2
        elif self.operator == truediv:
            if m2 == 0:
                return float("nan")
            return m1 / m2  # delta-method mean
        return float("nan")

    @property
    def variance(self) -> float:
        """Return the combined variance of the two distributions.

        Returns:
            float: The variance implied by the operator.
        """
        m1 = self.d1.mean
        m2 = self.d2.mean
        v1 = self.d1.variance
        v2 = self.d2.variance

        if self.operator in (add, sub):
            # Var(A + B) = Var(A) + Var(B), assuming independence
            # Var(A - B) = Var(A) + Var(B), assuming independence
            return v1 + v2
        elif self.operator == mul:
            # Var(A * B) = v1*v2 + m2^2*v1 + m1^2*v2, assuming independence
            return v1 * v2 + (m2**2) * v1 + (m1**2) * v2
        elif self.operator == truediv:
            # delta-method approximation for Var(A/B)
            if m2 == 0:
                return float("nan")
            return (v1 / (m2**2)) + ((m1**2) * v2) / (m2**4)
        return float("nan")

    @property
    def upper_limit(self):
        """Return the combined upper limit.

        Returns:
            float: The sum of the upper limits for addition, NaN otherwise.
        """
        if self.operator == add:
            return self.d1.upper_limit + self.d2.upper_limit
        return float("nan")

    @property
    def lower_limit(self):
        """Return the combined lower limit.

        Returns:
            float: The sum of the lower limits for addition, NaN otherwise.
        """
        if self.operator == add:
            return self.d1.lower_limit + self.d2.lower_limit
        return float("nan")


class Uniform(Distribution):
    """The Uniform distribution.

    Attributes:
        lower (float): The lower bound.
        upper (float): The upper bound.
    """

    def __init__(self, lower, upper):
        """Initialize the Uniform distribution.

        Args:
            lower (float): The lower bound.
            upper (float): The upper bound.

        Raises:
            ValueError: If a bound is negative or ``upper`` is less than ``lower``.
        """
        if lower < 0.0 or upper < 0.0:
            raise ValueError("Uniform distribution must sample positive numbers only.")
        if upper < lower:
            raise ValueError(
                "Uniform distirbution upper bound should be >= lower bound."
            )
        self.lower = lower
        self.upper = upper

    def __repr__(self):
        """Return a string representation of the Uniform distribution."""
        return f"Uniform(lower={self.lower}, upper={self.upper})"

    def sample(self, t=None, ind=None):
        """Sample from the Uniform distribution.

        Args:
            t (float, optional): The current time. Defaults to None.
            ind (Individual, optional): The individual being sampled. Defaults to None.

        Returns:
            float: A sample between ``lower`` and ``upper``.
        """
        return uniform(self.lower, self.upper)

    @property
    def mean(self):
        """Return the mean of the Uniform distribution.

        Returns:
            float: The mean.
        """
        return (self.lower + self.upper) / 2

    @property
    def variance(self):
        """Return the variance of the Uniform distribution.

        Returns:
            float: The variance.
        """
        return ((self.upper - self.lower) ** 2) / 12

    @property
    def median(self):
        """Return the median of the Uniform distribution.

        Returns:
            float: The median.
        """
        return (self.lower + self.upper) / 2

    @property
    def upper_limit(self):
        """Return the upper limit of the Uniform distribution.

        Returns:
            float: The upper bound.
        """
        return self.upper

    @property
    def lower_limit(self):
        """Return the lower limit of the Uniform distribution.

        Returns:
            float: The lower bound.
        """
        return self.lower


class Deterministic(Distribution):
    """The Deterministic distribution.

    Attributes:
        value (float): The value always returned by the distribution.
    """

    def __init__(self, value):
        """Initialize the Deterministic distribution.

        Args:
            value (float): The value to return.

        Raises:
            ValueError: If ``value`` is negative.
        """
        if value < 0.0:
            raise ValueError(
                "Deterministic distribution must sample positive numbers only."
            )
        self.value = value

    def __repr__(self):
        """Return a string representation of the Deterministic distribution."""
        return f"Deterministic(value={self.value})"

    def sample(self, t=None, ind=None):
        """Sample from the Deterministic distribution.

        Args:
            t (float, optional): The current time. Defaults to None.
            ind (Individual, optional): The individual being sampled. Defaults to None.

        Returns:
            float: The deterministic value.
        """
        return self.value

    @property
    def mean(self):
        """Return the mean of the Deterministic distribution.

        Returns:
            float: The deterministic value.
        """
        return self.value

    @property
    def variance(self):
        """Return the variance of the Deterministic distribution.

        Returns:
            float: Always 0.0.
        """
        return 0.0

    @property
    def median(self):
        """Return the median of the Deterministic distribution.

        Returns:
            float: The deterministic value.
        """
        return self.value

    @property
    def upper_limit(self):
        """Return the upper limit of the Deterministic distribution.

        Returns:
            float: The deterministic value.
        """
        return self.value

    @property
    def lower_limit(self):
        """Return the lower limit of the Deterministic distribution.

        Returns:
            float: The deterministic value.
        """
        return self.value


class Triangular(Distribution):
    """The Triangular distribution.

    Attributes:
        lower (float): The lower bound.
        mode (float): The modal value.
        upper (float): The upper bound.
    """

    def __init__(self, lower, mode, upper):
        """Initialize the Triangular distribution.

        Args:
            lower (float): The lower bound.
            mode (float): The modal value.
            upper (float): The upper bound.

        Raises:
            ValueError: If any parameter is negative.
            ValueError: If the bounds do not satisfy ``lower <= mode <= upper``.
        """
        if lower < 0.0 or upper < 0.0 or mode < 0.0:
            raise ValueError(
                "Triangular distribution must sample positive numbers only."
            )
        if not lower <= mode <= upper:
            raise ValueError(
                "Triangular distribution lower bound must be <= mode must be "
                "<= upper bound."
            )
        self.lower = lower
        self.mode = mode
        self.upper = upper

    def __repr__(self):
        """Return a string representation of the Triangular distribution."""
        return f"Triangular(lower={self.lower}, mode={self.mode}, upper={self.upper})"

    def sample(self, t=None, ind=None):
        """Sample from the Triangular distribution.

        Args:
            t (float, optional): The current time. Defaults to None.
            ind (Individual, optional): The individual being sampled. Defaults to None.

        Returns:
            float: A sample between ``lower`` and ``upper``.
        """
        return triangular(self.lower, self.upper, self.mode)

    @property
    def mean(self):
        """Return the mean of the Triangular distribution.

        Returns:
            float: The mean.
        """
        return (self.lower + self.mode + self.upper) / 3

    @property
    def variance(self):
        """Return the variance of the Triangular distribution.

        Returns:
            float: The variance.
        """
        a, b, c = self.lower, self.upper, self.mode
        return (a**2 + b**2 + c**2 - a * b - a * c - b * c) / 18

    @property
    def median(self):
        # True median of a Triangular(a, c, b)
        """Return the median of the Triangular distribution.

        Returns:
            float: The median.
        """
        a, c, b = self.lower, self.mode, self.upper
        mid = (a + b) / 2
        if c >= mid:
            return a + (((b - a) * (c - a) / 2) ** 0.5)
        return b - (((b - a) * (b - c) / 2) ** 0.5)

    @property
    def upper_limit(self):
        """Return the upper limit of the Triangular distribution.

        Returns:
            float: The upper bound.
        """
        return self.upper

    @property
    def lower_limit(self):
        """Return the lower limit of the Triangular distribution.

        Returns:
            float: The lower bound.
        """
        return self.lower


class Exponential(Distribution):
    """The Exponential distribution.

    Attributes:
        rate (float): The rate parameter, lambda.
    """

    def __init__(self, rate):
        """Initialize the Exponential distribution.

        Args:
            rate (float): The rate parameter, lambda.

        Raises:
            ValueError: If ``rate`` is not positive.
        """
        if rate <= 0.0:
            raise ValueError(
                "Exponential distribution must sample positive numbers only."
            )
        self.rate = rate

    def __repr__(self):
        """Return a string representation of the Exponential distribution."""
        return f"Exponential(rate={self.rate})"

    def sample(self, t=None, ind=None):
        """Sample from the Exponential distribution.

        Args:
            t (float, optional): The current time. Defaults to None.
            ind (Individual, optional): The individual being sampled. Defaults to None.

        Returns:
            float: A sample from the distribution.
        """
        return expovariate(self.rate)

    @property
    def mean(self):
        """Return the mean of the Exponential distribution.

        Returns:
            float: The mean.
        """
        return 1 / self.rate

    @property
    def variance(self):
        """Return the variance of the Exponential distribution.

        Returns:
            float: The variance.
        """
        return 1 / (self.rate**2)

    @property
    def median(self):
        """Return the median of the Exponential distribution.

        Returns:
            float: The median.
        """
        return math.log(2) / self.rate

    @property
    def upper_limit(self):
        """Return the upper limit of the Exponential distribution.

        Returns:
            float: Infinity.
        """
        return float("inf")

    @property
    def lower_limit(self):
        """Return the lower limit of the Exponential distribution.

        Returns:
            float: Zero.
        """
        return 0


class Gamma(Distribution):
    """The Gamma distribution.

    Attributes:
        shape (float): The shape parameter, alpha.
        scale (float): The scale parameter, beta.
    """

    def __init__(self, shape, scale):
        """Initialize the Gamma distribution.

        Args:
            shape (float): The shape parameter, alpha.
            scale (float): The scale parameter, beta.
        """
        self.shape = shape
        self.scale = scale

    def __repr__(self):
        """Return a string representation of the Gamma distribution."""
        return f"Gamma(shape={self.shape}, scale={self.scale})"

    def sample(self, t=None, ind=None):
        """Sample from the Gamma distribution.

        Args:
            t (float, optional): The current time. Defaults to None.
            ind (Individual, optional): The individual being sampled. Defaults to None.

        Returns:
            float: A sample from the distribution.
        """
        return gammavariate(self.shape, self.scale)

    @property
    def mean(self):
        """Return the mean of the Gamma distribution.

        Returns:
            float: The mean.
        """
        return self.shape * self.scale

    @property
    def variance(self):
        """Return the variance of the Gamma distribution.

        Returns:
            float: The variance.
        """
        return self.shape * (self.scale**2)

    @property
    def upper_limit(self):
        """Return the upper limit of the Gamma distribution.

        Returns:
            float: Infinity.
        """
        return float("inf")

    @property
    def lower_limit(self):
        """Return the lower limit of the Gamma distribution.

        Returns:
            float: Zero.
        """
        return 0


class Normal(Distribution):
    """Truncated Normal distribution, truncated below at 0."""

    def __init__(self, mean, sd):
        """Initialize the truncated Normal distribution.

        Args:
            mean (float): Mean of the underlying normal distribution.
            sd (float): Standard deviation of the underlying normal distribution.
        """
        self._mean = mean
        self._sd = sd

    def __repr__(self):
        """Return a string representation of the Normal distribution."""
        return f"Normal(mean={self._mean}, sd={self._sd})"

    def sample(self, t=None, ind=None):
        """Sample from the truncated Normal distribution.

        Args:
            t (float, optional): The current time. Defaults to None.
            ind (Individual, optional): The individual being sampled. Defaults to None.

        Returns:
            float: A sample truncated below at 0.
        """
        return truncated_normal(self._mean, self._sd)

    @property
    def mean(self):
        """Return the mean of the truncated Normal distribution.

        Returns:
            float: The mean of the truncated distribution.
        """
        z = self._mean / self._sd
        phi = (1 / sqrt(2 * pi)) * exp(-0.5 * z**2)
        Phi = 0.5 * (1 + erf(z / sqrt(2)))
        return self._mean + self._sd * (phi / Phi)

    @property
    def variance(self):
        """Return the variance of the truncated Normal distribution.

        Returns:
            float: The variance of the truncated distribution.
        """
        z = self._mean / self._sd
        phi = (1 / sqrt(2 * pi)) * exp(-0.5 * z**2)
        Phi = 0.5 * (1 + erf(z / sqrt(2)))
        term = phi / Phi
        return (self._sd**2) * (1 - z * term - (term**2))

    @property
    def median(self):
        # Truncated below at 0
        """Return the median of the truncated Normal distribution.

        Returns:
            float: The median of the truncated distribution.
        """
        z = self._mean / self._sd
        Norm = st.NormalDist(0, 1)
        target = 1.0 - 0.5 * Norm.cdf(z)
        return self._mean + self._sd * Norm.inv_cdf(target)

    @property
    def upper_limit(self):
        """Return the upper limit of the truncated Normal distribution.

        Returns:
            float: Infinity.
        """
        return float("inf")

    @property
    def lower_limit(self):
        """Return the lower limit of the truncated Normal distribution.

        Returns:
            float: Zero.
        """
        return 0


class Lognormal(Distribution):
    """The Lognormal distribution."""

    def __init__(self, mean, sd):
        """Initialize the Lognormal distribution.

        Args:
            mean (float): The mean of the underlying normal, mu.
            sd (float): The standard deviation of the underlying normal, sigma.
        """
        self._mean = mean
        self._sd = sd

    def __repr__(self):
        """Return a string representation of the Lognormal distribution."""
        return f"Lognormal(mean={self._mean}, sd={self._sd})"

    def sample(self, t=None, ind=None):
        """Sample from the Lognormal distribution.

        Args:
            t (float, optional): The current time. Defaults to None.
            ind (Individual, optional): The individual being sampled. Defaults to None.

        Returns:
            float: A sample from the distribution.
        """
        return lognormvariate(self._mean, self._sd)

    @property
    def mean(self):
        """Return the mean of the Lognormal distribution.

        Returns:
            float: The mean.
        """
        return math.exp(self._mean + (self._sd**2) / 2)

    @property
    def variance(self):
        """Return the variance of the Lognormal distribution.

        Returns:
            float: The variance.
        """
        return (math.exp(self._sd**2) - 1) * math.exp(2 * self._mean + self._sd**2)

    @property
    def median(self):
        """Return the median of the Lognormal distribution.

        Returns:
            float: The median.
        """
        return math.exp(self._mean)

    @property
    def upper_limit(self):
        """Return the upper limit of the Lognormal distribution.

        Returns:
            float: Infinity.
        """
        return float("inf")

    @property
    def lower_limit(self):
        """Return the lower limit of the Lognormal distribution.

        Returns:
            float: Zero.
        """
        return 0


class Weibull(Distribution):
    """The Weibull distribution.

    Attributes:
        scale (float): The scale parameter, alpha.
        shape (float): The shape parameter, beta.
    """

    def __init__(self, scale, shape):
        """Initialize the Weibull distribution.

        Args:
            scale (float): The scale parameter, alpha.
            shape (float): The shape parameter, beta.
        """
        self.scale = scale
        self.shape = shape

    def __repr__(self):
        """Return a string representation of the Weibull distribution."""
        return f"Weibull(shape={self.shape}, scale={self.scale})"

    def sample(self, t=None, ind=None):
        """Sample from the Weibull distribution.

        Args:
            t (float, optional): The current time. Defaults to None.
            ind (Individual, optional): The individual being sampled. Defaults to None.

        Returns:
            float: A sample from the distribution.
        """
        return weibullvariate(self.scale, self.shape)

    @property
    def mean(self):
        """Return the mean of the Weibull distribution.

        Returns:
            float: The mean.
        """
        return self.scale * math.gamma(1 + 1 / self.shape)

    @property
    def variance(self):
        """Return the variance of the Weibull distribution.

        Returns:
            float: The variance.
        """
        g1 = math.gamma(1 + 1 / self.shape)
        g2 = math.gamma(1 + 2 / self.shape)
        return (self.scale**2) * (g2 - (g1**2))

    @property
    def median(self):
        """Return the median of the Weibull distribution.

        Returns:
            float: The median.
        """
        return self.scale * (math.log(2) ** (1 / self.shape))

    @property
    def upper_limit(self):
        """Return the upper limit of the Weibull distribution.

        Returns:
            float: Infinity.
        """
        return float("inf")

    @property
    def lower_limit(self):
        """Return the lower limit of the Weibull distribution.

        Returns:
            float: Zero.
        """
        return 0


class Empirical(Distribution):
    """The Empirical distribution.

    Attributes:
        observations (list): The observations from which to sample.
    """

    def __init__(self, observations):
        """Initialize the Empirical distribution.

        Args:
            observations (list): The observations from which to sample.

        Raises:
            ValueError: If any observation is negative.
        """
        if any(o < 0 for o in observations):
            raise ValueError(
                "Empirical distribution must sample positive numbers only."
            )
        self.observations = observations

    def __repr__(self):
        """Return a string representation of the Empirical distribution."""
        return "Empirical"

    def sample(self, t=None, ind=None):
        """Sample from the Empirical distribution.

        Args:
            t (float, optional): The current time. Defaults to None.
            ind (Individual, optional): The individual being sampled. Defaults to None.

        Returns:
            float: A value chosen uniformly from ``observations``.
        """
        return random_choice(self.observations)

    @property
    def mean(self):
        """Return the mean of the Empirical distribution.

        Returns:
            float: The mean of the observations.
        """
        return sum(self.observations) / len(self.observations)

    @property
    def variance(self):
        """Return the variance of the Empirical distribution.

        Returns:
            float: The population variance of the observations.
        """
        m = self.mean
        return sum((x - m) ** 2 for x in self.observations) / len(self.observations)

    @property
    def median(self):
        # standard sample-median:
        #  - odd n: middle element
        #  - even n: average of the two middle elements
        """Return the median of the Empirical distribution.

        Returns:
            float: The sample median of the observations.
        """
        xs = sorted(self.observations)
        n = len(xs)
        mid = n // 2
        if n % 2 == 1:
            return xs[mid]
        else:
            return (xs[mid - 1] + xs[mid]) / 2

    @property
    def upper_limit(self):
        """Return the upper limit of the Empirical distribution.

        Returns:
            float: The largest observation.
        """
        return max(self.observations)

    @property
    def lower_limit(self):
        """Return the lower limit of the Empirical distribution.

        Returns:
            float: The smallest observation.
        """
        return min(self.observations)


class Sequential(Distribution):
    """The Sequential distribution.

    Attributes:
        sequence (list): The sequence of values to cycle through.
        generator (itertools.cycle): The cycle iterator over ``sequence``.
    """

    def __init__(self, sequence):
        """Initialize the Sequential distribution.

        Args:
            sequence (list): The sequence of values to cycle through.

        Raises:
            ValueError: If any value in ``sequence`` is negative.
        """
        if any(o < 0 for o in sequence):
            raise ValueError(
                "Sequential distribution must sample positive numbers only."
            )
        self.sequence = sequence
        self.generator = cycle(self.sequence)

    def __repr__(self):
        """Return a string representation of the Sequential distribution."""
        if len(self.sequence) <= 3:
            return f"Sequential({self.sequence})"
        else:
            return f"Sequential([{self.sequence[0]}, ..., {self.sequence[-1]}])"

    def sample(self, t=None, ind=None):
        """Sample the next value from the sequence.

        Args:
            t (float, optional): The current time. Defaults to None.
            ind (Individual, optional): The individual being sampled. Defaults to None.

        Returns:
            float: The next value in the sequence.
        """
        return next(self.generator)

    @property
    def mean(self):
        """Return the mean of the Sequential distribution.

        Returns:
            float: The mean of the sequence.
        """
        return sum(self.sequence) / len(self.sequence)

    @property
    def variance(self):
        """Return the variance of the Sequential distribution.

        Returns:
            float: The population variance of the sequence.
        """
        m = self.mean
        return sum((x - m) ** 2 for x in self.sequence) / len(self.sequence)

    @property
    def median(self):
        # sample median of the fixed sequence
        #  - odd n: middle element
        #  - even n: average of the two middle elements
        """Return the median of the Sequential distribution.

        Returns:
            float: The sample median of the sequence.
        """
        xs = sorted(self.sequence)
        n = len(xs)
        mid = n // 2
        if n % 2 == 1:
            return xs[mid]
        else:
            return (xs[mid - 1] + xs[mid]) / 2

    @property
    def upper_limit(self):
        """Return the upper limit of the Sequential distribution.

        Returns:
            float: The largest value in the sequence.
        """
        return max(self.sequence)

    @property
    def lower_limit(self):
        """Return the lower limit of the Sequential distribution.

        Returns:
            float: The smallest value in the sequence.
        """
        return min(self.sequence)


class Pmf(Distribution):
    """A distribution defined by a probability mass function (pmf).

    Attributes:
        values (list): The values that can be sampled.
        probs (list): The probability associated with each value.
    """

    def __init__(self, values, probs):
        """Initialize the Pmf distribution.

        Args:
            values (list): The values to sample.
            probs (list): The associated probabilities, which must sum to 1.

        Raises:
            ValueError: If any value is negative.
            ValueError: If any probability is outside [0, 1].
            ValueError: If the probabilities do not sum to 1.0.
        """
        if any(o < 0 for o in values):
            raise ValueError("Pmf must sample positive numbers only.")
        if any(p < 0 or p > 1.0 for p in probs):
            raise ValueError("Pmf must have valid probabilities.")
        if not np.isclose(sum(probs), 1.0):
            raise ValueError("Pmf probabilities must sum to 1.0.")
        self.values = values
        self.probs = probs

    def __repr__(self):
        """Return a string representation of the Pmf distribution."""
        return f"Pmf(values={self.values}, probs={self.probs})"

    def sample(self, t=None, ind=None):
        """Sample from the Pmf distribution.

        Args:
            t (float, optional): The current time. Defaults to None.
            ind (Individual, optional): The individual being sampled. Defaults to None.

        Returns:
            float: A value chosen according to ``probs``.
        """
        return random_choice(self.values, self.probs)

    @property
    def mean(self):
        """Return the mean of the Pmf distribution.

        Returns:
            float: The mean.
        """
        return sum(v * p for v, p in zip(self.values, self.probs, strict=False))

    @property
    def variance(self):
        """Return the variance of the Pmf distribution.

        Returns:
            float: The variance.
        """
        m = self.mean
        return sum(
            p * (v - m) ** 2 for v, p in zip(self.values, self.probs, strict=False)
        )

    @property
    def median(self):
        """Return the median of the Pmf distribution.

        Returns:
            float: The value at which the cumulative probability reaches 0.5.
        """
        pairs = sorted(zip(self.values, self.probs, strict=False), key=lambda t: t[0])
        cum = 0.0
        for v, p in pairs:
            cum += p
            if cum >= 0.5:
                return v
        return pairs[-1][0]

    @property
    def upper_limit(self):
        """Return the upper limit of the Pmf distribution.

        Returns:
            float: The largest value.
        """
        return max(self.values)

    @property
    def lower_limit(self):
        """Return the lower limit of the Pmf distribution.

        Returns:
            float: The smallest value.
        """
        return min(self.values)


class PhaseType(Distribution):
    """A distribution defined by an initial vector and an absorbing Markov chain.

    The final state of the chain is the absorbing state.

    Attributes:
        initial_state (list): The initial probability of being in each state.
        states (tuple): The indices of the states.
        absorbing_matrix (list): The rates of the absorbing Markov chain.
    """

    def __init__(self, initial_state, absorbing_matrix):
        """Initialize the PhaseType distribution.

        Args:
            initial_state (list): The initial probabilities of being in each state.
            absorbing_matrix (list): The matrix representation of the absorbing
                Markov chain, with the final state the absorbing state.

        Raises:
            ValueError: If the initial state contains negative probabilities.
            ValueError: If the initial state contains probabilities above 1.0.
            ValueError: If the initial state probabilities do not sum to 1.0.
            ValueError: If the absorbing matrix is not square.
            ValueError: If the initial state and matrix sizes differ.
            ValueError: If any transition rate is negative.
            ValueError: If the matrix rows do not sum to 0.
            ValueError: If the final state is not the absorbing state.
            ValueError: If the absorbing state cannot be reached.
        """
        if any(p < 0 for p in initial_state):
            raise ValueError("Initial state vector must have positive probabilities.")
        if any(p > 1.0 for p in initial_state):
            raise ValueError(
                "Initial state vector probabilities must be no more than 1.0."
            )
        if sum(initial_state) > 1.0 + 10 ** (-10) or sum(initial_state) < 1.0 - 10 ** (
            -10
        ):
            raise ValueError("Initial state vector probabilities must sum to 1.0.")
        if any(len(absorbing_matrix) != len(row) for row in absorbing_matrix):
            raise ValueError("Matrix of the absorbing Markov chain must be square.")
        if len(initial_state) != len(absorbing_matrix):
            raise ValueError(
                "Initial state vector must have same number of states as absorbing "
                "Markov chain matrix."
            )
        if any(
            row[j] < 0
            for i, row in enumerate(absorbing_matrix)
            for j in range(len(absorbing_matrix))
            if i != j
        ):
            raise ValueError("Transition rates must be positive.")
        if not all(
            -(10 ** (-10)) < sum(row) < 10 ** (-10)
            for i, row in enumerate(absorbing_matrix)
        ):
            raise ValueError("Matrix rows must sum to 0.")
        if not all(r == 0 for r in absorbing_matrix[-1]):
            raise ValueError("Final state must be the absorbing state.")
        if not any(row[-1] > 0 for row in absorbing_matrix):
            raise ValueError("Must be possible to reach the absorbing state.")
        self.initial_state = initial_state
        self.states = tuple(range(len(initial_state)))
        self.absorbing_matrix = absorbing_matrix

    def __repr__(self) -> str:
        """Return a string representation of the PhaseType distribution."""
        return "PhaseType"

    def sample_transition(self, rate):
        """Sample the time to a single transition.

        Args:
            rate (float): The rate of the transition.

        Returns:
            float: The sampled transition time, or infinity if ``rate`` is not positive.
        """
        if rate <= 0.0:
            return float("Inf")
        return expovariate(rate)

    def sample(self, t=None, ind=None):
        """Sample from the PhaseType distribution.

        Args:
            t (float, optional): The current time. Defaults to None.
            ind (Individual, optional): The individual being sampled. Defaults to None.

        Returns:
            float: The total time until absorption.
        """
        cumulative_time = 0
        current_state = random_choice(self.states, probs=self.initial_state)
        while current_state != self.states[-1]:
            potential_transitions = [
                self.sample_transition(r) for r in self.absorbing_matrix[current_state]
            ]
            time, idx = min(
                (time, idx) for (idx, time) in enumerate(potential_transitions)
            )
            cumulative_time += time
            current_state = idx
        return cumulative_time

    @property
    def mean(self):
        """Return the mean of the PhaseType distribution.

        Returns:
            float: The expected time to absorption.
        """
        Q = np.array(self.absorbing_matrix)[:-1, :-1]
        alpha = np.array(self.initial_state[:-1])
        ones = np.ones(len(Q))
        return float(alpha @ np.linalg.inv(-Q) @ ones)

    @property
    def variance(self):
        """Return the variance of the PhaseType distribution.

        Returns:
            float: The variance of the time to absorption.
        """
        Q = np.array(self.absorbing_matrix)[:-1, :-1]
        alpha = np.array(self.initial_state)[:-1]
        ones = np.ones(len(Q))
        invQ = np.linalg.inv(-Q)

        # E[T] and E[T^2]
        mean = float(alpha @ invQ @ ones)
        second_moment = float(2 * alpha @ invQ @ invQ @ ones)

        # Var(T) = E[T^2] - (E[T])^2  (with tinynegative clamp)
        v = second_moment - (mean**2)
        return v

    @property
    def upper_limit(self):
        """Return the upper limit of the PhaseType distribution.

        Returns:
            float: Infinity.
        """
        return float("inf")

    @property
    def lower_limit(self):
        """Return the lower limit of the PhaseType distribution.

        Returns:
            float: Zero.
        """
        return 0


class Erlang(PhaseType):
    """A shortcut for the Erlang distribution, using the PhaseType distribution.

    Attributes:
        rate (float): The rate spent in each phase.
        num_phases (int): The number of phases in series.
    """

    def __init__(self, rate, num_phases):
        """Initialize the Erlang distribution.

        Args:
            rate (float): The rate spent in each phase.
            num_phases (int): The number of phases in series.

        Raises:
            ValueError: If ``rate`` is not positive.
            ValueError: If ``num_phases`` is less than 1.
        """
        if rate <= 0.0:
            raise ValueError("Rate must be positive.")
        if num_phases < 1:
            raise ValueError("At least one phase is required.")
        self.rate = rate
        self.num_phases = num_phases
        initial_state = [1] + [0] * num_phases
        absorbing_matrix = [[0] * (num_phases + 1) for _ in range(num_phases + 1)]
        for phase in range(num_phases):
            absorbing_matrix[phase][phase] = -self.rate
            absorbing_matrix[phase][phase + 1] = self.rate
        super().__init__(initial_state, absorbing_matrix)

    def __repr__(self):
        """Return a string representation of the Erlang distribution."""
        return f"Erlang(rate={self.rate}, k={self.num_phases})"

    @property
    def mean(self):
        """Return the mean of the Erlang distribution.

        Returns:
            float: The mean.
        """
        return self.num_phases / self.rate

    @property
    def variance(self):
        """Return the variance of the Erlang distribution.

        Returns:
            float: The variance.
        """
        return self.num_phases / (self.rate**2)


class HyperExponential(PhaseType):
    """A shortcut for the HyperExponential distribution, using the PhaseType
    distribution.

    Attributes:
        rates (list): The rate of each phase.
        probs (list): The probability of starting in each phase.
    """

    def __init__(self, rates, probs):
        """Initialize the HyperExponential distribution.

        Args:
            rates (list): A vector of rates for each phase.
            probs (list): A probability vector for starting in each phase.

        Raises:
            ValueError: If any rate is not positive.
        """
        if any(r <= 0.0 for r in rates):
            raise ValueError("Rates must be positive.")
        self.rates = rates
        self.probs = probs
        initial_state = [*probs, 0]
        num_phases = len(probs)
        absorbing_matrix = [[0] * (num_phases + 1) for _ in range(num_phases + 1)]
        for phase in range(num_phases):
            absorbing_matrix[phase][phase] = -rates[phase]
            absorbing_matrix[phase][num_phases] = rates[phase]
        super().__init__(initial_state, absorbing_matrix)

    def __repr__(self):
        """Return a string representation of the HyperExponential distribution."""
        return "HyperExponential"

    @property
    def mean(self):
        """Return the mean of the HyperExponential distribution.

        Returns:
            float: The mean.
        """
        return sum(p / r for p, r in zip(self.probs, self.rates, strict=False))

    @property
    def variance(self):
        """Return the variance of the HyperExponential distribution.

        Returns:
            float: The variance.
        """
        mean = self.mean
        return sum(
            2 * p / (r**2) for p, r in zip(self.probs, self.rates, strict=False)
        ) - (mean**2)


class HyperErlang(PhaseType):
    """A shortcut for the HyperErlang distribution, using the PhaseType distribution.

    Attributes:
        rates (list): The rate of each phase.
        probs (list): The probability of starting in each phase.
        phase_lengths (list): The number of sub-phases in each phase.
    """

    def __init__(self, rates, probs, phase_lengths):
        """Initialize the HyperErlang distribution.

        Args:
            rates (list): A vector of rates for each phase.
            probs (list): A probability vector for starting in each phase.
            phase_lengths (list): The number of sub-phases in each phase.

        Raises:
            ValueError: If any rate is not positive.
            ValueError: If any phase length is less than 1.
        """
        if any(r <= 0.0 for r in rates):
            raise ValueError("Rates must be positive.")
        if any(n < 1 for n in phase_lengths):
            raise ValueError("At least one phase is required for each sub-phase.")
        initial_state = []
        for p, n in zip(probs, phase_lengths, strict=False):
            initial_state += [p]
            initial_state += [0] * (n - 1)
        initial_state += [0]

        num_phases = sum(phase_lengths)
        absorbing_matrix = [[0] * (num_phases + 1) for _ in range(num_phases + 1)]
        for i, r in enumerate(rates):
            for subphase in range(phase_lengths[i]):
                offset = sum(phase_lengths[:i])
                absorbing_matrix[offset + subphase][offset + subphase] = -r
                if subphase < phase_lengths[i] - 1:
                    absorbing_matrix[offset + subphase][offset + subphase + 1] = r
                else:
                    absorbing_matrix[offset + subphase][-1] = r
        self.rates = rates
        self.probs = probs
        self.phase_lengths = phase_lengths

        super().__init__(initial_state, absorbing_matrix)

    def __repr__(self):
        """Return a string representation of the HyperErlang distribution."""
        return "HyperErlang"

    @property
    def mean(self):
        """Return the mean of the HyperErlang distribution.

        Returns:
            float: The mean.
        """
        return sum(
            p * k / r
            for p, r, k in zip(self.probs, self.rates, self.phase_lengths, strict=False)
        )

    @property
    def variance(self):
        """Return the variance of the HyperErlang distribution.

        Returns:
            float: The variance.
        """
        mean = self.mean  # sum p * k / r
        #  second moment for Erlang(k, r) is k*(k+1)/r^2
        second_moment = sum(
            p * (k * (k + 1)) / (r**2)
            for p, r, k in zip(self.probs, self.rates, self.phase_lengths, strict=False)
        )
        v = second_moment - (mean**2)
        return v


class Coxian(PhaseType):
    """A shortcut for the Coxian distribution, using the PhaseType distribution."""

    def __init__(self, rates, probs):
        """Initialize the Coxian distribution.

        Args:
            rates (list): A vector of rates for each phase.
            probs (list): A vector of the probability of absorption at each phase.

        Raises:
            ValueError: If any rate is not positive.
            ValueError: If any probability is outside [0, 1].
            ValueError: If the final probability is not exactly 1.0.
        """
        if any(r <= 0.0 for r in rates):
            raise ValueError("Rates must be positive.")
        if any(p < 0 or p > 1.0 for p in probs):
            raise ValueError("Probability vector must have valid probabilities.")
        if probs[-1] != 1.0:
            raise ValueError(
                "The probability of going to the absorbing state from the final "
                "phase must be 1.0."
            )
        num_phases = len(rates)
        initial_state = [1] + [0] * num_phases
        absorbing_matrix = [[0] * (num_phases + 1) for _ in range(num_phases + 1)]
        for i, (p, r) in enumerate(zip(probs, rates, strict=False)):
            absorbing_matrix[i][i] = -r
            absorbing_matrix[i][i + 1] = (1 - p) * r
            absorbing_matrix[i][-1] = p * r
        super().__init__(initial_state, absorbing_matrix)

    def __repr__(self):
        """Return a string representation of the Coxian distribution."""
        return "Coxian"


class PoissonIntervals(Sequential):
    """A time-dependent Poisson distribution for arrivals.

    The number of arrivals in each time interval is sampled from a Poisson
    distribution, the arrival dates are distributed uniformly within each
    interval, and the consecutive differences of these dates are used as the
    inter-arrival times.

    Attributes:
        rates (list): The Poisson rate for each time interval.
        endpoints (list): The endpoints of each time interval.
        max_sample_date (float): The point after which no arrivals occur.
    """

    def __init__(self, rates, endpoints, max_sample_date):
        """Initialize the PoissonIntervals distribution.

        Args:
            rates (list): A list of Poisson rates for each time interval.
            endpoints (list): The endpoints of each time interval.
            max_sample_date (float): The point where no more arrivals can occur.

        Raises:
            ValueError: If any rate is negative.
            ValueError: If any endpoint is not positive.
            ValueError: If ``max_sample_date`` is not positive.
            ValueError: If the endpoints are not strictly increasing.
            ValueError: If the numbers of rates and endpoints differ.
        """
        if any(r < 0.0 for r in rates):
            raise ValueError("All rates must be positive.")
        if any(e <= 0.0 for e in endpoints):
            raise ValueError("All interval endpoints must be positive.")
        if max_sample_date <= 0.0:
            raise ValueError("Maximum sample date must be positive.")
        diffs = [s - t for s, t in zip(endpoints[1:], endpoints[:-1], strict=False)]
        if any(d <= 0.0 for d in diffs):
            raise ValueError("Interval endpoints must be strictly increasing.")
        if len(rates) != len(endpoints):
            raise ValueError(
                "Consistent number of intervals (rates and endpoints) must be used."
            )

        self.rates = rates
        self.endpoints = endpoints
        self.max_sample_date = max_sample_date
        self.get_intervals()
        self.get_dates()
        self.inter_arrivals = [
            t - s for s, t in zip(self.dates, self.dates[1:], strict=False)
        ] + [float("inf")]
        super().__init__(self.inter_arrivals)

    def __repr__(self):
        """Return a string representation of the PoissonIntervals distribution."""
        return "PoissonIntervals"

    def get_intervals(self):
        """Build the list of time intervals up to ``max_sample_date``."""
        self.num_intervals = len(self.endpoints)
        self.intervals = [(0, self.endpoints[0])]
        i, t1, t2 = 0, 0, 0
        while self.intervals[-1][-1] < self.max_sample_date:
            if i % self.num_intervals == self.num_intervals - 1:
                t2 = t1 + self.endpoints[-1]
            self.intervals.append(
                (
                    t1 + self.endpoints[i % self.num_intervals],
                    min(
                        t2 + self.endpoints[(i + 1) % self.num_intervals],
                        self.max_sample_date,
                    ),
                )
            )
            i += 1
            t1 = t2

    def get_dates(self):
        """Sample the arrival dates within each time interval."""
        self.dates = [0.0]
        for i, interval in enumerate(self.intervals):
            n = hciw.rng.poisson(
                self.rates[i % self.num_intervals] * (interval[1] - interval[0])
            )
            interval_dates = [
                random.uniform(interval[0], interval[1]) for _ in range(n)
            ]
            interval_dates = sorted(interval_dates)
            self.dates += interval_dates

    @property
    def overall_rate(self):
        """Return the overall rate across all intervals.

        Returns:
            float: The time-averaged Poisson rate.
        """
        deltas = [self.endpoints[0]] + [
            self.endpoints[i] - self.endpoints[i - 1]
            for i in range(1, len(self.endpoints))
        ]
        P = self.endpoints[-1]
        LambdaP = sum(r * d for r, d in zip(self.rates, deltas, strict=False))
        return LambdaP / P

    @property
    def mean(self):
        """Return the mean inter-arrival time.

        Returns:
            float: The reciprocal of the overall rate, or infinity.
        """
        O_R = self.overall_rate
        return 1 / O_R if O_R > 0 else float("inf")

    @property
    def variance(self):
        """Return the variance of the inter-arrival times.

        Returns:
            float: The variance, which is NaN.
        """
        return float("nan")

    @property
    def median(self):
        """Return the median inter-arrival time.

        Returns:
            float: The median, which is NaN.
        """
        return float("nan")

    @property
    def upper_limit(self):
        """Return the upper limit of the inter-arrival times.

        Returns:
            float: Infinity.
        """
        return float("inf")

    @property
    def lower_limit(self):
        """Return the lower limit of the inter-arrival times.

        Returns:
            float: Zero.
        """
        return 0


class Poisson(Distribution):
    """The Poisson distribution.

    Note that this is a discrete integer distribution, for use with batching.

    Attributes:
        rate (float): The rate parameter, lambda.
    """

    def __init__(self, rate):
        """Initialize the Poisson distribution.

        Args:
            rate (float): The rate parameter, lambda.

        Raises:
            ValueError: If ``rate`` is not positive.
        """
        if rate <= 0.0:
            raise ValueError("Poisson distribution must sample positive numbers only.")
        self.rate = rate

    def sample(self, t=None, ind=None):
        """Sample from the Poisson distribution.

        Args:
            t (float, optional): The current time. Defaults to None.
            ind (Individual, optional): The individual being sampled. Defaults to None.

        Returns:
            int: A sample from the distribution.
        """
        return hciw.rng.poisson(lam=self.rate)

    def __repr__(self):
        """Return a string representation of the Poisson distribution."""
        return f"Poisson(rate={self.rate})"

    @property
    def mean(self):
        """Return the mean of the Poisson distribution.

        Returns:
            float: The mean.
        """
        return self.rate

    @property
    def variance(self):
        """Return the variance of the Poisson distribution.

        Returns:
            float: The variance.
        """
        return self.rate

    @property
    def median(self):
        """Return the median of the Poisson distribution.

        Returns:
            float: An approximation of the median.
        """
        return math.floor(self.rate + (1 / 3) - (0.02 / self.rate))

    @property
    def upper_limit(self):
        """Return the upper limit of the Poisson distribution.

        Returns:
            float: Infinity.
        """
        return float("inf")

    @property
    def lower_limit(self):
        """Return the lower limit of the Poisson distribution.

        Returns:
            float: Zero.
        """
        return 0


class Geometric(Distribution):
    """The Geometric distribution.

    Note that this is a discrete integer distribution, for use with batching.

    Attributes:
        prob (float): The probability parameter.
    """

    def __init__(self, prob):
        """Initialize the Geometric distribution.

        Args:
            prob (float): The probability parameter.

        Raises:
            ValueError: If ``prob`` is not strictly between 0 and 1.
        """
        if prob <= 0.0 or prob >= 1:
            raise ValueError(
                "Geometric distribution must have parameter between 0 and 1."
            )
        self.prob = prob

    def sample(self, t=None, ind=None):
        """Sample from the Geometric distribution.

        Args:
            t (float, optional): The current time. Defaults to None.
            ind (Individual, optional): The individual being sampled. Defaults to None.

        Returns:
            int: A sample from the distribution.
        """
        return hciw.rng.geometric(p=self.prob)

    def __repr__(self):
        """Return a string representation of the Geometric distribution."""
        return f"Geometric(prob={self.prob})"

    @property
    def mean(self):
        """Return the mean of the Geometric distribution.

        Returns:
            float: The mean.
        """
        return 1 / self.prob

    @property
    def variance(self):
        """Return the variance of the Geometric distribution.

        Returns:
            float: The variance.
        """
        return (1 - self.prob) / (self.prob**2)

    @property
    def median(self):
        """Return the median of the Geometric distribution.

        Returns:
            float: The median.
        """
        return math.ceil(-1 / math.log(1 - self.prob, 2))

    @property
    def upper_limit(self):
        """Return the upper limit of the Geometric distribution.

        Returns:
            float: Infinity.
        """
        return float("inf")

    @property
    def lower_limit(self):
        """Return the lower limit of the Geometric distribution.

        Returns:
            float: Zero.
        """
        return 0


class Binomial(Distribution):
    """The Binomial distribution.

    Note that this is a discrete integer distribution, for use with batching.

    Attributes:
        n (int): The total number of experiments.
        prob (float): The probability parameter.
    """

    def __init__(self, n, prob):
        """Initialize the Binomial distribution.

        Args:
            n (int): The total number of experiments.
            prob (float): The probability parameter.

        Raises:
            ValueError: If ``prob`` is not strictly between 0 and 1.
            ValueError: If ``n`` is not a positive integer.
        """
        if prob <= 0.0 or prob >= 1:
            raise ValueError(
                "Binomial distribution have probability parameter between 0 and 1."
            )
        if not isinstance(n, int) or n <= 0:
            raise ValueError(
                "The number of trials of the Binomial distirbution must be a "
                "positive integer."
            )
        self.n = n
        self.prob = prob

    def sample(self, t=None, ind=None):
        """Sample from the Binomial distribution.

        Args:
            t (float, optional): The current time. Defaults to None.
            ind (Individual, optional): The individual being sampled. Defaults to None.

        Returns:
            int: A sample from the distribution.
        """
        return hciw.rng.binomial(n=self.n, p=self.prob)

    def __repr__(self):
        """Return a string representation of the Binomial distribution."""
        return f"Binomial(n={self.n}, prob={self.prob})"

    @property
    def mean(self):
        """Return the mean of the Binomial distribution.

        Returns:
            float: The mean.
        """
        return self.n * self.prob

    @property
    def variance(self):
        """Return the variance of the Binomial distribution.

        Returns:
            float: The variance.
        """
        return self.n * self.prob * (1 - self.prob)

    @property
    def median(self):
        """Return the median of the Binomial distribution.

        Returns:
            float: The rounded mean.
        """
        return round(self.n * self.prob)

    @property
    def upper_limit(self):
        """Return the upper limit of the Binomial distribution.

        Returns:
            float: Infinity.
        """
        return float("inf")

    @property
    def lower_limit(self):
        """Return the lower limit of the Binomial distribution.

        Returns:
            float: Zero.
        """
        return 0


class MixtureDistribution(Distribution):
    """A mixture distribution combining multiple probability distributions.

    Attributes:
        probs (List[float]): The weights of each distribution, summing to 1.
        dists (List[Distribution]): The distributions in the mixture.
    """

    def __init__(self, dists: list[Distribution], probs: list[float]) -> None:
        """Initialize the MixtureDistribution.

        Args:
            dists (List[Distribution]): The distributions to combine in the mixture.
            probs (List[float]): The weights of each distribution, summing to 1.
        """
        self.probs = probs
        self.dists = dists

    def sample(self, t: float | None = None, ind: Individual | None = None) -> float:
        """Generate a random sample from the mixture distribution.

        Args:
            t (float, optional): The current time. Defaults to None.
            ind (Individual, optional): The individual being sampled. Defaults to None.

        Returns:
            float: A sample from one of the distributions, chosen by weight.
        """
        chosen_dist = random.choices(population=self.dists, weights=self.probs, k=1)[0]

        return chosen_dist.sample(t, ind)

    def __repr__(self):
        """Return a string representation of the mixture distribution."""
        return "MixtureDistribution"

    @property
    def mean(self):
        """Return the mean of the mixture distribution.

        Returns:
            float: The weighted mean of the component distributions.
        """
        return sum(
            p * dist.mean for p, dist in zip(self.probs, self.dists, strict=False)
        )

    @property
    def variance(self):
        """Return the variance of the mixture distribution.

        Returns:
            float: The weighted variance of the component distributions.
        """
        mu = self.mean
        var = (
            sum(
                p * (dist.variance + dist.mean**2)
                for p, dist in zip(self.probs, self.dists, strict=False)
            )
            - mu**2
        )
        return max(var, 0)

    @property
    def upper_limit(self):
        """Return the upper limit of the mixture distribution.

        Returns:
            float: The largest component upper limit, or NaN if any is NaN.
        """
        if any(math.isnan(dist.upper_limit) for dist in self.dists):
            return float("nan")
        return max(dist.upper_limit for dist in self.dists)

    @property
    def lower_limit(self):
        """Return the lower limit of the mixture distribution.

        Returns:
            float: The smallest component lower limit, or NaN if any is NaN.
        """
        if any(math.isnan(dist.lower_limit) for dist in self.dists):
            return float("nan")
        return min(dist.lower_limit for dist in self.dists)
