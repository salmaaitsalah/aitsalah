/* -*- Mode:C++; c-file-style:"gnu"; indent-tabs-mode:nil; -*- */

#include "DataCollection.h"

#include <fstream>
#include <iostream>

#include "mygym.h"

using namespace ns3;
//Scenario using ns2 tcl traces from PhDThesis:
/*
std::string traceFile="/home/aviSHOP/Programes/ns-allinone-3.19/ns-3.19/maps/highway_1cluster_highdensity_2jammers.tcl";
//std::string traceFile="/home/huongnguyenm/Programe/ns-allinone-3.19/ns-3.19/maps/highway_platoon_highdensity.mobility.tcl";
Ns2MobilityHelper ns2 = Ns2MobilityHelper (traceFile);
ns2.Install ();
*/

NS_LOG_COMPONENT_DEFINE ("JammingDataCollection");

int
main (int argc, char *argv[])
{
  // LogComponentEnable ("JammingDataCollection", LOG_LEVEL_DEBUG);
  // LogComponentEnable ("DataCollectionModuleUtility", LOG_LEVEL_DEBUG);
  // LogComponentEnable ("JammerWifiPhy", LOG_LEVEL_DEBUG);

  // Parameters of the environment
  uint32_t openGymPort = 5555;
  uint32_t agentNum = 0;

  uint32_t nodeNum = 10; // number of node that includes 1 jammer node 0
  double JamProb = 1;
  int experimentname = 0;
  uint8_t scenariooption = 1;

  CommandLine cmd;
  // required parameters for OpenGym interface
  cmd.AddValue ("openGymPort", "Port number for OpenGym env. Default: 5555", openGymPort);
  cmd.AddValue ("agentNum", "Number of agents. Default: 0", agentNum);

  cmd.AddValue ("N", "Input number of nodes", nodeNum);
  cmd.AddValue ("p", "Probability of reactive Jamming attack", JamProb);
  cmd.AddValue ("exp", "Experiment name by number", experimentname);
  cmd.AddValue ("scenario", "Scenario option 0 1 2", scenariooption);
  cmd.Parse (argc, argv);

  // OpenGymEnv
  std::vector<Ptr<OpenGymInterface>> openGymInterfaceVector;
  std::vector<Ptr<MyGymEnv>> gymEnvVector;

  for (uint32_t agentId = 1; agentId <= agentNum; agentId++)
    {
      Ptr<OpenGymInterface> openGymInterface = CreateObject<OpenGymInterface> (openGymPort);
      Ptr<MyGymEnv> myGymEnv = CreateObject<MyGymEnv> ();
      myGymEnv->SetOpenGymInterface (openGymInterface);
      openGymPort++;
      openGymInterfaceVector.push_back (openGymInterface);
      gymEnvVector.push_back (myGymEnv);
    }

  // std::string mobilitytrace ="./position-files/maps/highway_1cluster_highdensity.tcl";
  std::string TrafficTrace = "./GUSTtracefiles/experiment_" + std::to_string (experimentname) +
                             "/exp_" + std::to_string (experimentname) + "_rxtxtrace.txt";
  std::ofstream out (TrafficTrace);
  std::streambuf *coutbuf = std::cout.rdbuf (); //save old buf
  std::cout.rdbuf (out.rdbuf ()); //redirect std::cout to out.txt!

  std::cout << "experiment number " << experimentname << " Number of nodes = " << nodeNum
            << " JamProb = " << JamProb << " scenario option (0:validation;1:platoon;2: cluster) = "
            << (uint16_t) scenariooption << " \n"
            << std::endl;

  DataCollection sim;
  sim.SetupMobility (1);
  sim.ScenarioSetup (nodeNum, JamProb, scenariooption, gymEnvVector, openGymInterfaceVector);
  std::cout << sim.m_rxpackets << std::endl;
  sim.DatatracePrintOut ("experiment_" + std::to_string (experimentname));
  // openGymInterface->NotifySimulationEnd ();
  std::cout.rdbuf (coutbuf);
  return 0;
}
