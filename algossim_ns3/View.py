# -*- coding: utf-8 -*-
"""
Created on Thu Aug  8 22:09:11 2019

@author: gutowski
"""
import matplotlib as mpl
import matplotlib.pyplot as plt
import seaborn as sns
# Implement the default Matplotlib key bindings.
from matplotlib.backend_bases import key_press_handler
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk)
from matplotlib.figure import Figure

from lib.realtimeplot import RealtimePlot


def viewDensity(nbArms, algo, d, nameDataset, viewAll, a):
    if viewAll == 1:
        # print("toto")
        for i in range(0, nbArms):
            # print("i: "+str(i))
            for f in range(0, d):

                tab = []
                for z in range(1, int(algo.count[i]) - 1):
                    tab.append(float(algo.features_theta[a][z][f]))
                label_line = "Class: " + str(i) + " - Features: " + str(f)
                if tab[len(tab) - 1] != 0.0:
                    fig = sns.distplot(tab, hist=False, kde=True, kde_kws={'linewidth': 2}, label=label_line)

        # select=range (0,len(tab))

        # viewGraphic(0,select,tab,[],"weight","feature convergence","2D")
        plt.xlabel("Theta weights")
        plt.ylabel("Density")
        plt.title("Density per features for each class in " + str(nameDataset))
        plt.show(fig)
        # print(tab)

    else:

        for f in range(0, d):

            tab = []
            for z in range(1, int(algo.count[f]) - 1):
                tab.append(float(algo.features_theta[a][z][f]))
            label_line = "Class: " + str(a) + " - Features: " + str(f)
            if tab[len(tab) - 1] != 0.0:
                fig = sns.distplot(tab, hist=False, kde=True, kde_kws={'linewidth': 2}, label=label_line)
        plt.xlabel("Theta weights")
        plt.ylabel("Density")
        plt.title("Density per features for class " + str(a) + " in " + str(nameDataset))
        plt.show(fig)
        # print(tab)


def viewGraphic(measure, xTab, yTab, zTab, metric, graphicTitle, dim):
    #print("\n" + str(metric) + ": " + str(measure))
    plt.plot(xTab, yTab)
    plt.xlabel(metric)
    plt.title(graphicTitle)
    plt.show()
    
    
    # If you put root.destroy() here, it will cause an error if the window is
    # closed with the window manager.
def saveGraphic(xTab, yTab, zTab, metric, graphicTitle, dim):
    #print("\n" + str(metric) + ": " + str(measure))
    plt.clf()
    plt.plot(xTab, yTab)
    plt.xlabel(metric)
    plt.title(graphicTitle)
    plt.savefig(f'./plot/{graphicTitle.replace(" ", "")}')

def displayRound(i):
    if (i + 1) % 1000 == 0 and i > 0:
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


def showConfusionMatrix(title,expected, predicted):
    confusion_m = confusion_matrix(expected, predicted)
    disp = ConfusionMatrixDisplay(confusion_matrix=confusion_m, display_labels=["Not jammed", "Jammed"])
    disp.plot()
    plt.title(title)
    plt.show()
    
def saveConfusionMatrix(title,expected, predicted):
    confusion_m = confusion_matrix(expected, predicted)
    disp = ConfusionMatrixDisplay(confusion_matrix=confusion_m, display_labels=["Not jammed", "Jammed"])
    disp.plot()
    plt.title(title)
    plt.savefig(f"./plot/{title.replace(' ','')}")
    

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
