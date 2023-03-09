## @file    execute.py
#  @brief   Algorithm of the simulation
#  @details This file run the training algorithm for one node only. It's composed in two part : 
#           the execute part is used to retrieve data from the linker and launch the run part until the end of the simulation. 
#           Then, it saves all the needed plot and organizes all the needed data for the PDF Generation
#  @author Romain Durieux and Nathan Trouillet (2022), using the work of gutowski (2019)

import math
import random
import sys
import os
import csv
import time

import pandas as pd

import util.View
from Model import Model
from datetime import datetime

import matplotlib.pyplot as plt
import glob

from linker.Ns3gymLinker import Ns3gymLinker
from linker.DatasetLinker import DatasetLinker
from util.PDFGenerator import PDFGenerator, generatePDF

## @brief Initialization of the execute method.
# @details
# @param    int node                the node id
# @param    Namespace args          the argsParser object from the main
# @param    boolean live            the parameter that define if the pretrain phase is activated or not, True by default
# @param    Model m1                the model used for the execute method, None by default
# @return   linker                  Linker object (DatasetLinker of Ns3GymLinker depending on the live parameter)
# @return   store_data              Arms info
# @return   m1                      the model used for the execute method, (untrained if live == False, trained but cleared from all the old context if live == True and untrained if live == True but pretrain_mode == False)
# @return   dict_conf_matrix        Dictionnary for all the values relative to the Confusion Matrix
# @return   dict_graph_list         Dictionnary for all the values used to generate all the graphs
# @return   dict_process_value      Dictionnary for all the values used to process one round of the training in the run method

def init_execute(node, args, live = True, m1 = None):

    linker = None
    
    if live : 
        linker = Ns3gymLinker(node, C = args.C, L = args.L, mode = args.mode)
        ns3gym_data = linker.getData()
        nb_arms, arms, d_arms = linker.getArmsInfo()
        if m1 != None :
            m1.resetContext()
        else :
            m1 = Model(args.name_algo, arms, [ns3gym_data])

    else :
        linker = DatasetLinker(node, C = args.C, L = args.L, mode = args.mode)
        dataset_data = linker.getData()
        nb_arms, arms, d_arms = linker.getArmsInfo()
        if m1 == None :
            m1 = Model(args.name_algo, arms, [dataset_data])
    
    store_data = linker.getArmsInfo()
    
    dict_conf_matrix = {
        'TP':0,
        'TP_eval':0,
        'P':0,
        'TN':0,
        'TN_eval':0,
        'N':0
    }
    
    dict_graph_list = {
        'predicted' :[],
        'expected' : [],
        'node_id' : [],
        'ls' : [],
        'lc' : [],
        'le' : [],
        'ltx' : [],
        'nb' : [],
        'label' : [],
        'acc' : [],
        'rwd' : [],
        'rcl_eval' : [],
        'rcl_label' : [],
        'qos' : [],
        'out_qos' : []
        # 'new_context_value' : []
    }
    
    dict_process_value={
        'current_QOS':-1,
        'previous_QOS':-1,
        'previous_pred':-1,
        'reward':0,
        'nb_instances':0,
        'previous_cls':None,
        'previous_context':0,
        'epsilon':args.epsilon
    }

    return linker, store_data, m1, dict_conf_matrix, dict_graph_list, dict_process_value

