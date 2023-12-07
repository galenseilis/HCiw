from typing import Callable, NoReturn

import ciw
import numpy as np
from sklearn.base import ClassifierMixin

class SKRouter(ciw.Node):
    '''
    Routes individuals depending on the system's state and time.

    Args:
        get_clf_data (Callable): A function that takes an instance of SKRouter and an individual as input
                                and returns the data used for classification.
        classifier (ClassifierMixin): An instance of a scikit-learn compatible classifier.
        sampling (bool, optional): Flag indicating whether to use sampling for predicting the next node.
                                   Defaults to True.

    Raises:
        ValueError: If sampling is True and the classifier does not have the `predict_proba` method.

    Attributes:
        get_data (Callable): The provided function for obtaining classification data.
        clf (ClassifierMixin): The classifier used for predicting the next node.

    Methods:
        next_node(ind: ciw.Individual) -> ciw.Node:
            Predicts the next node based on the provided individual's data using the classifier.

    '''

    def __init__(self, get_clf_data: Callable, classifier: ClassifierMixin, sampling: bool = True) -> NoReturn:
        '''
        Initializes an instance of SKRouter.

        Args:
            get_clf_data (Callable): A function that takes an instance of SKRouter and an individual as input
                                    and returns the data used for classification.
            classifier (ClassifierMixin): An instance of a scikit-learn compatible classifier.
            sampling (bool, optional): Flag indicating whether to use sampling for predicting the next node.
                                       Defaults to True.

        Raises:
            ValueError: If sampling is True and the classifier does not have the `predict_proba` method.

        '''
        self.get_data = get_clf_data
        self.clf = classifier

        if sampling and not hasattr(classifier, 'predict_proba'):
            raise ValueError('Classifier does not have `predict_proba` method.')

    def next_node(self, ind: ciw.Individual) -> ciw.Node:
        '''
        Predicts the next node based on the provided individual's data using the classifier.

        Args:
            ind (ciw.Individual): The individual for which the next node needs to be predicted.

        Returns:
            ciw.Node: The predicted next node.

        '''
        clf_data = self.get_clf_data(self, ind)

        if sampling:
            probs = self.clf.predict_proba(clf_data)[0]
            chosen_node = self.clf.classes_ @ np.random.multinomial(1, probs)
        else:
            chosen_node = (self.clf.predict(clf_data) + 1)[0]

        return self.simulation.nodes[chosen_node]
