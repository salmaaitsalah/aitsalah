## @file    Linker.py
#  @brief   Abstract link between data and agents.
#  @details This file contains the Linker class.
#  @author  Romain Durieux and Nathan Trouillet (2022)

from linker.QoSComputation import Computer
from linker.QoSEvaluation import Evaluator
from util.FilesLoader import FilesLoader

## @brief   Linker Class. 
#  @details This class is used to retrieve agent context data. This involves saving a 
#           history of context data and a history of QoS values. This class also defines
#           to the agent when no more data is given, the different QoS calculations and 
#           the different evaluations.
class Linker :
    ## @brief   Linker constructor.
    #  @details This constructor needs at least 3 parameters and maximum 5 parameters.
    #
    #  @param   nodeId      The N-th Process created.
    #  @param   C           The calculation window (eg. : for an average sum(data)/C).
    #  @param   L           The delay between the first and the second calculated value. The second value will be calculated at t-L.
    #  @param   mode        Computation mode to use (cf. QoSComputation.py). Default = "QOS".
    #  @param   evalType    Evaluation mode to use (cf. QoSEvaluation.py). Default = "Std".
    def __init__(self, nodeId, C, L, mode="QOS", evalType="Std"):
        self.data = []
        self.histo = []
        self.qosHistory = []
        self.label = []
        self.i = 0

        self.evalMode = evalType
        self.mode = mode
        self.id = nodeId
        self.cWindow = int(C)
        self.lDelay = int(L)

        self.computer = Computer(mode, self.data, self.qosHistory, self.cWindow, self.lDelay, self.i)
        self.evaluator = Evaluator(evalType, self.qosHistory, self.cWindow, self.lDelay)
    
    ## @brief   The method that gives information about the arms.
    #  @details This method gives the information about the arms contained in the "data/classes.txt" file.
    #
    #  @return  The number of arms, the arms object, the arms id.
    def getArmsInfo(self):
        classes = "./data/classes.txt"

        f_arms = FilesLoader(classes)
        store_arms = f_arms.loadFile()
        res_arms = f_arms.processFileArms(store_arms)
        arms = res_arms[2]
        nb_arms = res_arms[1]
        d_arms = res_arms[0]

        f_arms.close(store_arms)

        return nb_arms, arms, d_arms
    
    ## @brief   The methode getData.
    #  @details This method invokes the "next()" method, which will refresh the data and feed the histories.
    #
    #  @return  The context data.
    def getData(self):
        self.next()
        return self.computer.data

    ## @brief   The methode getQOS.
    #  @details This method will calculate the next QoS based on the mode of the class.
    #
    #  @return  The computed QoS (Cf. QoSComputation.py)
    def getQOS(self): 
        return self.computer.getQOS()
    
    ## @brief   The methode getEvaluation.
    #  @details This method will evaluate an attack.
    #
    #  @param   qos         First QoS to compare.
    #  @param   qost1       Second QoS (eg. : QoS at t-L).
    #  @param   epsilon     Epsilon represents the fluctuation that we validate (QoS + epsilon = QoS and QoS - epsilon = QoS).
    #  @param   wasAttacked Last attack. Default = False.
    #
    #  @return  A boolean calculated by the evaluation chosen by the evaluation mode (Cf. QoSEvaluation.py)
    def getEvaluation(self, qos, qost1, epsilon, wasAttacked = False):
        return self.evaluator.getEval(qos, qost1, epsilon, wasAttacked)

    ## @brief   The methode getHisto.
    #  @details This method returns the historical context.
    #
    #  @return  The historical context.
    def getHisto(self):
        return self.histo

    ## @brief   The methode getEnv.
    #  @details This method returns a computed environment variable for the linker.
    #
    #  @return  A list of the environment variable.
    def getEnv(self):
        return self.env
    
    ## @brief   The methode isDone.
    #  @details This method returns a boolean to know if there is data left to iterate.
    #
    #  @return  If the script is done.
    def isDone(self):
        return self.done
        