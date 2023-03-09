## @file    QoSEvaluation.py
#  @brief   File containing the Evaluator class.
#  @details File containing all QoS evaluation methods.
#  @author  Romain Durieux and Nathan Trouillet (2022)

## @brief   Evaluator Class. 
#  @details This class is used to evaluate an attack based on the data provided.
class Evaluator:
    ## @brief   Evaluator constructor.
    #  @details This constructor needs 4 parameters.
    #
    #  @param   mode        Computation mode to use (cf. QoSComputation.py).
    #  @param   qosHisto    The QoS historic.
    #  @param   cWindow     The calculation window (eg. : for an average sum(data)/C).
    #  @param   lDelay      The delay between the first and the second calculated value. The second value will be calculated at t-L.
    def __init__(self, mode, qosHisto, cWindow, lDelay):
        self.mode = mode
        self.qosHisto = qosHisto
        self.cWindow = cWindow
        self.lDelay = lDelay
    
    ## @brief   The method that gets historical data at t-lDelay.
    #  @details The methode that get the historical data at t-lDelay.
    #
    #  @return  The historical data at t-lDelay.
    def getQoSatTminusL(self):
        return self.qosHisto[len(self.qosHisto - 1) - self.lDelay]

    ## @brief   Is a greater than or equal to b, taking into account the epsilon fluctuation.
    #  @details Is a greater than or equal to b, taking into account the epsilon fluctuation.
    #
    #  @return  A boolean value.
    def aUpperEqualsBEpsilon(self, a, b, epsilon):
        return float(a) >= (float(b) - epsilon)

    ## @brief   The method that selects the QoS assessment.
    #  @details This method selects the QoS assessment based on the parameters.
    #
    #  @return  A boolean representing if we are attacked.
    def getEval(self, qos, qost1, epsilon, wasAttacked):
        if self.mode == "Std":
            return self.simpleEval(qos, qost1, wasAttacked, epsilon)
        elif self.mode == "QOSatTandTL":
            return self.evaluateQOSatTandTL(qos, qost1, epsilon)
        else :
            print("Error, unknown evaluation mode")
            return -1

    ## @brief   The simple jam evaluation.
    #  @details This method is simple QoS assessment. If the QoS at t+1 is worse
    #           than the QoS at t, it means we are under attack.
    #
    #  @return  A boolean representing if we are attacked.
    def simpleEval(self, qos, qost1, wasAttacked, epsilon):
        attack = True
        if wasAttacked:
            attack = self.aUpperEqualsBEpsilon(qos, qost1, epsilon)
        else:
            attack = not self.aUpperEqualsBEpsilon(qost1, qos, epsilon)

        return attack
    
    ## @brief   The percentage jam evaluation.
    #  @details This method makes a percentage according to the QoS at t and t+1. 
    #           If this percentage is less than 100%, it means that we are under a jam attack.
    #
    #  @return  A boolean representing if we are attacked.
    def evaluateQOSatTandTL(self,qos, qostl, epsilon):
        attack = False
        if qostl > 0 :
            a = (qos*100)/qostl
        else :
            a = 100
        if self.aUpperEqualsBEpsilon(100, a, float(epsilon)):
            attack = True
            
        return attack
