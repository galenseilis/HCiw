API Reference
=============

This reference is generated from the source code with Sphinx autodoc, so it
stays in step with the implementation. Every public module, class, function,
and method is documented with `Google-style
<https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings>`_
docstrings.

Core
----

.. automodule:: hciw.import_params
   :members:

.. automodule:: hciw.simulation
   :members:

.. automodule:: hciw.network
   :members:

.. automodule:: hciw.auxiliary
   :members:

Distribution classes
--------------------

.. automodule:: hciw.dists.distributions
   :members:
   :exclude-members: Distribution

Disciplines
-----------

.. automodule:: hciw.disciplines
   :members:

Schedules
---------

.. automodule:: hciw.schedules
   :members:

Routing
-------

.. automodule:: hciw.routing.routing
   :members:

State trackers
--------------

.. automodule:: hciw.trackers.state_tracker
   :members:

Deadlock detection
------------------

.. automodule:: hciw.deadlock.deadlock_detector
   :members:

Simulation internals
--------------------

The classes below model the internal workings of a simulation. They are
documented for reference and for advanced use, but most users will interact
with HCiw only through ``hciw.create_network` and `hciw.Simulation``.

.. automodule:: hciw.node
   :members:

.. automodule:: hciw.arrival_node
   :members:

.. automodule:: hciw.exit_node
   :members:

.. automodule:: hciw.server
   :members:

.. automodule:: hciw.individual
   :members:

.. automodule:: hciw.data_record
   :members:

.. automodule:: hciw.processor_sharing
   :members:

.. automodule:: hciw.exactnode
   :members:
