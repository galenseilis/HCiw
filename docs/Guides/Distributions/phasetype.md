<a id="phase-type"></a>

# How to Set Phase-Type Distributions

One particular subset of distributions offered by HCiw is Phase-Type distributions. These are very useful and versatile family of distributions defined by absorbing Markov chains. That is, given a probability vector $\alpha$ representing the probability of the starting state, and an transition rate matrix $M$ of an absorbing Markov chain, these are distributions given by the time to absorption. It is therefore a random sum of exponential variables.

The diagram below gives a general representation of an absorbing Markov chain with four states, 1, 2, 3, and the absorbing state $\star$:

<img src="../../_static/phasetype.svg" class="align-center" style="width:100.0%" alt="Absorbing Markov chain of a general Phase-Type distribution." />

The corresponding Phase-Type distribution would be defined by an initial state probability vector:

$$
\alpha = \left(p_1, p_2, p_3, 0\right)
$$

and the transition matrix corresponding to the absorbing Markov chain:

$$
\begin{aligned}
M = \begin{pmatrix}
-\sum_{i \neq 1} q_{1i} & q_{12} & q_{13} & q_{14} \\
q_{21} & -\sum_{i \neq 2} q_{2i} & q_{23} & q_{24} \\
q_{31} & q_{32} & -\sum_{i \neq 3} q_{3i} & q_{34} \\
0 & 0 & 0 & 0
\end{pmatrix}
\end{aligned}
$$

An example of implementing this in HCiw:

``` python
>>> import hciw
>>> initial_state = [0.7, 0.2, 0.1, 0.0]
>>> absorbing_matrix = [
...     [-6, 2, 0, 4],
...     [0, -3, 3, 0],
...     [1, 0, -5, 4],
...     [0, 0, 0, 0]
... ]
>>> Ph = hciw.dists.PhaseType(initial_state, absorbing_matrix)
```

Phase-Type distributions are a large family of distributions. Some Phase-Type distributions that have particular structures to their underlying absorbing Markov chain can be particularly useful, and HCiw offers helper classes for some of these to build the transition matrix for you. They are outlined below.

## Erlang Distributions

An Erlang distribution with parameters $\lambda$ and $n$ is the sum of $n$ Exponential distributions with parameter $\lambda$. This can be equivalently defined as the Phase-Type distribution with the following structure:

<img src="../../_static/erlang.svg" class="align-center" style="width:100.0%" alt="Absorbing Markov chain of an Erlang distribution." />

The corresponding Phase-Type distribution would be defined by an initial state probability vector:

$$
\alpha = \left(1, 0, \dots, 0\right)
$$

and the transition matrix:

$$
\begin{aligned}
M = \begin{pmatrix}
-\lambda & \lambda & 0 & \dots & 0 & 0 \\
0 & -\lambda & \lambda & \dots & 0 & 0 \\
0 & 0 & -\lambda & \dots & 0 & 0 \\
\vdots & \vdots & \vdots & \dots & \vdots & \vdots \\
0 & 0 & 0 & \dots & -\lambda & \lambda \\
0 & 0 & 0 & \dots & 0 & 0 \\
\end{pmatrix}
\end{aligned}
$$

Rather than define these, in HCiw we can create an Erlang distribution from the parameters $\lambda$ and $n$:

``` python
>>> Er = hciw.dists.Erlang(rate=9, num_phases=4)
```

## HyperExponential Distributions

An HyperExponential distribution is defined by a probability vector $\mathbf{p}$ and rate vector $\mathbf{\lambda}$, and samples an Exponential distribution with parameter $\lambda_i$ with probability $p_i$. This can be equivalently defined as the Phase-Type distribution with the following structure:

<img src="../../_static/hyperexponential.svg" class="align-center" style="width:100.0%" alt="Absorbing Markov chain of a HyperExponential distribution." />

When $\mathbf{p} = \left(p_1, p_2, \dots, p_n\right)$ and $\mathbf{\lambda} = \left(\lambda_1, \lambda_2, \dots, \lambda_n\right)$ the corresponding Phase-Type distribution would be defined by an initial state probability vector:

$$
\alpha = \left(p_1, p_2, \dots, p_n, 0\right)
$$

and the transition matrix:

