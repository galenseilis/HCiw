
# API Reference

This reference is generated from the source code with
[mkdocstrings](https://mkdocstrings.github.io/), so it stays in step with the
implementation. Every public module, class, function, and method is documented
with [Google-style](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings)
docstrings.

## Core

::: hciw.import_params

::: hciw.simulation

::: hciw.network

::: hciw.auxiliary

## Warm starts

::: hciw.waitlist

## Distribution classes

::: hciw.dists.distributions
    options:
      filters: ["!^Distribution$"]

## Disciplines

::: hciw.disciplines

## Schedules

::: hciw.schedules

## Routing

::: hciw.routing.routing

## State trackers

::: hciw.trackers.state_tracker

## Deadlock detection

::: hciw.deadlock.deadlock_detector

## Simulation internals

The classes below model the internal workings of a simulation. They are
documented for reference and for advanced use, but most users will interact
with HCiw only through `hciw.create_network` and `hciw.Simulation`.

::: hciw.node

::: hciw.arrival_node

::: hciw.exit_node

::: hciw.server

::: hciw.individual

::: hciw.data_record

::: hciw.processor_sharing

::: hciw.exactnode
