#ARGS : nb_node_train[1-10] 
import glob
import sys
import os
import random
import pandas as pd 
import numpy as np
import distutils

debug_mode = False

def execute():
    nodes_info = getNodesInfo()
    generateClasses()
    generateDescriptions(nodes_info)
    generatePredictions(nodes_info)
    return

def generateClasses():
    print("---------GENERATE CLASSES---------")
    class_names = ["Jammed", "Not_Jammed"]
    class_id = np.identity(len(class_names)).astype(int)

    df_class = pd.DataFrame(class_id)
    df_class['classes'] = class_names
    df_class = df_class[['classes', 0, 1]]
    
    if debug_mode == True :
        print("class_id : \n", class_id)
        print("df_class.head() : \n", df_class.head())
        
    df_class.to_csv('../processed_data/classes.txt', header = False , sep = ';')
    return

def generateDescriptions(nodes_info):
    print("---------GENERATE DESCRIPTIONS---------")

    for node in nodes_info :
        df_desc = pd.DataFrame()
        df_desc = pd.concat([df_desc, node[1]], ignore_index= True)
        df_desc = df_desc[['nodeid ',' ls ', ' lc ', ' le ', ' ltx ',' number of neighbors ']]
        if debug_mode == True :
            print("df_desc : \n", df_desc)
    
        try:
            # Create target Directory
            os.mkdir(f'../processed_data/node{node[2]}/')
            print(f"Directory node{node[2]} Created ") 
        except FileExistsError:
            print(f"Directory node{node[2]} Created ")
            
        df_desc.to_csv(f'../processed_data/node{node[2]}/descriptions.txt', header = False , sep = ';')
    
    return

def generatePredictions(nodes_info):
    print("---------GENERATE PREDICTIONS---------")

    for node in nodes_info :
        i = 0
        dict_pred = {}
        list_jammed = list()
        list_choice = list()
        list_index = list()
        for index, row in node[1].iterrows() :
            list_index.append(i)
            list_index.append(i)
            
            list_choice.append(0)
            list_choice.append(1)
            
            if row[' label(jammed or not)'] == 0 :
                list_jammed.append(1)
                list_jammed.append(0)
            else : 
                list_jammed.append(0)
                list_jammed.append(1)
            i += 1
    
        dict_pred["idx"] = list_index
        dict_pred["choice"] = list_choice
        dict_pred["jammed"] = list_jammed
        dict_pred["idx_2"] = list_index
    
        df_pred = pd.DataFrame(dict_pred)
    
        if debug_mode == True :
            print("df_pred : \n", df_pred)
        
        df_pred.to_csv(f'../processed_data/node{node[2]}/predictions.txt', header = False , sep = ';', index = False)

def getNodesInfo(nb_nodes = int(sys.argv[1])):
    print("---------GET NODES INFO---------")
    #we gather the statetrace and traceall file of nb_nodes numbers of node chosen randomly (between 1 and 9 included)
    nodes_number = random.sample(range(1, 10), nb_nodes)
    files = []
    for number in nodes_number :
        files.append([f for f in glob.glob("../unprocessed_data/*.csv") if str(number) in f and 'exp' not in f])
        
    if debug_mode == True :
        print("nodes number : ", nodes_number)
        print("res : ", files)

    res = []
    
    #we read and process the data to have a clean dataframe (remove the first row and all other irrelevant rows)
    for file in files :
    
        df_state_trace = pd.read_csv(file[0], sep = '\t', skiprows=1)
        df_state_trace = df_state_trace[~df_state_trace[df_state_trace.columns[0]].isin(['TimeStart '])]
        
        df_trace_all = pd.read_csv(file[1], sep = '\t', skiprows=1)
        df_trace_all = df_trace_all[~df_trace_all[' channelNumber '].isin([172])] 
        
        res.append([df_state_trace, df_trace_all, file[0].split('_')[2]])
        
        if debug_mode == True :
            for col in df_trace_all.columns:
                print("col : ", col.replace(' ', '_'))
                
            print("file : ", file)
            print("df_state_trace.head() : \n",df_state_trace.head())
            print("df_trace_all.head() : \n",df_trace_all.head())
    
    return res
            
if __name__ == '__main__':
    if len(sys.argv) < 2 or len(sys.argv) >= 4 or int(sys.argv[1]) < 1 or int(sys.argv[1]) >=10:
        print("1 argument is needed and 1 argument is optionnal: number of node's [1-8] information used for the training - debug [debug] (optionnal)")
    else:
        print("You have chosen " + str(sys.argv[1]) + " node(s)")

        if sys.argv[-1] != None and sys.argv[-1] == "debug" :
            debug_mode = True
        execute()