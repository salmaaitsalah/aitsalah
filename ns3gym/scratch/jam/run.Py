import argparse
import json
import os
import time
import numpy as np
from multiprocessing import Process

parser = argparse.ArgumentParser()
parser.add_argument("--conf", dest="conf", action='store_true', help="Use conf parameters.")
parser.add_argument("-n", "--nb_node", dest="nb_node", help="Number of node used.", type=int)
parser.add_argument("-e", "--epsilon", dest="epsilon", help="Error value used in the evaluation.", type=float)
parser.add_argument("-c", "--C", dest="C", help="Number of round used in the computation of certain QOS Mode.", type=float)
parser.add_argument("-l", "--L", dest="L", help="Delay between the QoS computation and the used value (in round).", type=float)
parser.add_argument("-m", "--mode", dest="mode", help="QoS Computation mode.", type=str)
parser.add_argument("-t", "--title_report", dest="titlre_report", help="Title of the outputed report.", type=str)
parser.add_argument("-p", "--pretrain_mode", dest="pretrain_mode", action='store_true', help="Using the pretraining mode.")

args = parser.parse_args()

if __name__ == '__main__':
    #Template : 'Mode':{'Epsilon':[Min,Max,Step],'C':[Min,Max,Step], 'L':[Min,Max,Step]}
    #modeDict = { 
            #   'QOSAvgMedianDiv':{'Epsilon':[0.03,0.091,0.03],'C':[5,21,5], 'L':[5,50,15]},
             #   'QOSAvgExtremumSub':{'Epsilon':[0.001,0.003,0.001],'C':[5,21,5], 'L':[5,50,15]},
              #  'QOSAvgExtremumDiv':{'Epsilon':[0.007,0.021,0.007],'C':[5,21,5], 'L':[5,50,15]}
    #}
   # modeDict = None

    if not args.conf:
        strPretrain = "true" if args.pretrain_mode else "false"
        agentProcess = Process(target=os.system, args=[f"python main.py linucb {args.nb_node} {args.epsilon} {args.C} {args.L} {args.mode} '{args.mode}' {strPretrain}"])
        ns3GymProcess = Process(target=os.system, args=['../../waf --run "jam --agentNum=8 --openGymPort=5556"'])
        ns3GymProcess.start()
        time.sleep(1)
        agentProcess.start()
        ns3GymProcess.join()
        print("end process ns3gym")
        agentProcess.join()
        print("end process agent")
    
    else:
        with open('./run_conf.json') as conf:
            modeDict = json.load(conf)

        for key,value in modeDict.items():
            mode = key 
            for epsilon in np.arange(value['Epsilon'][0], value['Epsilon'][1], value['Epsilon'][2]):
                
                for C in np.arange(value['C'][0], value['C'][1], value['C'][2]):
                    if value['L'][0] > 0 :
                        for L in np.arange(value['L'][0], value['L'][1], value['L'][2]):
                            print(f"-----------MODE : {mode} EPSILON : {epsilon} C : {C} L : {L}-----------")
                            agentProcess = Process(target=os.system, args=[f"python main.py linucb 8 {epsilon} {C} {L} {mode} '{mode}' true"])
                            ns3GymProcess = Process(target=os.system, args=['../../waf --run "jam --agentNum=8 --openGymPort=5556"'])
                            ns3GymProcess.start()
                            time.sleep(1)
                            agentProcess.start()
                            ns3GymProcess.join()
                            print("end process ns3gym")
                            agentProcess.join()
                            print("end process agent")
                            
                            
                    else:
                        print(f"-----------MODE : {mode} EPSILON : {epsilon} C : {C} L : 1-----------")
                        agentProcess = Process(target=os.system, args=[f"python main.py linucb 8 {epsilon} {C} 1 {mode} '{mode}' true"])
                        ns3GymProcess = Process(target=os.system, args=['../../waf --run "jam --agentNum=8 --openGymPort=5556"'])
                        ns3GymProcess.start()
                        time.sleep(1)
                        agentProcess.start()
                        ns3GymProcess.join()
                        print("end process ns3gym")
                        agentProcess.join()                        
                        print("end process agent")

                   