## @brief Method which run the training algorithm.
# @details
# @param    int node: the node id
# @param    Namespace args: the argsParser object from the main
# @param    boolean live : the parameter that define if the pretrain phase is activated or not, True by default
# @param    Queue q : queue used to return object to the parent process
# @param    Model m : the model used for the execute method, None by default 
# 
def execute(node, args, q, live = True, m = None):
    

    #INIT EXECUTE
    linker, store_data, m1, dict_conf_matrix, dict_graph_list, dict_process_value = init_execute(node, args, live, m)

    #RUN LOOP
    i = 0
    while(True):
        util.View.displayRound(i)
        
        #DATA RETRIEVE FROM THE LINKER
        data = linker.getData()
        dict_graph_list['node_id'].append(data.features[0])
        dict_graph_list['ls'].append(data.features[1])
        dict_graph_list['lc'].append(data.features[2])
        dict_graph_list['le'].append(data.features[3])
        dict_graph_list['ltx'].append(data.features[4])
        dict_graph_list['nb'].append(data.features[5])
        
        # dict_graph_list['new_context_value'].append(data.features[6])
        
        TP_bool = linker.label[-1]
        dict_graph_list['label'].append(TP_bool)

        m1.appendContext(data)

        dict_process_value['previous_QOS'] = dict_process_value['current_QOS']
        dict_process_value['current_QOS'] = linker.getQOS()
        
        dict_graph_list['qos'].append(dict_process_value['current_QOS'])
        dict_graph_list['out_qos'].append('{:.3f}'.format(dict_process_value['current_QOS'])) #String value of the QOS for output in the PDF file

        dict_process_value['nb_instances'] += 1
        
        #LAUNCH THE RUN
        data = run(m1, m1.model, store_data, dict_process_value, dict_graph_list, dict_conf_matrix,TP_bool,live, linker) #TODO (nathan): REFACTORING INTO A DATA STRUCT -> TOO MUCH PARAMETERS I DONT LIKE IT
        
        #DATA RETRIEVE FROM THE RUN
        dict_process_value = data[0]
        dict_graph_list = data[1]
        dict_conf_matrix = data[2]

        dict_process_value['accuracy'] = dict_process_value['reward'] / (i + 1)
        i += 1

        if live : 
            if linker.isDone():
                print("close link")
                linker.getEnv().close()
                break
        elif linker.i == linker.getDatasetLen()-1 :
            break
            
    if live :
        #GENERATING THE IMAGES FOR THE PDF
        save_images(dict_graph_list, node)
        
        v_acc, v_rcl_label, v_rcl_eval = retrieve_training_values(dict_graph_list)
        
        final_acc = '{:.3f}'.format(v_acc)
        final_rcl_label = '{:.3f}'.format(v_rcl_label)
        final_rcl_eval = '{:.3f}'.format(v_rcl_eval)
        
        v_specificity, v_precision, v_performance = compute_performance_values(dict_conf_matrix, dict_graph_list)

        specificity = '{:.3f}'.format(v_specificity)
        precision = '{:.3f}'.format(v_precision)
        performance = '{:.3f}'.format(v_performance)
        
    
        save_node_data(dict_graph_list, node)
        
        list_final_value = [node, final_acc,
                            final_rcl_label, final_rcl_eval,
                            specificity, precision, performance]
        
        #SEND DATA TO THE PARENT PROCESS
        q.put(list_final_value)
        print(f"node {node} data sent")
    else :
        v_specificity, v_precision, v_performance = compute_performance_values(dict_conf_matrix, dict_graph_list)
        #SEND DATA TO THE PARENT PROCESS
        q.put([node,m1,v_performance])
        print(f"node {node} model sent")
    
    return

## @brief Method which save the dict_graph_list dictionnary in a csv format.
# @details Method which save the dict_graph_list dictionnary in a csv format. This method need to rename all the columns to match the existing data format
# @param    int node: the node id
# @param    dict dict_graph_list: Dictionnary for all the values used to generate all the graphs
def save_node_data(dict_graph_list, node):
    
    dict_node_data = {}
    dict_node_data['nodeId'] = dict_graph_list['node_id']
    dict_node_data['ls'] = dict_graph_list['ls']
    dict_node_data['lc'] = dict_graph_list['lc']
    dict_node_data['le'] = dict_graph_list['le']
    dict_node_data['ltx'] = dict_graph_list['ltx']
    dict_node_data['number of neighbors'] = dict_graph_list['nb']
    
    #dict_node_data['new_context_value'] = dict_graph_list['new_context_value']
    
    dict_node_data['QOS'] = dict_graph_list['out_qos']
    dict_node_data['arm'] = dict_graph_list['predicted']
    dict_node_data['jammed evaluation'] = dict_graph_list['expected']
    dict_node_data['label (jammed or not)'] = dict_graph_list['label']

    df = pd.DataFrame(dict_node_data)
    df.to_csv(f'./data/node{node}/data.txt')
    
