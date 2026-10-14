<a id="kendall-notation"></a>

# Kendall's Notation

Kendall's notation is used as shorthand to denote single node queueing systems [WS09](references.md#WS09).

A queue is characterised by:

$$
A/B/C/X/Y/Z
$$

where:

- $A$ denotes the distribution of inter-arrival times
- $B$ denotes the distribution of service times
- $C$ denotes the number of servers
- $X$ denotes the queueing capacity
- $Y$ denotes the size of the population of customers
- $Z$ denotes the queueing discipline

For the parameters $A$ and $B$, a number of shorthand notation is available. For example:

- $M$: Markovian or Exponential distribution
- $E$: Erlang distribution (a special case of the Gamma distribution)
- $C_k$: Coxian distribution of order $k$
- $D$: Deterministic distribution
- $G$ / $GI$: General / General independent distribution

The parameters $X$, $Y$ and $Z$ are optional, and are assumed to be $\infty$, $\infty$, and First In First Out (FIFO) respectively. Other options for the queueing schedule $Z$ may be SIRO (Service In Random Order), LIFO (Last In First Out), and PS (Processor Sharing).

Some examples:

- $M/M/1$:  
  - Exponential inter-arrival times
  - Exponential service times
  - 1 server
  - Infinite queueing capacity
  - Infinite population
  - First in first out

- $M/D/\infty/\infty/1000$:  
  - Exponential inter-arrival times
  - Deterministic service times
  - Infinite servers
  - Infinite queueing capacity
  - Population of 1000 customers
  - First in first out

- $G/G/1/\infty/\infty/\text{SIRO}$:  
  - General distribution for inter-arrival times
  - General distribution for service times
  - 1 server
  - Infinite queueing capacity
  - Infinite population
  - Service in random order

- $M/M/4/5$:  
  - Exponential inter-arrival times
  - Exponential service times
  - 4 servers
  - Queueing capacity of 5
  - Infinite population
  - First in first out
