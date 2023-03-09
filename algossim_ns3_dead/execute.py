# -*- coding: utf-8 -*-
"""
Created on Wed Jul 31 15:37:44 2019

@author: gutowski
"""
import math
import random
import sys
import os

import pandas as pd

from scipy.stats import variation

import View
from Model import Model
from data.DataMonitor import data_store

import matplotlib.pyplot as plt
import glob

# from View import plot3D

def execute(df_recall, name_dataset, name_algorithm=str(sys.argv[1]), loop=int(sys.argv[2])):
    # seed = 0
    # random.seed(seed)
    # np.random.seed(seed)

    store_data = data_store(name_dataset)

    (dContexts, nbArms, arms, contexts, ratings, nbArms, nbContexts, nbPred, dArms) = store_data
    
    horizon = loop * nbContexts

    m1 = Model(name_algorithm, horizon, arms, contexts, ratings)

    View.displayDataInformations(nbArms, nbContexts, nbPred, dContexts, horizon)
    View.displayAlgorithmInformations(name_algorithm, m1.model)

    nb_instances = len(m1.model.contexts)
    # print(str(nb_instances))
    reward = 0
    acc = []
    rwd = []
    div = []
    trial = range(1, m1.model.horizon + 1)
    expected = []
    predicted = []
    expected_jam = 0
    predicted_jam = 0
    loop_counter = 1

    # for j in range (1,self.horizon+1):
    #    trial.append(int(j))
    
    recall_list = []

    if sys.argv[3] == "dynamic":
        set_dyn = set_dynamic_drawing(horizon, View.nameProcessing(name_algorithm), name_dataset)
        display_crw = set_dyn[0]
        display_div = set_dyn[1]
        display_acc = set_dyn[2]
    for i in range(m1.model.horizon):
        View.displayRound(i)
        data = run(m1, m1.model, nb_instances, reward, acc, i, trial, rwd, store_data, expected, predicted, expected_jam, predicted_jam, div)
        
        expected_jam = data[7]
        predicted_jam = data[8]
        
        if expected_jam > 0 :
            recall = predicted_jam/expected_jam
        else :
            recall = 0
        
        acc = data[1]
        reward = data[3]
        rwd = data[4]
        div = data[5]
        diversity = data[6]
        accuracy = reward / (i + 1)
        
        if i % nb_instances == nb_instances - 1  :
            recall_list.append([loop_counter, recall])
            loop_counter += 1
        if sys.argv[3] == "dynamic":
            dynamic_drawing(display_crw, display_div, display_acc, i, reward, diversity, accuracy)

    df_recall_temp = pd.DataFrame(recall_list, columns=['loop',name_dataset])
    d2 = "2D"
    d3 = "3D"
    null_tab = []
    
    if df_recall.empty :
        df_recall = pd.concat([df_recall, df_recall_temp])
    else :
        df_recall = df_recall.merge(df_recall_temp)
    print(df_recall.head())
    
    #View.showConfusionMatrix(expected, predicted)
    # View accuracy evolution over rounds
    #View.viewGraphic(data[0], trial, acc, null_tab, "Accuracy", "Accuracy evolution over trials", d2)

    # View Cumulative Reward evolution over rounds
    #View.viewGraphic(data[3], trial, rwd, null_tab, "Cumulative reward", "Cumulative reward evolution over trials", d2)

    # View Diversity evolution over rounds
   # View.viewGraphic(data[6], trial, div, null_tab, "Diversity", "Diversity evolution over trials", d2)

    # viewGraphic(str(data[6])+"-"+str(data[0]),acc,div,"Accyracy-Diversity","Diversity evolution over trials")

    # View Accuracy-Diversity evolution over rounds
    #View.viewGraphic(str(data[6]) + "-" + str(data[0]), trial, div, acc, "Diversity-Accuracy","Diversity-Accuracy over trials", d3)
    
    

    # View density of each feature for each arm in LinUCB only (very unreadable if too many features or classes) try
    # it with control and controlsp viewDensity(nbArms,m1.getAlgo(),dContexts,nameDataset,1,0)

    # View densitiy for each features in class 0 in LinUCB only
    # viewDensity(nbArms,m1.getAlgo(),dContexts,nameDataset,0,0)

    # View densitiy for each features in class 1 in LinUCB only
    # viewDensity(nbArms,m1.getAlgo(),dContexts,nameDataset,0,1)
    return df_recall