## @brief Method which compute the performance values using the data from the dictionnaries dict_conf_matrix and dict_graph_list
# @details
# @param    dict dict_conf_matrix: Dictionnary for all the values relative to the Confusion Matrix
# @param    dict dict_graph_list: Dictionnary for all the values used to generate all the graphs
# @return   v_specificity       specificity value : TN/(TN+FP)
# @return   v_precision     precision value : TP/(TP+FP)
# @return   v_performance       performance value : (v_specificity + v_precision + last recall value)/3

def compute_performance_values(dict_conf_matrix, dict_graph_list):
    
    FP = dict_conf_matrix['P'] - dict_conf_matrix['TP']
    v_specificity = dict_conf_matrix['TN']/(dict_conf_matrix['TN']+FP)
    v_precision = dict_conf_matrix['TP']/(dict_conf_matrix['TP']+FP)
    v_performance = (v_specificity + v_precision + dict_graph_list['rcl_label'][-1])/3
    
    return v_specificity, v_precision, v_performance

## @brief Method which retrieve the final accuracy, recall using the label and recall using the evaluation value
# @details
# @param    dict dict_graph_list: Dictionnary for all the values used to generate all the graphs
# @return   v_acc       last accuracy value
# @return   v_rcl_label     last recall using the label value
# @return   v_rcl_eval      last recall using the evaluation value
def retrieve_training_values(dict_graph_list):
   
    v_acc = dict_graph_list['acc'][-1]
    v_rcl_label = dict_graph_list['rcl_label'][-1]
    v_rcl_eval = dict_graph_list['rcl_eval'][-1]
    
    return v_acc, v_rcl_label, v_rcl_eval

## @brief Method which save all the needed graph for the PDF Report
# @details
# @param    dict dict_graph_list: Dictionnary for all the values used to generate all the graphs
# @param    int node: node id
def save_images(dict_graph_list, node):
    
    d2 = "2D"
    null_tab = []
    util.View.saveGraphic(range(1, len(dict_graph_list['acc'])+1), dict_graph_list['acc'], null_tab,
                    f"Accuracy node {node}", f"Accuracy evolution over trials node {node}", d2)
    util.View.saveGraphic(range(1, len(dict_graph_list['rcl_label'])+1), dict_graph_list['rcl_label'], null_tab,
                    f"Recall node {node}", f"Recall evolution over trials using label node {node}", d2)
    util.View.saveGraphic(range(1, len(dict_graph_list['rcl_eval'])+1), dict_graph_list['rcl_eval'], null_tab,
                    f"Recall node {node}", f"Recall evolution over trials using evaluation node {node}", d2)
    util.View.saveGraphic(range(1, len(dict_graph_list['qos'])+1), dict_graph_list['qos'], null_tab,
                    f"QOS node {node}", f"QOS evolution over trials node {node}", d2)
    util.View.saveConfusionMatrix(
        f"Confusion matrix using label node {node}", dict_graph_list['label'], dict_graph_list['predicted'])
    util.View.saveConfusionMatrix(
        f"Confusion matrix using evaluation node {node}", dict_graph_list['expected'], dict_graph_list['predicted'])

