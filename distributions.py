'''Custom distributions to be used with Ciw.'''

class SeqPMFNaive(cw.distributions.Distribution):
	'''Samples from a sequence of PMFs, else a naive extrapolation assumption.
	
	Input times are rounded.

	The naive forecast assumption is that the probability mass function in the future of the sequence is the same as the last element of the sequence.
	The naive backcast assumption is that the probability mass function in the past of the sequence is the same as the first element of the sequence.
	These naive extrapolation assumptions are not intended
	'''
	def __init__(self, distseq):
		if not all(map(lambda o: isinstance(o, ciw.dists.Pmf))):
			raise ValueError('Not all inputs of distseq were of type ciw.dists.Pmf')
		self.distseq = distdeq

	def sample(self, t, ind=None):
		time = round(t) # TODO: Remove once probability interpolation is implemented.
		if time in self.distseq:
			return self.distseq[time].sample(time, ind)
		elif time > max(self.distseq):
			return self.distseq[max(self.distseq)].sample(time, ind)
		elif time < min(self.distseq)::
			return self.distseq[min(self.distseq)].sample(time, ind)
		else:# TODO: Linearly interpolate probabilities wrt t
			raise ValueError(f'Unsupported sampling time of {t} in SeqPMFNaive.')
