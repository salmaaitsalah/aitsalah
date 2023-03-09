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
from multiprocessing import Process
import multiprocessing as mp
import View
from Model import Model
from data.DataMonitor import data_store

import matplotlib.pyplot as plt
import glob

from data.Ns3gymLinker import Ns3gymLinker
from PDFGenerator import PDFGenerator

# from View import plot3D

def execute(name_algorithm, node, q):
    # seed = 0
    # random.seed(seed)
    # np.random.seed(seed)

    store_data = data_store()
    

    nbArms, arms, dArms = store_data

    ns3Linker = Ns3gymLinker(node)
    ns3_data = ns3Linker.getDataFromNS3()
    m1 = Model(name_algorithm, arms, [ns3_data])
    # print(str(nb_instances))
    reward = 0
    acc = []
    rwd = []
    rcl_eval = []
    rcl_label = []
    qos = []
    out_qos = []
    nb_instances = 0
    expected_jam = 0
    expected_jam_eval = 0
    predicted_jam = 0
    
    current_QOS = -1
    previous_QOS = -1
    previous_pred = -1
    
    predicted = []
    expected = []
    
    node_id = []
    ls = []
    lc = []
    le = []
    ltx = []
    nb = []
    label = []

    # for j in range (1,self.horizon+1):
    #    trial.append(int(j))
    
    i = 0
    while(True):
        
        View.displayRound(i)
        
        ns3_data = ns3Linker.getDataFromNS3()
        
        node_id.append(ns3_data.features[0])
        ls.append(ns3_data.features[1])
        lc.append(ns3_data.features[2])
        le.append(ns3_data.features[3])
        ltx.append(ns3_data.features[4])
        nb.append(ns3_data.features[5])
        
        expected_jam_bool = ns3Linker.label[-1]
        
        if expected_jam_bool : 
            expected_jam += 1
        
        label.append(expected_jam_bool)
        
        m1.appendContext(ns3_data)
        
        previous_QOS = current_QOS
        current_QOS = ns3Linker.getQOS() #TODO -> getQOS() : float
        qos.append(current_QOS)
        out_qos.append('{:.3f}'.format(current_QOS))
        
        nb_instances += 1 
        data = run(m1, m1.model, nb_instances, reward, acc, rwd, store_data, expected_jam, predicted_jam, expected_jam_eval, current_QOS, previous_QOS, previous_pred, rcl_eval, rcl_label, predicted, expected)
        
        expected_jam_eval = data[3]
        predicted_jam = data[4]
        previous_pred = data[5]
        acc = data[0]
        reward = data[1]
        rwd = data[2]
        accuracy = reward / (i + 1)
        rcl_label = data[6]
        predicted = data[7]
        expected = data[8]
        rcl_eval = data[9]
            
        i+=1
        if i == 2000 :
            break
        
    # View accuracy evolution over rounds
   


    d2 = "2D"
    d3 = "3D"
    null_tab = []
    trial = range(1,i+1)
    View.saveGraphic(trial, acc, null_tab, f"Accuracy node {node}", f"Accuracy evolution over trials node {node}", d2)
    View.saveGraphic(range(1,len(data[6])+1), rcl_label, null_tab, f"Recall node {node}", f"Recall evolution over trials using label node {node}", d2)
    View.saveGraphic(range(1,len(data[9])+1), rcl_eval, null_tab, f"Recall node {node}", f"Recall evolution over trials using evaluation node {node}", d2)
    View.saveGraphic(range(1,len(qos)+1), qos, null_tab, f"QOS node {node}", f"QOS evolution over trials node {node}", d2)
    View.saveConfusionMatrix(f"Confusion matrix using label node {node}",label, predicted)
    View.saveConfusionMatrix(f"Confusion matrix using evaluation node {node}",expected, predicted)
    
    final_acc_value = '{:.3f}'.format(acc[-1])
    final_rcl_label_value = '{:.3f}'.format(rcl_label[-1])
    final_rcl_eval_value = '{:.3f}'.format(rcl_eval[-1])
    
    dict_node_data = {}
    dict_node_data['nodeId'] = node_id
    dict_node_data['ls'] = ls
    dict_node_data['lc'] = lc
    dict_node_data['le'] = le
    dict_node_data['ltx'] = ltx
    dict_node_data['number of neighbors'] = nb
    dict_node_data['QOS'] = out_qos
    dict_node_data['arm'] = predicted
    dict_node_data['jammed evaluation'] = expected
    dict_node_data['label (jammed or not)'] = label
    
    df = pd.DataFrame(dict_node_data)
    df.to_csv(f'.\data\\node{node}\data.txt')
    # print(df.head())
    
    list_final_value = [node, final_acc_value, final_rcl_label_value, final_rcl_eval_value]
    
    q.put(list_final_value)