## @brief Method which run one round of the training algorithm.
# @details
# @param    Model m: the model used
# @param    Algorithm algo: the algorithm used
# @param    list store_data: data relative to the arms (nb_arms, arms and d_arms)
# @param    dict_conf_matrix: Dictionnary for all the values relative to the Confusion Matrix
# @param    dict_graph_list: Dictionnary for all the values used to generate all the graphs
# @param    dict_process_value: Dictionnary for all the values used to process one round of the training in the run method
# @param    boolean TP_bool: label of the current context (attacked or not)
# @param    boolean live: the parameter that define if the pretrain phase is activated or not
# @param    Linker linker: Linker object (DatasetLinker or Ns3GymLinker depending on the live parameter)
# @return   dict_conf_matrix      Dictionnary for all the values relative to the Confusion Matrix
# @return   dict_graph_list       Dictionnary for all the values used to generate all the graphs
# @return   dict_process_value        Dictionnary for all the values used to process one round of the training in the run method
def run(m, algo, store_data, dict_process_value, dict_graph_list, dict_conf_matrix, TP_bool,live, linker):
   
    #RETRIEVE THE CONTEXT INDEX
    context = dict_process_value['nb_instances']-1
    
    #RETRIEVE THE ARM USING THE CONTEXT INDEX
    cls = algo.choose_action(context)

    current_pred = store_data[1].__getitem__(cls).feature[1]
    store_data[1].__getitem__(cls).count += 1
    evaluation = False
    QOS_state = False

    #EVALUATE THE QOS STATE (Attacked or not)
    if dict_process_value['previous_QOS'] != -1:
        QOS_state = linker.getEvaluation(dict_process_value['previous_QOS'], dict_process_value['current_QOS'], dict_process_value['epsilon'], dict_process_value['previous_pred'])

    #EVALUATE THE PREVIOUS PREDICTION USING THE CURRENT QOS STATE
    if dict_process_value['previous_pred'] != -1:
        evaluation = float(bool(dict_process_value['previous_pred']) == QOS_state)

    dict_graph_list['expected'].append(QOS_state)
    dict_graph_list['predicted'].append(current_pred == "1")

    #UPDATE THE CONFUSION MATRIX
    if current_pred == "1":
        dict_conf_matrix['P'] += 1
        if TP_bool :
            dict_conf_matrix['TP'] += 1
        if QOS_state :
            dict_conf_matrix['TP_eval'] += 1
    else :
        dict_conf_matrix['N'] += 1
        if not TP_bool :
            dict_conf_matrix['TN'] += 1
        if not QOS_state :
            dict_conf_matrix['TN_eval'] += 1

    dict_process_value['previous_pred'] = current_pred

    #UPDATE THE ALGORITHM REWARD
    if live :
        if dict_process_value['previous_cls'] != None :
            algo.update_reward(dict_process_value['previous_context'], dict_process_value['previous_cls'], evaluation)
    else :
        algo.update_reward(context, cls, TP_bool)
        
    
    dict_process_value['previous_cls'] = cls
    dict_process_value['previous_context'] = context
    
    dict_process_value['reward'] += evaluation
    dict_graph_list['acc'].append(dict_process_value['reward'] / (dict_process_value['nb_instances'] + 1))
    dict_graph_list['rwd'].append(dict_process_value['reward'])
    
    FN = dict_conf_matrix['N'] - dict_conf_matrix['TN']
    FN_eval = dict_conf_matrix['N'] - dict_conf_matrix['TN_eval']

    if (dict_conf_matrix['TP']+FN) > 0 :
        dict_graph_list['rcl_label'].append(dict_conf_matrix['TP']/(dict_conf_matrix['TP']+FN))
    if (dict_conf_matrix['TP_eval']+FN_eval) > 0 :
        dict_graph_list['rcl_eval'].append(dict_conf_matrix['TP_eval']/(dict_conf_matrix['TP_eval']+FN_eval))

    return dict_process_value, dict_graph_list, dict_conf_matrix

## @brief Method which remove all the existing images in the plot directory
# @details
def resetPlotImg():

    files = glob.glob('plot/*')
    for f in files:
        os.remove(f)

