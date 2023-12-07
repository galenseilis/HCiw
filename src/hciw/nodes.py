from typing import Callable, NoReturn, Union

import ciw
import numpy as np
from sklearn.base import BaseEstimator

class SKRouter(ciw.Node):
    '''
    Routes individuals depending on the system's state and time using a Scikit-Learn model.

    Args:
        get_clf_data (Callable): A function that takes an instance of Self and an individual as input
                                and returns the data used for prediction of the next node.
        skmodel (BaseEstimator): An instance of a scikit-learn compatible model.
        method (str, optional): Label indicating how the next node is obtained from skmodel.
                                   Defaults to `'predict_proba'`.

    Raises:
        ValueError: If method is predict_proba the model does not have the `predict_proba` method.

    Attributes:
        get_pred_data (Callable): The provided function for obtaining prediction data.
        skmodel (BaseEstimator): The scikit-learn model used for predicting the next node.

    Methods:
        next_node(ind: ciw.Individual) -> ciw.Node:
            Predicts the next node based on the provided individual's data using skmodel.

    '''

    def __init__(self, get_pred_data: Callable, skmodel: BaseEstimator, method: Union[str,Callable] = 'predict_proba') -> NoReturn:
        '''
        Initializes an instance of SKRouter.

        Args:
            get_pred_data (Callable): A function that takes an instance of Self and an individual as input
                                    and returns the data used for prediction of the next node.
            skmodel (BaseEstimator): An instance of a scikit-learn compatible model.
            method (str, optional): Label indicating how the next node is obtained from skmodel.
                                   Defaults to `'predict_proba'`.

        Raises:
            ValueError: If sampling is True and the skmodel does not have the `predict_proba` method.

        '''
        self.get_data = get_pred_data
        self.clf = skmodel

        if method not in ('predict_proba', 'predict') and not callable(method):
            raise NotImplementedError(f'{self.method} is not supported.')
        self.method: = method


    def next_node(self, ind: ciw.Individual) -> ciw.Node:
        '''
        Predicts the next node based on the provided individual's data using the scikit-learn model.

        Args:
            ind (ciw.Individual): The individual for which the next node needs to be predicted.

        Returns:
            ciw.Node: The predicted next node.

        '''
        
        pred_data = self.get_pred_data(self, ind)

        if self.method == 'predict_proba':
            if hasattr(self.skmodel, 'predict_proba'):
                probs = self.skmodel.predict_proba(pred_data)[0]
                chosen_node = self.skmodel.classes_ @ np.random.multinomial(1, probs)
            else:
                probs = self.skmodel.predict(pred_data)[0]
                chosen_node = range(len(self.simulation.nodes)) @ np.random.multinomial(1, probs)
        elif self.method == 'predict':
            chosen_node = self.skmodel.predict(pred_data)[0]
        else:
            chosen_node = self.method(self.skmodel.predict(pred_data)[0])

        return self.simulation.nodes[chosen_node]