def run(m, algo, nb_instances, reward, acc, rwd, store_data, expected_jam, predicted_jam, expected_jam_eval, current_QOS, previous_QOS, previous_pred, rcl_eval, rcl_label, predicted, expected):
    context = nb_instances-1
    #print("context : ", context)
    cls = algo.choose_action(context)

    #store_data[2].__getitem__(cls) -> arm output (0 : not_jammed 1 : jammed)
    current_pred =  store_data[1].__getitem__(cls).feature[1]
    store_data[1].__getitem__(cls).count += 1
    evaluation = False
    QOS_state = False
    
    if previous_QOS != -1 :
        QOS_state = evaluateQOS(previous_QOS, current_QOS, previous_pred)  #TODO -> evaluateQOS(was_Attacked, current_QOS, previous_QOS) : Boolean
        #print("QOS_state", QOS_state)
    
    if QOS_state == True : 
        expected_jam_eval += 1 
        
    # evaluation = float(m.evaluate(context, cls)) 
    if previous_pred != -1 :
        evaluation = True if bool(previous_pred) == QOS_state else False
    
    expected.append(QOS_state)
    predicted.append(True if current_pred == "1" else False)
    
    if current_pred == "1" :
        predicted_jam +=1
    
    
    # print("========================================nb_instances", nb_instances)
    # print("previous_pred", previous_pred)
    # print("current_pred", current_pred)
    # print("reward", reward)
    # print("evaluation", evaluation)
    # print("predicted_jam", predicted_jam)
    # print("expected_jam", expected_jam)
    
    previous_pred = current_pred
    
    
        
    #evalutation : 0 -> good prediction 1 -> bad prediction
    algo.update_reward(context, cls, evaluation)
    
    reward += evaluation
    acc.append(reward / (nb_instances + 1))
    rwd.append(reward)
    if expected_jam > 0 : 
        rcl_label.append(predicted_jam/(expected_jam+predicted_jam))
        
    if expected_jam_eval > 0 :
        rcl_eval.append(predicted_jam/(expected_jam_eval+predicted_jam))
    
    return acc, reward, rwd, expected_jam_eval, predicted_jam, previous_pred, rcl_label, predicted, expected, rcl_eval

def aUpperEqualsBEpsilon(a, b, epsilon = 0.2):
    return float(a) >= (float(b) - epsilon)

def evaluateQOS (qos, qost1, wasAttacked):
    attack = True
    if wasAttacked:
        attack = aUpperEqualsBEpsilon(qos, qost1)
    else:
        attack = not aUpperEqualsBEpsilon(qost1, qos)
        
    return attack

def resetPlotImg():
    files = glob.glob('plot/*')
    for f in files:
        os.remove(f)
        
def generatePDF(dict_acc, dict_rcl, dict_rcl_eval) :
    df_acc = pd.DataFrame(dict_acc, index=[0]).iloc[:, ::-1]
    df_acc[' ']=['Accuracy']
    df_acc=df_acc.iloc[:, ::-1]
  
    df_rcl = pd.DataFrame(dict_rcl, index=[0]).iloc[:, ::-1]
    df_rcl[' ']=['Recall']
    df_rcl=df_rcl.iloc[:, ::-1]
    
    df_rcl_eval = pd.DataFrame(dict_rcl_eval, index=[0]).iloc[:, ::-1]
    df_rcl_eval[' ']=['Recall using evaluation']
    df_rcl_eval=df_rcl_eval.iloc[:, ::-1]
    
    print("generate df")
    list_df_node_info = []
    list_dir = [f for f in glob.glob("./data/*") if "node" in f]
    for d in range(0,nb_node):
        list_df_node_info.append(pd.read_csv(f'{list_dir[d]}/data.txt'))
        
    
    generator = PDFGenerator()
    generator.GeneratePDF(df_acc=df_acc, df_rcl=df_rcl, df_rcl_eval = df_rcl_eval,
                          QOS_formula="ls/lc if lc != 0, else number of neighbors", 
                          epsilon="0.2", algorithm = sys.argv[1], 
                          list_df_node_info = list_df_node_info)
        
if __name__ == '__main__':
    q = mp.Queue()
    resetPlotImg()
    # for i num of sub_folder
    list_process = []
    dict_acc = {}
    dict_rcl = {}
    dict_rcl_eval = {}
    nb_node = 1
    
    if len(sys.argv) == 3:
        nb = int(sys.argv[2])
        if nb > 0 and nb < 10:
            nb_node = nb
            
    print(sys.argv)
    
    for i in range(1, nb_node + 1):
        sub_folder="node{}".format(i)
        p = Process(target=execute, args=[sys.argv[1], i, q])
        p.start()        
        list_process.append(p)
    
    for p in list_process:
        node_id, list_acc, list_rcl, list_rcl_eval = q.get()
        
        dict_acc[f"node {node_id}"] = list_acc
        dict_rcl[f"node {node_id}"] = list_rcl
        dict_rcl_eval[f'node {node_id}'] = list_rcl_eval
        
        p.join()
        
    generatePDF(dict_acc, dict_rcl, dict_rcl_eval)
    
    print("END\n")