def run(m, algo, nb_instances, reward, acc, i, trial, rwd, store_data, expected, predicted, expected_jam, predicted_jam, div):
    context = i % nb_instances
    #print("context : ", context)
    cls = algo.choose_action(context)

    nb = []
    #store_data[2].__getitem__(cls) -> arm output (0 : not_jammed 1 : jammed)
    expected.append(store_data[2].__getitem__(cls).feature[1])
    if store_data[2].__getitem__(cls).feature[1] == '1' :
        expected_jam += 1 
        
    store_data[2].__getitem__(cls).count += 1
    # print(str(cls)+" - "+str(storeData[2].__getitem__(cls).getSelected()))
    for j in range(0, store_data[1]):
        nb.append(store_data[2].__getitem__(j).count)

    evaluation = float(m.evaluate(context, cls)) 
    
    if evaluation == 1.0 :
        predicted.append(store_data[2].__getitem__(cls).feature[1])
        if store_data[2].__getitem__(cls).feature[1] == '1' :
            predicted_jam +=1
    else :
        predicted.append(int(not store_data[2].__getitem__(cls).feature[1]))
    #evalutation : 0 -> good prediction 1 -> bad prediction
    algo.update_reward(context, cls, evaluation)
    reward += evaluation
    acc.append(reward / (i + 1))
    rwd.append(reward)

    cv = variation(nb)
    # print(nb)
    diversity = 1 - (cv / math.sqrt(store_data[1]))
    div.append(diversity)

    
    return reward / algo.horizon, acc, trial, reward, rwd, div, diversity, expected_jam, predicted_jam


def set_dynamic_drawing(horizon, na, name_dataset):
    display_crw = View.figure(horizon, na, name_dataset, "Round", "Reward", "Cumulative rewards: ")
    display_div = View.figure(horizon, na, name_dataset, "Round", "Diversity", "Diversity evolution: ")
    # displayDivAcc=figure(horizon,nA,nameDataset,"Accuracy","Diversity","Accuracy and Diversity evolution: ")
    display_acc = View.figure(horizon, na, name_dataset, "Round", "Accuracy", "Accuracy evolution: ")

    return display_crw, display_div, display_acc


def dynamic_drawing(display_crw, display_div, display_acc, i, reward, diversity, accuracy):
    View.dynamicView(display_crw, i, reward)
    View.dynamicView(display_div, i, diversity)
    # dynamicView(displayDivAcc,diversity,accuracy)
    View.dynamicView(display_acc, i, accuracy)


if __name__ == '__main__':
    if len(sys.argv) < 4 or len(sys.argv) >= 5:
        print(str(
            sys.argv) + "3 arguments are needed: name of the dataset (mushrooms, control, or statlog), name of the "
                        "algorithm (linucb or egreedy), number of loop, and static or dynamic graph drawing")
    else:
        print("You have chosen " + str(sys.argv[1]) + " algorithm")
        df_recall = pd.DataFrame()
        for dir in os.listdir('./data/'):
            if not os.path.isfile(f"./data/{dir}") and dir != '__pycache__':
                df_recall = execute(df_recall, name_dataset=dir)
        df_recall.set_index('loop')
        avg_list = []
        df = df_recall[['node1','node2','node3','node4','node5','node6','node7','node8','node9']]
        for index, row in df.iterrows():
            i = 0
            val = 0
            for col in row :
                i +=1
                val += col
            avg_list.append(val/i)
        print(avg_list)
        df_recall['average'] = avg_list
        df_recall.to_csv('result.csv', index=False, sep=';')
       