## @brief Method which update the best.csv file depending of the global performance. 
# @details Method which update the best.csv file depending of the global performance. If the global performance is higher than the smallest value in the best.csv file, 
# the smallest value and its corresponding report path is replaced by the current global performance value and its corresponding report path.
# @param    PDFGeneratorVar generator_var : Object containing all the needed variable for the PDF Generation
# @param    dict dict_value : Dictionnary of the values relatives to the resumed performance of each nodes
# @param    float global_performance : Global performance value
# @param    string name : name of the report
def findGlobalBest(generator_var, dict_value, global_performance, name):
    try :
            df_best = pd.read_csv('best_report/best.csv')
            if len(df_best.index) < 10 :
                dict_perf = {'Name of report' : name, 'Performance' : global_performance}#TODO : refactor in a method
                new_df = pd.concat([df_best,pd.DataFrame(dict_perf, index=[0])], ignore_index = True)#
                # print(new_df.head())#
                new_df.to_csv('best_report/best.csv', index = False)#
                generatePDF(generator_var, dict_value, global_performance, name)#
            else :
                min_perf = 100
                min_report = ""
                for index, row in df_best.iterrows():
                    if float(row['Performance']) <= min_perf :
                        min_perf = float(row['Performance'])
                        min_report = row['Name of report']
                   
                if global_performance >= min_perf :
                    df_best.drop(df_best.index[df_best['Name of report'] == min_report], inplace=True)
                    dict_perf = {'Name of report' : name, 'Performance' : global_performance}
                    new_df = pd.concat([df_best,pd.DataFrame(dict_perf, index=[0])], ignore_index = True)
                    # print(new_df.head())
                    new_df.to_csv('best_report/best.csv', index = False)
                    generatePDF(generator_var, dict_value, global_performance, name)
                
            
                    
    except FileNotFoundError:
        dict_perf = {'Name of report' : name, 'Performance' : global_performance}
        df_best = pd.DataFrame(dict_perf, index=[0])
        df_best.to_csv('best_report/best.csv', index = False)
        generatePDF(generator_var, dict_value, global_performance, name)
            
## @brief Method which update the best_{mode}.csv file depending of the global performance. 
# @details Method which update the best_{mode}.csv file depending of the global performance. If the global performance is higher than the smallest value in the best_{mode}.csv file, 
# the smallest value and its corresponding report path is replaced by the current global performance value and its corresponding report path.
# @param    PDFGeneratorVar generator_var : Object containing all the needed variable for the PDF Generation
# @param    dict dict_value : Dictionnary of the values relatives to the resumed performance of each nodes
# @param    float global_performance : Global performance value
# @param    string mode : selected QOSComputation mode
# @param    string name : name of the report
def findModeBest(generator_var, dict_value, global_performance, mode, name):
    try :
        df_best = pd.read_csv(f'best_report/best_{mode}.csv')
        if len(df_best.index) < 10 :
            dict_perf = {'Name of report' : name, 'Performance' : global_performance}#TODO : refactor in a method
            new_df = pd.concat([df_best,pd.DataFrame(dict_perf, index=[0])], ignore_index = True)#
            # print(new_df.head())#
            new_df.to_csv(f'best_report/best_{mode}.csv', index = False)#
            generatePDF(generator_var, dict_value, global_performance, name)#
        else :
            min_perf = 100
            min_report = ""
            for index, row in df_best.iterrows():
                if float(row['Performance']) <= min_perf :
                    min_perf = float(row['Performance'])
                    min_report = row['Name of report']
            
            if global_performance >= min_perf :
                df_best.drop(df_best.index[df_best['Name of report'] == min_report], inplace=True)
                dict_perf = {'Name of report' : name, 'Performance' : global_performance}
                new_df = pd.concat([df_best,pd.DataFrame(dict_perf, index=[0])], ignore_index = True)
                # print(new_df.head())
                new_df.to_csv(f'best_report/best_{mode}.csv', index = False)
                generatePDF(generator_var, dict_value, global_performance, name)
                    
    except FileNotFoundError:
        dict_perf = {'Name of report' : name, 'Performance' : global_performance}
        df_best = pd.DataFrame(dict_perf, index=[0])
        df_best.to_csv(f'best_report/best_{mode}.csv', index = False)
        generatePDF(generator_var, dict_value, global_performance, name)
 
## @brief Method which remove the reports that aren't on the best.csv nor the best_{mode}.csv file.
#  @details NOT WORKING
#  @param   name    name of the report
#  @param   node    used mode    
def removeReport(name, mode):
  
    df_best = pd.read_csv(f'best_report/best.csv')
    df_best_mode = pd.read_csv(f'best_report/best_{mode}.csv')
    
    if not (name in df_best['Name of report'].values or name in df_best_mode['Name of report'].values):
        os.remove(f"report/{name}.pdf")

