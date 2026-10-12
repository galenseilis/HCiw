.. _combine-dists:

How to Combine Distributions
============================

There are two ways to combine distributions in HCiw: arithmetically, and probabilistically.


Arithmetically Combining Distributions
--------------------------------------

As distribution objects inherit from the generic distirbution function, they can be *combined* using the operations :code:`+`, :code:`-`, :code:`*`, and :code:`/`.

For example, let's combine an Exponential distribution with a Deterministic distribution in all four ways::

    >>> import hciw
    >>> Exp_add_Det = hciw.dists.Exponential(rate=0.05) + hciw.dists.Deterministic(value=3.0)
    >>> Exp_sub_Det = hciw.dists.Exponential(rate=0.05) - hciw.dists.Deterministic(value=3.0)
    >>> Exp_mul_Det = hciw.dists.Exponential(rate=0.05) * hciw.dists.Deterministic(value=3.0)
    >>> Exp_div_Det = hciw.dists.Exponential(rate=0.05) / hciw.dists.Deterministic(value=3.0)

These combined distributions return the combined sampled values:

    >>> hciw.seed(10)
    >>> Ex = hciw.dists.Exponential(rate=0.05)
    >>> Dt = hciw.dists.Deterministic(value=3.0)
    >>> [round(Ex.sample(), 2) for _ in range(5)]
    [16.94, 11.2, 17.26, 4.62, 33.57]
    >>> [round(Dt.sample(), 2) for _ in range(5)]
    [3.0, 3.0, 3.0, 3.0, 3.0]

    >>> # Addition
    >>> hciw.seed(10)
    >>> [round(Exp_add_Det.sample(), 2) for _ in range(5)]
    [19.94, 14.2, 20.26, 7.62, 36.57]

    >>> # Subtraction
    >>> hciw.seed(10)
    >>> [round(Exp_sub_Det.sample(), 2) for _ in range(5)]
    [13.94, 8.2, 14.26, 1.62, 30.57]

    >>> # Multiplication
    >>> hciw.seed(10)
    >>> [round(Exp_mul_Det.sample(), 2) for _ in range(5)]
    [50.83, 33.61, 51.78, 13.85, 100.7]

    >>> # Division
    >>> hciw.seed(10)
    >>> [round(Exp_div_Det.sample(), 2) for _ in range(5)]
    [5.65, 3.73, 5.75, 1.54, 11.19]


Probabilistically Combining Distributions
-----------------------------------------

Distributions can also be combined probabilistically. A countable and finite mixture distriubtion probabilistically chooses to sample from one of a number of given distributions. This is given by the :code:`MixtureDistribution` object. Given a number of distributions each with PDF :math:`D_i(x)`, each with a probability :math:`p_i`, such that :math:`\sum_i p_i = 1`, then the Mixture distribution has PMF :math:`f(x) = \sum_i p_i D_i(x)`

For example, say let's make a mixture distribution that samples from an Exponential distribution rate 1 with probability 0.5, another Exponential distribution rate 2 with probability 0.2, a Uniform distribution between 0.2 and 0.8 with probability 0.2, and returns a Deterministic value of 0.5 with probability 0.1. We can do this with:

    >>> Exp1 = hciw.dists.Exponential(rate=1)
    >>> Exp2 = hciw.dists.Exponential(rate=2)
    >>> Unif = hciw.dists.Uniform(lower=0.2, upper=0.8)
    >>> Det5 = hciw.dists.Deterministic(0.5)

    >>> M = hciw.dists.MixtureDistribution(dists=[Exp1, Exp2, Unif, Det5], probs=[0.5, 0.2, 0.2, 0.1])
