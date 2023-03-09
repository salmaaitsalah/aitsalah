## @file    Model.py
#  @brief   Algorithm model used.
#  @details This file contains the Model class.
#  @author  Romain Durieux and Nathan Trouillet (2022), using the work of gutowski (2019)

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from algo.EXP3 import Exp3
from algo.Egreedy import Egreedy
from algo.LinTS import LinearThompsonSampling
from algo.LinUCB import LinUCB
from algo.Random import Random
from algo.TS import ThompsonSampling
from algo.UCB1 import Ucb1

## @brief   Model Class. 
#  @details This class is used to select which algorithm to use.
class Model:
    ## @brief   Model constructor.
    #  @details This constructor needs 3 parameters.
    #
    #  @param   model_name  Name of the algorithm to use during the learning.
    #  @param   arms        List of arms we can pull.
    #  @param   contexts    Starting context, init to an empty list if no pre-training is done.
    def __init__(self, model_name, arms, contexts):
        gamma = delta = epsilon = 0.1

        if model_name == "random":
            self.model = Random(arms, contexts)
        elif model_name == "linucb":
            self.model = LinUCB(arms, contexts, delta)
        elif model_name == "egreedy":
            self.model = Egreedy(arms, contexts, epsilon)
        elif model_name == "ucb1":
            self.model = Ucb1(arms, contexts)
        elif model_name == "ts":
            self.model = ThompsonSampling(arms, contexts)
        elif model_name == "lints":
            self.model = LinearThompsonSampling(arms, contexts, delta, 0.01)
        elif model_name == "exp3":
            self.model = Exp3(arms, contexts, gamma)

    ## @brief   The method that append new context data to the context historics.
    #  @details The method that append new context data to the selected model.
    def appendContext(self, con):
        self.model.appendContext(con)
        
    ## @brief   The method that reset the context historics.
    #  @details The method that reset the context historics from the selected model.
    def resetContext(self):
        self.model.contexts.clear()