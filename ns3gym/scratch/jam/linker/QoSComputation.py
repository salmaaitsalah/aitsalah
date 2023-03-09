## @file    QoSComputation.py
#  @brief   File containing the Computer class.
#  @details File containing all QoS calculation methods.
#  @author  Romain Durieux and Nathan Trouillet (2022)


## @brief   Computer Class. 
#  @details This class is used to calculate a QoS value based on the provided data.
class Computer:
    ## @brief   Computer constructor.
    #  @details This constructor needs 6 parameters.
    #
    #  @param   mode        Computation mode to use (cf. QoSComputation.py).
    #  @param   data        The current contxt data.
    #  @param   qosHisto    The QoS historic.
    #  @param   cWindow     The calculation window (eg. : for an average sum(data)/C).
    #  @param   lDelay      The delay between the first and the second value computed. The second value will be computed at t-L.
    #  @param   i           The iteration number.
    def __init__(self, mode, data, qosHisto, cWindow, lDelay, i):
        self.mode = mode
        self.data = data
        self.qosHistory = qosHisto
        self.cWindow = cWindow
        self.lDelay = lDelay
        self.i = i

    ## @brief   The method that selects the QoS calculation.
    #  @details This method selects the QoS calculation based on the mode parameter.
    #
    #  @return  The QoS value.
    def getQOS(self, mode="QOS"):
        if mode == "QOS" :
            return self.computeQOS()
        elif mode == "QOSNormalisationSub" :
            return self.computeQOSNormalisationSub()
        elif mode == "QOSNormalisationDiv" :
            return self.computeQOSNormalisationDiv()
        elif mode == "QOSAvg" :
            return self.computeQOSAvg()
        elif mode == "QOSExtremumAvg" :
            return self.computeQOSExtremumAvg()
        elif mode == "QOSMedian" :
            return self.computeQOSMedian()
        elif mode == "QOSAvgMedianSub" :
            return self.computeQOSAvgMedianSub()
        elif mode == "QOSAvgMedianDiv" :
            return self.computeQOSAvgMedianDiv()
        elif mode == "QOSAvgExtremumSub" :
            return self.computeQOSAvgExtremumSub()
        elif mode == "QOSAvgExtremumDiv" :
            return self.computeQOSAvgExtremumDiv()
        else :
            print("Error, unknown mode")
            return -1

    ## @brief   The QoS computation.
    #  @details This methode is the simple QoS computation.
    #
    #  @return  The QoS value.
    def computeQOS(self):
            return (self.data.features[1]) / self.data.features[2] if self.data.features[2] != 0 else self.data.features[5]
        
    ## @brief   QoS normalization with subtraction calculation.
    #  @details This method subtracts two QoS. These QoS represent an average of cWindows data and an average of cWindows data at t-lDelay.
    #
    #  @return  The QoS value.
    def computeQOSNormalisationSub(self):
        res = self.getQOS()
        res1 = self.getQOS()
        if self.i >= self.cWindow + self.lDelay:
            res = sum(self.qosHistory[self.i-self.cWindow:self.i]) / self.cWindow
            res1 = sum(self.qosHistory[self.i-self.cWindow-self.lDelay:self.i-self.lDelay]) / self.cWindow
        return res - res1

    ## @brief   QoS normalization with division calculation.
    #  @details This method divides two QoS. These QoS represent an average of cWindows data and an average of cWindows data at t-lDelay.
    #
    #  @return  The QoS value.
    def computeQOSNormalisationDiv(self):
        res = self.getQOS()
        res1 = self.getQOS()
        if self.i >= self.cWindow + self.lDelay:
            res = sum(self.qosHistory[self.i-self.cWindow:self.i]) / self.cWindow
            res1 = sum(self.qosHistory[self.i-self.cWindow-self.lDelay:self.i-self.lDelay]) / self.cWindow
        if res1 > 0 :
            return res / res1
        else :
            return 0
 
    ## @brief   The QoS Average computation.
    #  @details This method is the average of the latest cWindows data.
    #
    #  @return  The QoS value.
    def computeQOSAvg(self):
        res = self.getQOS()
        if self.i >= self.cWindow:
            res = sum(self.qosHistory[self.i-self.cWindow:self.i]) / self.cWindow
        return res

    ## @brief   The QoS Extremum Average computation.
    #  @details This method is the average of the minimum and maximum of the latest cWindows data.
    #
    #  @return  The QoS value.
    def computeQOSExtremumAvg(self):
        res = self.getQOS()
        if self.i >= self.cWindow:
            histoList = self.qosHistory[self.i-self.cWindow:self.i]
            histoList.sort()
            res = histoList[0] + histoList[self.cWindow - 1] / 2
        return res

    ## @brief   The QoS Median computation.
    #  @details This method is the median/mean of the latest cWindows data.
    #
    #  @return  The QoS value.
    def computeQOSMedian(self):
        res = self.getQOS()
        if self.i >= self.cWindow:
            histoList = self.qosHistory[self.i-self.cWindow:self.i]
            histoList.sort()
            median = None
            if(self.cWindow % 2 == 0):
                median = ( histoList[int(self.cWindow/2)] + histoList[int((self.cWindow/2)-1)] ) / 2
            else:
                median = histoList[int((self.cWindow-1)/2)]
            res = median
        return res

    ## @brief   The QoS Average Median Substraction.
    #  @details This method subtracts two QoS. The QoS mean and the QoS median at t-lDelay.
    #
    #  @return  The QoS value.
    def computeQOSAvgMedianSub(self):
        res = self.getQOS()
        if self.i >= self.cWindow:
            histoList = self.qosHistory[self.i-self.cWindow:self.i]
            histoList.sort()
            avg = sum(histoList) / self.cWindow
            median = None
            if(self.cWindow % 2 == 0):
                median = ( histoList[int(self.cWindow/2)] + histoList[int((self.cWindow/2)-1)] ) / 2
            else:
                median = histoList[int((self.cWindow-1)/2)]
            res = avg - median
        return res

    ## @brief   The QoS Average Median Division.
    #  @details This method divides two QoS. The QoS mean and the QoS median at t-lDelay.
    #
    #  @return  The QoS value.
    def computeQOSAvgMedianDiv(self):
        res = self.getQOS()
        if self.i >= self.cWindow:
            histoList = self.qosHistory[self.i-self.cWindow:self.i]
            histoList.sort()
            avg = sum(histoList) / self.cWindow
            median = None
            if(self.cWindow % 2 == 0):
                median = ( histoList[int(self.cWindow/2)] + histoList[int((self.cWindow/2)-1)] ) / 2
            else:
                median = histoList[int((self.cWindow-1)/2)]
            if median > 0 :
                res = avg / median
            else :
                res = 0
        return res 

    ## @brief   The QoS Average Extremum Substraction.
    #  @details This method subtracts two QoS. The average QoS and the extreme average QoS at t-lDelay.
    #
    #  @return  The QoS value.
    def computeQOSAvgExtremumSub(self):
        res = self.getQOS()
        if self.i >= self.cWindow:
            histoList = self.qosHistory[self.i-self.cWindow:self.i]
            histoList.sort()
            avg = sum(histoList) / self.cWindow
            median = histoList[0] + histoList[int(self.cWindow - 1)] / 2
            res = avg - median
        return res

    ## @brief   The QoS Average Extremum Disision.
    #  @details This method divides two QoS. The average QoS and the extreme average QoS at t-lDelay.
    #
    #  @return  The QoS value.
    def computeQOSAvgExtremumDiv(self):
        res = self.getQOS()
        if self.i >= self.cWindow:
            histoList = self.qosHistory[self.i-self.cWindow:self.i]
            histoList.sort()
            avg = sum(histoList) / self.cWindow
            median = histoList[0] + histoList[self.cWindow - 1] / 2
            res = avg / median
        return res 