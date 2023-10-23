import pickle

import ciw

class MetaNetwork:
  '''A class for managing ciw.network.Network objects.'''
	def __init__(self, initial_networks=None):

		# Store any final changes that should be made before 
		self.diffs = {}

		# Include any initial networks as an attribute.
		if initial_networks is None:
			self._networks = {}
		else:
			assert isinstance(initial_networks, dict)
      for name in initial_networks:
        assert isinstance(initial_networks[name], ciw.network.Network)
			self._networks = initial_networks
      
			# TODO: construct initial combined network.

  def add_network(self, network):
    '''Add a Ciw network to the metanetwork.'''
    if not isinstance(network, ciw.network.Network):
      raise ValueError('Input was not of type ciw.network.Network')
      
    if network.name in self._networks:
      raise ValueError("Metanetwork already contains a network with name {network.name}")
    else:
      self._networkx[network.name] = network

	def __add__(self, other):
		'''Union of metanetworks.'''
		...

	def __sub__(self, other):
		'''Difference of metanetworks.'''
		...

	def __div__(self, other):
		'''Difference of metanetworks.'''

	def _apply_final_overwrites(self):
		'''Make any final custom changes.

		Add components.
    Remove components.
		'''
		...

	def make_network(self):
		'''Return instance of combined network'''
		...

	def save(self, filename):
		'''Pickles instance.'''
		...

	def load(self, filename):
		'''Loads pickled instance.'''
    ...
