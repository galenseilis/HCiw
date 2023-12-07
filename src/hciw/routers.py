from typing import Callable, NoReturn

import ciw
import numpy as np
from sklearn.base import ClassifierMixin

class SKRouter(ciw.Node):
  '''Routes individuals depending on the system's state and time.'''

	def __init__(self, get_clf_data:Callable, classifier:ClassifierMixin, sampling=True) -> NoReturn:
		self.get_data = get_data
		self.clf = classifier

		if sampling and not hasattr(classifier, 'predict_proba'):
			raise ValueError('Classifier does not have `predict_proba` method.')

	def next_node(self, ind:ciw.Individual) -> ciw.Node:
	
    		clf_data = self.get_clf_data(self, ind)
		
		if sampling:
			probs = self.clf.predict_proba(clf_data)[0]
			chosen_node = self.clf.classes_ @ np.random.multinomial(1, probs)
		else:
			chosen_node = (self.clf.predict(clf_data) + 1)[0]
			
		return self.simulation.nodes[chosen_node]
