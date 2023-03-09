#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
from ns3gym import ns3env
from multiprocessing import Process
import time

def run_agent(port: int, agent_num: int):
    simArgs = {"--agentNum": agent_num}

    env = ns3env.Ns3Env(port=port, startSim=False, simArgs=simArgs, debug=False)
    env.reset()

    ob_space = env.observation_space
    ac_space = env.action_space
    print("Observation space: ", ob_space,  ob_space.dtype)
    print("Action space: ", ac_space, ac_space.dtype)

    stepIdx = 0

    try:
        while True:
            stepIdx += 1
            action = env.action_space.sample()
            print("---action: ", action)

            print("Step: ", stepIdx)
            obs, reward, done, info = env.step(action)
            print("---obs, reward, done, info: ", obs, reward, done, info)

            if done:
                break

    except KeyboardInterrupt:
        print("Ctrl-C -> Exit")
    finally:
        env.close()

def main(agent_num: int):
    starting_port = 5555
    processes = []
    # Create child processes to connect to the simulation environment
    for i in range(agent_num):
        p = Process(target=run_agent, args=(starting_port + i, agent_num))
        p.start()
        processes.append(p)
    for p in processes:
        p.join()

if __name__=='__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent_num", "-a", type=int, default=2, choices=range(1, 9), help="the number of agent interacting with the environment")
    args = parser.parse_args()
    main(args.agent_num)