import random
from data.Dataset import Context
from functools import reduce
class Ns3gymLinker:

    def __init__(self, nodeId):
        self.data = []
        self.histo = []
        self.qosHistory = []
        self.qosNormHistory = []
        self.qosAvgHistory = []
        self.label = []
        self.i = 0
        self.id = nodeId
        self.port = 5555 + self.id
        self.curr = 0
        self.loadFile()
        self.offset = 1
        self.C = 20
        self.L = 50

    def next(self):
        if self.data != []:
            self.histo.append(self.data)
        # Mise à jour -> self.data
        
        #features = [1, random.randrange(0, 11, 1), random.randrange(0, 11, 1), random.randrange(0, 2, 1), 0, 8] #[['nodeid ',' ls ', ' lc ', ' le ', ' ltx ',' number of neighbors ']]
        features = self.fileLinesDesc[self.curr].split('\n')[0].split(';')[1:]
        self.label.append(True if self.fileLinesPred[self.curr+self.offset].split('\n')[0].split(';')[2] == '1' else False)
        self.offset += 1
        features = [float(i) for i in features]
        #print('features : ', features)
        self.curr += 1
        self.curr %= 1500
        self.i += 1
        self.data = Context(self.i, features)
        self.qosHistory.append(self.getQOS())
        self.qosNormHistory.append(self.computeQOSNormalisation())
        self.qosAvgHistory.append(self.computeQOSAvg())

    def loadFile(self):
        path_data = f"./data/node{self.id}/descriptions.txt"
        file_data = open(path_data)
        self.fileLinesDesc = file_data.readlines()
        
        path_pred = f"./data/node{self.id}/predictions.txt"
        file_pred = open(path_pred)
        self.fileLinesPred = file_pred.readlines()
        
    def getDataFromNS3(self):
        self.next()
        return self.data
    
    def getQOS(self):
        return self.data.features[1] / self.data.features[2] if self.data.features[2] != 0 else self.data.features[5]

    def getHisto(self):
        return self.histo

    def computeQOSNormalisationSub(self):
        res = none
        res1 = none
        if self.i >= self.C + self.L:
            res = reduce(lambda a, b: a + b, self.list[self.i-self.L:self.i]) / self.L
            res1 = reduce(lambda a, b: a + b, self.list[self.i-self.C-self.L:self.i-self.C]) / self.L
        return res - res1

    def computeQOSNormalisationDiv(self):
        res = none
        res1 = none
        if self.i >= self.C + self.L:
            res = reduce(lambda a, b: a + b, self.list[self.i-self.L:self.i]) / self.L
            res1 = reduce(lambda a, b: a + b, self.list[self.i-self.C-self.L:self.i-self.C]) / self.L
        return res / res1

    def computeQOSAvg(self):
        res = none
        if self.i >= self.C:
            res = reduce(lambda a, b: a + b, self.list[self.i-self.C:self.i]) / self.C
        return res

    def computeQOSExtremumAvg(self):
        res = none
        if self.i >= self.C:
            histoListSorted = self.list[self.i-self.C:self.i].sort()
            res = histoList[0] + histoList[self.C - 1] / 2
        return res

    def computeQOSMedian(self):
        res = none
        if self.i >= self.C:
            histoListSorted = self.list[self.i-self.C:self.i].sort()
            res = histoList[0] + histoList[self.C - 1] / 2
        return res

    def computeQOSStandingFluctuationSub(self):
        res = none
        if self.i >= self.C:
            histoList = self.list[self.i-self.C:self.i]
            histoListSorted = self.list[self.i-self.C:self.i].sort()
            avg = reduce(lambda a, b: a + b, histoList) / self.C
            median = histoList[0] + histoList[self.C - 1] / 2
            res = avg - median
        return res

    def computeQOSStandingFluctuationDiv(self):
        res = none
        if self.i >= self.C:
            histoList = self.list[self.i-self.C:self.i]
            histoListSorted = self.list[self.i-self.C:self.i].sort()
            avg = reduce(lambda a, b: a + b, histoList) / self.C
            median = histoList[0] + histoList[self.C - 1] / 2
            res = avg / median
        return res 