## @file View.py
#  @brief file that regroup all the methods relating to View and Save differents plots
#  @details 
#  @author  Romain Durieux and Nathan Trouillet (2022), using the work of gutowski (2019)

# -*- coding: utf-8 -*-
"""
@author: Romain Durieux and Nathan Trouillet (2022), using the work of gutowski (2019)
"""
import matplotlib as mpl
import matplotlib.pyplot as plt
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay

def plotDensity(i, algo, d, a):
    for f in range(0, d):
        tab = []
        x = f if i == None else i
        for z in range(1, int(algo.count[x]) - 1):
            tab.append(float(algo.features_theta[a][z][f]))
        y = a if i == None else i
        label_line = "Class: " + str(y) + " - Features: " + str(f)
        if tab[len(tab) - 1] != 0.0:
            fig = sns.distplot(
                tab, 
                hist=False, 
                kde=True, 
                kde_kws={'linewidth': 2}, 
                label=label_line
            )
    return fig

def viewDensity(nbArms, algo, d, nameDataset, viewAll, a):
    if viewAll == 1:
        for i in range(0, nbArms):
            fig = plotDensity(i, algo, d, a)

        plt.xlabel("Theta weights")
        plt.ylabel("Density")
        plt.title("Density per features for each class in " + str(nameDataset))
        plt.show(fig)
    else:
        
        fig = plotDensity(i, algo, d, a)
        plt.xlabel("Theta weights")
        plt.ylabel("Density")
        plt.title("Density per features for class " + str(a) + " in " + str(nameDataset))
        plt.show(fig)

## @brief Method that plot and show a 2D graph
# @details 
# @param    xTab    x values
# @param    yTab    y values
# @param    zTab    z values (not used)
# @param    metric  metric of the graph
# @param    graphicTitle    title of the graph
# @param    dim     dimension of the graph (not used)
# @return
def viewGraphic(xTab, yTab, zTab, metric, graphicTitle, dim):
    plt.plot(xTab, yTab)
    plt.xlabel(metric)
    plt.title(graphicTitle)
    plt.show()

    # If you put root.destroy() here, it will cause an error if the window is
    # closed with the window manager.

## @brief Method that plot and save a 2D graph
# @details
# @param    xTab    x values
# @param    yTab    y values
# @param    zTab    z values (not used)
# @param    metric  metric of the graph
# @param    graphicTitle    title of the graph
# @param    dim     dimension of the graph (not used)
# @return
def saveGraphic(xTab, yTab, zTab, metric, graphicTitle, dim):
    plt.clf()
    plt.plot(xTab, yTab)
    plt.xlabel(metric)
    plt.title(graphicTitle)
    plt.savefig(f'./plot/{graphicTitle.replace(" ", "")}')

## @brief method that print the current round at each 100 round
# @details
# @param    i   current round
# @return
def displayRound(i):
    if (i + 1) % 100 == 0 and i > 0:
        print("Round -> " + str(i + 1))

def displayDataInformations(nbArms, nbContexts, nbPred, dContexts, horizon):
    print("Number of arms: " + str(nbArms))
    print("Number of instances: " + str(nbContexts))
    print("Number of ratings: " + str(nbPred))
    print("\nNumber of dimensions: " + str(dContexts))
    print("\nHorizon: " + str(horizon))

def displayAlgorithmInformations(algoName, algo):
    if algoName == "linucb":
        print("\ndelta: " + str(algo.delta))
        print("alpha: " + str(algo.alpha))
    if algoName == "egreedy":
        print("\nepsilon: " + str(algo.epsilon))
        
def dynamicView(display, i, metric):
    display.add(i + 1, metric)
    plt.pause(0.001)

def figure(horizon, nameAlgo, nameData, xl, yl, tl):
    fig, axes = plt.subplots()
    display = RealtimePlot(axes, horizon)
    plt.ylabel(yl)
    plt.xlabel(xl)
    plt.title(tl + str(nameAlgo) + " - " + str(nameData) + " dataset.")

    return display

def plot3D(x, y, z, la):
    mpl.rcParams['legend.fontsize'] = 10

    fig = plt.figure()
    ax = fig.gca(projection='3d')

    ax.plot(x, y, z, label=la)
    ax.legend()

    plt.show()
    
## @brief   method that create the confusion matrix
# @details
# @param    title   title of the plot
# @param    expected    list containing the expected binary value of the confusion matrix 
# @param    predicted   list containing the predicted binary value of the confusion matrix
# @return   plt the generated plot
def createConfusionMatrix(title, expected, predicted):
    confusion_m = confusion_matrix(expected, predicted)
    disp = ConfusionMatrixDisplay(confusion_matrix=confusion_m, display_labels=["Not jammed", "Jammed"])
    disp.plot()
    plt.title(title)
    return plt

## @brief   method that show the confusion matrix
# @details
# @param    title   title of the plot
# @param    expected    list containing the expected binary value of the confusion matrix 
# @param    predicted   list containing the predicted binary value of the confusion matrix
# @return
def showConfusionMatrix(title, expected, predicted):
    plot = createConfusionMatrix(title, expected, predicted)
    plot.show()

## @brief   method that save the confusion matrix
# @details
# @param    title   title of the plot
# @param    expected    list containing the expected binary value of the confusion matrix 
# @param    predicted   list containing the predicted binary value of the confusion matrix
# @return
def saveConfusionMatrix(title, expected, predicted):
    plot = createConfusionMatrix(title, expected, predicted)
    plot.savefig(f"./plot/{title.replace(' ','')}")

def nameProcessing(nameAlgorithm):
    algorithm = nameAlgorithm
    if algorithm == "random":
        return nameAlgorithm[0].upper() + nameAlgorithm[1:len(nameAlgorithm)]
    if algorithm == "linucb":
        return nameAlgorithm[0].upper() + nameAlgorithm[1:3] + nameAlgorithm[3:len(nameAlgorithm)].upper()
    if algorithm == "egreedy":
        return "epsilon-" + nameAlgorithm[1].upper() + nameAlgorithm[2:3] + nameAlgorithm[3:len(nameAlgorithm)]
    if algorithm == "ucb1":
        return nameAlgorithm[0:len(nameAlgorithm)].upper()
    if algorithm == "ts":
        return nameAlgorithm[0:len(nameAlgorithm)].upper()
    if algorithm == "lints":
        return nameAlgorithm[0].upper() + nameAlgorithm[1:3] + nameAlgorithm[3:len(nameAlgorithm)].upper()
    if algorithm == "exp3":
        return nameAlgorithm[0:len(nameAlgorithm)].upper()
