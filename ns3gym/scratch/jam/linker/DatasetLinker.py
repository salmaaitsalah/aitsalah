## @file    DatasetLinker.py
#  @brief   Link between dead dataset and agents.
#  @details This file contains the DatasetLinker class.
#  @author  Romain Durieux and Nathan Trouillet (2022)

from data.Dataset import Context
from linker.Linker import Linker

## @brief   DatasetLinker Class. 
#  @details This class is used to retrieve context data back to the agent using the dead dataset.
#           This class extends the Linker class.
class DatasetLinker(Linker):
    ## @brief   DatasetLinker constructor.
    #  @details This constructor needs at least 3 parameters and maximum 5 parameters.
    #
    #  @param   nodeId      The N-th Process created.
    #  @param   C           The calculation window (eg. : for an average sum(data)/C).
    #  @param   L           The delay between the first and the second calculated value. The second value will be calculated at t-L.
    #  @param   mode        Computation mode to use (cf. QoSComputation.py). Default = "QOS".
    #  @param   evalType    Evaluation mode to use (cf. QoSEvaluation.py). Default = "Std".
    def __init__(self, nodeId, C, L, mode="QOS",evalType="Std"):
        super().__init__(nodeId, C, L, mode, evalType)
        
        self.dataset = self.readDataFile()
        self.label = self.readLabelFile()

    ## @brief   The method that refreshes the data and feeds the histories.
    #  @details The method that refreshes data and populates histories with context data from the dead dataset.
    def next(self):
        if self.computer.data != []:
            self.histo.append(self.data)
        
        self.obs = self.getDataFromDataset(self.i)
        self.label.append(self.getLabelFromDataset(self.i))
        
        new_context_data = self.obs[1]/2 #LS/2
        # self.obs.append(new_context_data)
        
        self.computer.data = Context(self.i, self.obs)
        self.i += 1

    ## @brief   The method that reads a file.
    #  @details The method that reads a file to get the dead dataset's context values.
    #
    #  @return  All lines of the file.
    def readFile(self, file):
        data_file = f"./data/node{self.id}/{file}.txt"
        with open(data_file, 'r') as f :
            return f.readlines()
    
    ## @brief   The method that reads context values ​​from the dead dataset.
    #  @details The method that reads context values ​​from the dead dataset.
    #
    #  @return  The data.
    def readDataFile(self):
        return self.readFile("descriptions")

    ## @brief   The method that reads the jam attack prediction.
    #  @details The method that reads the values ​​from the labels.
    #
    #  @return  The label data.
    def readLabelFile(self):
        return self.readFile("predictions")

    ## @brief   The method that returns the length of the dataset.
    #  @details The method that returns the length of the dataset.
    #
    #  @return  The length of the dataset.
    def getDatasetLen(self):
        return len(self.dataset)
 
    ## @brief   The method that formats the context data.
    #  @details The method that returns a formatted version of the context data.
    #
    #  @return  Formatted contextual data.
    def getDataFromDataset(self, index):
        row, node, ls, lc, le, ltx, nb = self.dataset[self.i].split(';')
        return [int(node), int(ls), int(lc), int(le), int(ltx), int(nb)]
    
    ## @brief   The method that formats the label data.
    #  @details The method that returns a formatted version of the labem data.
    #
    #  @return  The formatted label data.
    def getLabelFromDataset(self, index):
        rd, label, bool_info, rd_reverse = self.label[self.i*2].split(';')
        return not bool(int(bool_info))
