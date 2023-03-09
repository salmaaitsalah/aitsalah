## @file main.py
#  @brief Main script to call.
#  @details Main script to call.
#  @author: Romain Durieux and Nathan Trouillet (2022)
from algo.execute import execute, resetPlotImg, findModeBest, findGlobalBest
from util.PDFGenerator import PDFGenerator, PDFGeneratorVar, generatePDF
from multiprocessing import Process
import multiprocessing as mp
import sys
from datetime import datetime
import argparse

## @brief   The function that parses the arguments we need.
#  @details This function init and parses the arguments we need. If there are not enough arguments, 
#           a helper option will print the correct syntax for the script. The types must also be 
#           respected otherwise the help option for the parameters will be printed.
#
#  @return  The number of arms, the arms object, the arms id.
def init_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("name_algo", help="The name of the algorithm used", type=str)
    parser.add_argument("nb_node", help="number of node used", type=int)
    parser.add_argument("epsilon", help="error value used in the evaluation", type=float)
    parser.add_argument("C", help="number of round used in the computation of certain QOS Mode", type=float)
    parser.add_argument("L", help="delay between the QoS computation and the used value (in round)", type=float)
    parser.add_argument("mode", help="QoS Computation mode", type=str)
    parser.add_argument("title_report", help="title of the outputed report", type=str)
    parser.add_argument("pretrain_mode", help="using the pretraining mode", type=bool)
    temp_args = parser.parse_args()
    return temp_args

########################################################
#################### Executed code. ####################
########################################################
args = init_parser()

if __name__ == '__main__':


    q = mp.Queue()
    list_process = []
    nb_node = 1
    model_used = None
    best_perf = 0
    resetPlotImg()
    
    generatorVar = PDFGeneratorVar(args)
    
    # Checking the arguments count.
    if len(sys.argv) == 9:
        nb = int(args.nb_node)
        pretrain = args.pretrain_mode
        if nb > 0 and nb < 10:
            nb_node = nb
        
        # Checking if a pre-training is needed.
        if pretrain :
            print(f"----------------START OF THE DEAD MODE :-----------------")
            # Initialize and start as many subprocesses indicated by args.nb_node.
            for i in range(1, nb_node + 1):
                sub_folder = "node{}".format(i)
                p = Process(target=execute, args=[i, args, q, False])
                p.start()
                list_process.append(p)   
                
            # Waiting for as many data in the Queue as the args.nb_node.
            print(nb_node)
            while q.qsize() != nb_node:
                pass       
            
            # Retrieving model from the pre-training. And select the best one.
            while q.qsize() > 0:
                print(f"start get - remaining objects : {q.qsize()}")
                node_id, model, performance = q.get(timeout=10)
                if performance >= best_perf :
                    best_perf = performance
                    model_used = model
                
                print(f"node {node_id} model received")
            
            # Waiting for every subprocesses to finish.
            for p in list_process: 
                p.join()
                
            print(f"best perf of pretrain phase : {best_perf}")
            
        # Initialize and start as many subprocesses indicated by args.nb_node using the best 
        # model retrieved before.
        print(f"----------------START OF THE LIVE MODE :-----------------")
        for i in range(1, nb_node + 1):
            sub_folder = "node{}".format(i)
            p = Process(target=execute, args=[i, args, q, True, model_used])
            p.start()
            list_process.append(p)

        # Waiting for as many data in the Queue as the args.nb_node.
        while q.qsize() != nb_node:
            pass       
        
        # Retrieving model from the pre-training. And select the best one.
        while q.qsize() > 0:
            node_id, acc, rcl, rcl_eval, spe, pre, perf = q.get()
            print(f"-----------PERF :{perf}")
            print(f"node {node_id} data received")
            generatorVar.dict_acc[f"node {node_id}"] = acc
            generatorVar.dict_rcl[f"node {node_id}"] = rcl
            generatorVar.dict_rcl_eval[f'node {node_id}'] = rcl_eval
            generatorVar.list_eps.append(args.epsilon)
            generatorVar.list_C.append(args.C)
            generatorVar.list_L.append(args.L)
            generatorVar.list_pre.append(pre)
            generatorVar.list_node_id.append(node_id)
            generatorVar.list_rcl.append(rcl)
            generatorVar.list_spe.append(spe)
            generatorVar.list_acc.append(acc)
            generatorVar.list_perf.append(perf)
            
        # Waiting for every subprocesses to finish.
        for p in list_process:
            p.join()
            print(f"end sub node process")
        
        # Generated data for pdfGenerator.
        dict_value = dict()
        dict_value['Node']=generatorVar.list_node_id
        dict_value['L'] = generatorVar.list_L
        dict_value['C'] = generatorVar.list_C
        dict_value['Epsilon'] = generatorVar.list_eps
        dict_value['Accuracy'] = generatorVar.list_acc
        dict_value['Recall'] = generatorVar.list_rcl
        dict_value['Precision'] = generatorVar.list_pre
        dict_value['Specificity'] = generatorVar.list_spe
        dict_value['Performance'] = generatorVar.list_perf
        
        # Current date for pdf title.
        now = datetime.now()
        dt_string = now.strftime("%d%m%Y%H%M%S_%f")
        name = f"Report_{args.mode}_{dt_string}"
        
        # pdf generation.
        global_performance = sum([float(x) for x in generatorVar.list_perf])/len(generatorVar.list_perf)
        print(f"global_performance: {global_performance}")
        print("Start Generate PDF")
        generatePDF(generatorVar, dict_value, global_performance, name)
        
        #PART ONLY USED IN CASE OF MULTIEXPERIMENT. NEED TO BE UNCOMMENTED IF YOU WANT TO RUN A MULTIEXPERIMENT
        
        #print("start find best")
        #findGlobalBest(global_performance)
        #findModeBest(global_performance)
        print("start find best")
        findGlobalBest(generatorVar, dict_value, global_performance, name)
        findModeBest(generatorVar, dict_value, global_performance, args.mode, name)

        
        print("END\n")
    else :
        print(" 7 arguments needed : algorithm, nb of node, epsilon, C, L, mode,title of the report, pretrain mode")
