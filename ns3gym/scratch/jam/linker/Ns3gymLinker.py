## @file    Ns3gymLinker.py
#  @brief   Linker between ns3gym and agents.
#  @details This file contains the DatasetLinker class.
#  @author  Romain Durieux and Nathan Trouillet (2022)

from data.Dataset import Context
from ns3gym import ns3env
from linker.Linker import Linker

## @brief   Ns3gymLinker Class. 
#  @details This class is used to retrieve context data to the agent using ns3gym.
#           This class extends the Linker class.
class Ns3gymLinker(Linker):

    ## @brief   Ns3gymLinker constructor.
    #  @details This constructor needs at least 3 parameters and maximum 5 parameters.
    #
    #  @param   nodeId      The N-th Process created.
    #  @param   C           The calculation window (eg. : for an average sum(data)/C).
    #  @param   L           The delay between the first and the second calculated value. The second value will be calculated at t-L.
    #  @param   mode        Computation mode to use (cf. QoSComputation.py). Default = "QOS".
    #  @param   evalType    Evaluation mode to use (cf. QoSEvaluation.py). Default = "Std".
    def __init__(self, nodeId, C, L, mode="QOS", evalType="Std"):
        
        super().__init__(nodeId, C, L, mode, evalType)
        
        self.port = 5555 + self.id
        simArgs = {"--agentNum": 9}
        self.env = ns3env.Ns3Env(port=self.port, startSim=False, simArgs=simArgs, debug=False)
        self.env.reset()

        self.ob_space = self.env.observation_space
        self.ac_space = self.env.action_space

        print("-------port : ",self.port)
        print("Observation space: ", self.ob_space,  self.ob_space.dtype)
        print("Action space: ", self.ac_space, self.ac_space.dtype)

    ## @brief   The method that refreshes the data and feeds the histories.
    #  @details The method that refreshes data and populates histories with context data from ns3gym.
    def next(self):
        if self.computer.data != []:
            self.histo.append(self.computer.data)
        
        obs, reward, self.done, info = self.env.step(self.env.action_space.sample())
        self.label.append(obs.pop())
        
        features = [x for x in obs]# obs seems to be an object that only accept int values, so we recreate the list using obs to allows float values in it
        # new_context_data = features[1]/2 #LS/2
        # features.append(new_context_data)
        
        self.computer.data = Context(self.i, features)
        self.i += 1