$$
\begin{aligned}
M = \begin{pmatrix}
-\lambda_1 & 0 & 0 & \dots & 0 & \lambda_1 \\
0 & -\lambda_2 & 0 & \dots & 0 & \lambda_2 \\
0 & 0 & -\lambda_3 & \dots & 0 & \lambda_3 \\
\vdots & \vdots & \vdots & \ddots & 0 & \vdots \\
0 & 0 & 0 & \dots & -\lambda_n & \lambda_n \\
0 & 0 & 0 & \dots & 0 & 0
\end{pmatrix}
\end{aligned}
$$

Rather than define these, in HCiw we can create a HyperExponential distribution from the parameters $\mathbf{\lambda}$ and $\mathbf{p}$:

``` python
>>> Hx = hciw.dists.HyperExponential(rates=[9, 5, 6, 1], probs=[0.2, 0.1, 0.6, 0.1])
```

## HyperErlang Distributions

A HyperErlang distribution is defined by parameters $\mathbf{\lambda}$, $\mathbf{p}$, and $\mathbf{n}$, and samples an Erlang distribution of size $n_i$ with parameter $\lambda_i$ with probability $p_i$. This can be equivalently defined as the Phase-Type distribution with the following structure:

<img src="../../_static/hypererlang.svg" class="align-center" style="width:100.0%" alt="Absorbing Markov chain of a HyperErlang distribution." />

When $\mathbf{p} = \left(0.5, 0.25, 0.25\right)$, $\mathbf{\lambda} = \left(5, 2, 3\right)$, and $\mathbf{n} = \left(2, 1, 2\right)$ the corresponding Phase-Type distribution would be defined by an initial state probability vector:

$$
\alpha = \left(0.5, 0, 0.25, 0.25, 0, 0\right)
$$

and the transition matrix:

$$
\begin{aligned}
M = \begin{pmatrix}
-5 & 5 & 0 & 0 & 0 & 0 \\
0 & -5 & 0 & 0 & 0 & 5 \\
0 & 0 & -2 & 0 & 0 & 2 \\
0 & 0 & 0 & -3 & 3 & 0 \\
0 & 0 & 0 & 0 & -3 & 3 \\
0 & 0 & 0 & 0 & 0 & 0
\end{pmatrix}
\end{aligned}
$$

Rather than define these, in HCiw we can create a HyperErlang distribution from the parameters $\mathbf{\lambda}$, $\mathbf{p}$, and $\mathbf{n}$:

``` python
>>> Hg = hciw.dists.HyperErlang(rates=[5, 2, 3], probs=[0.5, 0.25, 0.25], phase_lengths=[2, 1, 2])
```

## Coxian Distributions

A Coxian distribution is defined by parameters $\mathbf{\lambda}$, the rates of each phase, and $\mathbf{p}$, the probability of going to the absorbing state after each phase. This can be equivalently defined as the Phase-Type distribution with the following structure:

<img src="../../_static/coxian.svg" class="align-center" style="width:100.0%" alt="Absorbing Markov chain of a general Coxian distribution." />

When $\mathbf{p} = \left(p_1, p_2, \dots, p_n\right)$ and $\mathbf{\lambda} = \left(\lambda_1, \lambda_2, \dots, \lambda_n\right)$ the corresponding Phase-Type distribution would be defined by an initial state probability vector:

$$
\alpha = \left(1, 0, \dots, 0\right)
$$

and the transition matrix:

$$
\begin{aligned}
M = \begin{pmatrix}
-\lambda_1 & (1 - p_1)\lambda_1 & 0 & 0 & \dots & 0 & p_1 \lambda_1 \\
0 & -\lambda_2 & (1 - p_2)\lambda_2 & 0 & \dots & 0 & p_2 \lambda_2 \\
0 & 0 & -\lambda_3 & (1 - p_3)\lambda_3 & \dots & 0 & p_3 \lambda_3 \\
\vdots & \vdots & \vdots & \vdots & \ddots & \vdots & \vdots \\
0 & 0 & 0 & 0 & \dots -\lambda_n & \lambda_n \\
0 & 0 & 0 & 0 & \dots & 0 & 0 \\
\end{pmatrix}
\end{aligned}
$$

Rather than define these, in HCiw we can create a Coxian distribution from the parameters $\mathbf{\lambda}$ and $\mathbf{p}$:

``` python
>>> Cx = hciw.dists.Coxian(rates=[5, 2, 3, 7], probs=[0.5, 0.3, 0.65, 1])
```
