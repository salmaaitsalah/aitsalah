/* -*- Mode:C++; c-file-style:"gnu"; indent-tabs-mode:nil; -*- */
#ifndef DATACOLLECTION_H
#define DATACOLLECTION_H

#include "ns3/command-line.h"
#include "ns3/node.h"
#include "ns3/packet.h"
#include "ns3/simulator.h"
#include "ns3/node-container.h"
#include "ns3/net-device-container.h"
#include "ns3/jammer-wifi-helper.h"
#include "ns3/jammer-helper.h"
#include "ns3/mobility-helper.h"
#include "ns3/seq-ts-header.h"
#include "ns3/llc-snap-header.h"
#include "ns3/wave-net-device.h"
#include "ns3/wave-mac-helper.h"
#include "ns3/wave-helper.h"
//#include "ns3/jammer-helper.h"

#include "ns3/ns2-mobility-helper.h"
#include "ns3/constant-velocity-mobility-model.h"
#include "ns3/datacollection-module-utility.h"
#include "neighborlist.h"
#include "mygym.h"

#include <fstream>
#include <iostream>

// NS_LOG_COMPONENT_DEFINE ("DataCollection");

using namespace ns3;
//Scenario using ns2 tcl traces from PhDThesis:
/*
std::string traceFile="/home/aviSHOP/Programes/ns-allinone-3.19/ns-3.19/maps/highway_1cluster_highdensity_2jammers.tcl";
//std::string traceFile="/home/huongnguyenm/Programe/ns-allinone-3.19/ns-3.19/maps/highway_platoon_highdensity.mobility.tcl";
Ns2MobilityHelper ns2 = Ns2MobilityHelper (traceFile);
ns2.Install ();
*/

static void
Send (Ptr<WaveNetDevice> netdevice, Mac48Address &dest, double arrivalrate,
      Ptr<ExponentialRandomVariable> X1)
{
  Ptr<Packet> packet = Create<Packet> (500);
  const static uint16_t WSMP_PROT_NUMBER = 0x88DC;
  const TxInfo txInfo = TxInfo (CCH);
  uint32_t deviceid = netdevice->GetNode ()->GetId ();
  auto phy = netdevice->GetPhy (0);
  Ptr<MobilityModel> mobility = netdevice->GetNode ()->GetObject<MobilityModel> ();
  std::cout << "WaveNet Device node " << deviceid << " systime "
            << Simulator::Now ().GetMilliSeconds () << " type: s ; psize = " << packet->GetSize ()
            << " position " << mobility->GetPosition () << " at channel "
            << (uint16_t) ((DynamicCast<WifiPhy> (phy))->GetChannelNumber ()) << std::endl;
  netdevice->SendX (packet, dest, WSMP_PROT_NUMBER, txInfo);
  //arrivalrate = duration between two consecutive sent packets in seconds
  Time t = Seconds (X1->GetValue ());
  Simulator::Schedule (Seconds (arrivalrate) + t, &Send, netdevice, dest, arrivalrate, X1);
};
class DataCollection
{
public:
  //Setup victims, jammer nodes, applications, channel switching, scenario option: 0 if validation, 1 if platoon, 2 if clusters
  void ScenarioSetup (uint32_t NodeNum, double JamProb, std::string mobilitytracefilename);
  void ScenarioSetup (uint32_t NodeNum, double JamProb, uint8_t scenariooption);
  void ScenarioSetup (uint32_t NodeNum, double JamProb, uint8_t scenariooption,
                      std::vector<Ptr<ns3::MyGymEnv>> &envVector,
                      std::vector<Ptr<OpenGymInterface>> &openGymInterfaceVector);

  bool ReceiveVSA (Ptr<const Packet> pkt, const Address &address, uint32_t, uint32_t);
  bool Receive (Ptr<NetDevice> nd, Ptr<const Packet> p, uint16_t protocol, const Address &addr);

  void DatatraceSetup (void);
  void DatatraceSetup (std::vector<Ptr<ns3::MyGymEnv>> &envVector);

  void DatatracePrintOut (std::string experimentname);
  void SetupMobility (uint8_t mobilitymode);

  uint16_t m_rxpackets = 0;
  // Vector m_jammerPos; // DONE: Change this to std::list<Vector>
  // DONE: Add a number of jam node, 1 by default

  uint32_t num_jamNode = 1;
  Vector m_jammerPos;
  std::vector<Vector> m_jammerPosList;

private:
  void CreateWaveNodes (); // create victims nodes and jammer node: node 0
  void CreateWaveNodes (
      uint8_t scenariooption); // create victims nodes and jammer node: node 0 with scenario option
  void PhyMacSetup (void);

  void SetupApplication (void);
  void SetupApplication (
      uint8_t
          scenariooption); // default application includes only beacons comming periodically in Exponential distribution (Bound= 46ms and mean=1)
  void ClusterTopoBuild (
      double *d, uint32_t startelement,
      uint32_t
          endelement); // create position of n nodes in a cluster that belong to the array d of all nodes
  Ptr<ListPositionAllocator> PositionSetup (void);
  Ptr<ListPositionAllocator> PositionSetup (uint8_t scenariooption);

  void SetJamPos (void);

  NodeContainer m_nodes;
  NetDeviceContainer m_devices;
  uint32_t m_nodeNum;
  double m_JamProb;
  std::string m_mobilitytracefile;
  uint8_t m_mobilitymode = 0; //= 1 if ns2 trace is used, 0 if listPositionAllocator is used
  std::vector<Ptr<DataCollectionModuleUtility>> m_datatrace;
  std::vector<NeighborList> m_neighbortrace;
};

/*-------------Implementation--------*/
Ptr<ListPositionAllocator>
DataCollection::PositionSetup (void)
{
  double d[m_nodeNum];
  std::ifstream myfile (m_mobilitytracefile);
  uint16_t count = 0;
  std::string str;
  std::string::size_type sz;
  if (myfile.is_open ())
    {

      while (count < m_nodeNum)
        {
          getline (myfile, str);
          //  std::cout << "str =  " << str << std::endl;
          d[count] = std::stod (str, &sz);
          count = count + 1;
        }
      myfile.close ();
    }
  else
    std::cout << "Unable to open file";
  Ptr<ListPositionAllocator> positionAlloc = CreateObject<ListPositionAllocator> ();
  for (uint32_t i = 0; i < m_nodeNum; i++)
    {
      positionAlloc->Add (Vector (d[i], 0.0, 0.0));
      // std::cout << "d = " << d[i] << std::endl;
    }
  // m_jammerPos = Vector (d[0], 0.0, 0.0); // DONE: Set this to be the first element of the list
  m_jammerPosList.push_back (Vector (d[0], 0.0, 0.0));
  return positionAlloc;
};

void
DataCollection::SetupMobility (uint8_t mobilitymode)
{
  m_mobilitymode = mobilitymode;
};

bool
DataCollection::ReceiveVSA (Ptr<const Packet> pkt, const Address &address, uint32_t, uint32_t)
{
  // std::cout << "receive a VSA management frame: recvTime = " << Now ().GetSeconds () << "s." << std::endl;
  m_rxpackets = m_rxpackets + 1;
  return true;
};

bool
DataCollection::Receive (Ptr<NetDevice> nd, Ptr<const Packet> p, uint16_t protocol,
                         const Address &addr)
{
  uint32_t deviceid = nd->GetNode ()->GetId ();
  // if (deviceid > 0)
  if (deviceid >= num_jamNode)
    {
      m_neighbortrace[deviceid - num_jamNode].SetMaxQueueTime (Seconds (5.0));
      m_neighbortrace[deviceid - num_jamNode].UpdateList (addr, Now ());
      m_datatrace[deviceid - num_jamNode]->UpdateNeighborList (
          m_neighbortrace[deviceid - num_jamNode].GetSize ());
      // NS_LOG_UNCOND ("update neighbor list at node "
      //                << deviceid << " size = " << m_neighbortrace[deviceid - num_jamNode].GetSize ()
      //                << std::endl);
    }
  m_rxpackets = m_rxpackets + 1;
  Ptr<MobilityModel> mobility = nd->GetNode ()->GetObject<MobilityModel> ();
  auto phy = DynamicCast<WaveNetDevice> (nd)->GetPhy (0);
  std::cout << "WaveNet Device node " << deviceid << " systime "
            << Simulator::Now ().GetMilliSeconds () << " type: r ; psize = " << p->GetSize ()
            << " position " << mobility->GetPosition () << " srcid " << addr << " at channel "
            << (uint16_t) ((DynamicCast<WifiPhy> (phy))->GetChannelNumber ()) << std::endl;
  return true;
};

////Trace functions
void
DataCollection::PhyMacSetup (void)
{
  NslWifiChannelHelper channelhelper = NslWifiChannelHelper::Default ();
  Ptr<NslWifiChannel> channel = channelhelper.Create ();
  QosWaveMacHelper waveMac = QosWaveMacHelper::Default ();
  WaveHelper waveHelper = WaveHelper::Default ();

  for (uint32_t k = 0; k < m_nodes.GetN (); k++)
    {
      // if (k == 0) // Setup jammer node 0
      if (k < num_jamNode) // Setup jammer nodes
        {
          JammerHelper jamhelper;
          jamhelper.SetJammerType ("ns3::ReactiveJammer");
          jamhelper.Set ("ReactiveJammerFixedProbability", DoubleValue (m_JamProb));
          jamhelper.Set ("ReactiveJammerRxTxSwitchingDelay", TimeValue (MicroSeconds (12)));
          jamhelper.Set ("ReactiveJammerJammingDuration", TimeValue (MicroSeconds (500)));
          jamhelper.Install (m_nodes.Get (k));
          NS_LOG_UNCOND ("Setup jammer = done " << std::endl);
          JammerWifiPhyHelper jamPhy = JammerWifiPhyHelper::Default ();
          jamPhy.Set ("TxPowerEnd", DoubleValue (23));
          jamPhy.Set ("TxPowerStart", DoubleValue (23));
          jamPhy.Set ("RxSensitivity", DoubleValue (-90.00));
          jamPhy.SetChannel (channel);
          waveHelper.Install (jamPhy, waveMac, m_nodes.Get (k));
        }
      else //Setup other node
        {
          YansWavePhyHelper wavePhy = YansWavePhyHelper::Default ();
          wavePhy.Set ("TxPowerEnd", DoubleValue (17.48));
          wavePhy.Set ("TxPowerStart", DoubleValue (17.48));
          wavePhy.Set ("RxSensitivity", DoubleValue (-85.00));
          wavePhy.SetChannel (channel);
          wavePhy.SetPcapDataLinkType (YansWifiPhyHelper::DLT_IEEE802_11);
          waveHelper.Install (wavePhy, waveMac, m_nodes.Get (k));
        }
      m_devices.Add (m_nodes.Get (k)->GetDevice (0));
    }

  //const SchInfo schInfo = SchInfo (SCH1, true, EXTENDED_ALTERNATING);

  for (uint32_t k = 0; k < m_devices.GetN (); k++)
    {
      //Set up channel switching alternatively and receive notification
      Ptr<WaveNetDevice> devicei = DynamicCast<WaveNetDevice> (m_devices.Get (k));
      // devicei->StartSch(schInfo);
      // if (k > 0) //Receiver
      if (k >= num_jamNode) //Receiver
        {
          devicei->SetWaveVsaCallback (MakeCallback (&DataCollection::ReceiveVSA, this));
          devicei->SetReceiveCallback (MakeCallback (&DataCollection::Receive, this));
        }
      //trace phy state
    }
};

void
DataCollection::CreateWaveNodes ()
{
  m_nodes.Create (m_nodeNum);
  if (m_mobilitymode == 1)
    {
      Ns2MobilityHelper mobility = Ns2MobilityHelper (m_mobilitytracefile);
      mobility.Install ();
    }
  else
    {
      MobilityHelper mobility;
      mobility.SetPositionAllocator (PositionSetup ());
      mobility.SetMobilityModel ("ns3::ConstantVelocityMobilityModel");
      mobility.Install (m_nodes);
    }

  PhyMacSetup ();
  for (uint32_t k = 0; k < m_nodes.GetN (); k++)
    {
      if (m_mobilitymode == 1)
        {
          Ptr<ConstantVelocityMobilityModel> model =
              m_nodes.Get (k)->GetObject<ConstantVelocityMobilityModel> ();
          // if (k > 0)
          if (k >= num_jamNode)
            {
              model->SetVelocity (Vector (30.0, 0.0, 0.0));
            }
        }
    }
};

void
DataCollection::SetupApplication (void)
{
  //Ptr<Packet> wsaPacket = Create<Packet> (500);
  Ptr<ExponentialRandomVariable> X1[m_nodeNum];
  Time t[m_nodeNum];
  double arrivalrate = 0.1; //50 packets/s = 1/arrivalrate
  Mac48Address dest = Mac48Address::GetBroadcast ();
  //const VsaInfo vsaInfo = VsaInfo (dest, OrganizationIdentifier (), 0, wsaPacket, CCH, 100, VSA_TRANSMIT_IN_CCHI);//50 frames/5s = 1 frame/100ms
  const SchInfo schInfo = SchInfo (SCH1, true, EXTENDED_ALTERNATING);
  // TxProfile txprof(CCH);
  for (uint32_t k = 0; k < m_devices.GetN (); k++)
    {

      Ptr<WaveNetDevice> devicei = DynamicCast<WaveNetDevice> (m_devices.Get (k));
      // devicei->RegisterTxProfile(txprof);
      Simulator::Schedule (Seconds (0.0), &WaveNetDevice::StartSch, devicei, schInfo);
      Simulator::Schedule (Seconds (150.0), &WaveNetDevice::StopSch, devicei, SCH1);
      // if (k > 1) // node 0 is the jammer, Transmitter sends packet
      if (k > num_jamNode)
        {
          X1[k] = CreateObject<ExponentialRandomVariable> ();
          X1[k]->SetAttribute ("Bound", DoubleValue (0.046));
          t[k] = Seconds (X1[k]->GetValue ());

          Simulator::Schedule (t[k], &Send, devicei, dest, arrivalrate, X1[k]);
        }
    }
};

void
DataCollection::DatatraceSetup (void)
{
  Ptr<Node> jammer = m_nodes.Get (0); //node 0 is alway the jammer
  Ptr<WirelessModuleUtility> Wutility = jammer->GetObject<WirelessModuleUtility> ();
  for (uint32_t i = 1; i < m_devices.GetN (); i++)
    {
      Ptr<DataCollectionModuleUtility> utility = CreateObject<DataCollectionModuleUtility> ();
      NeighborList nlist;
      m_neighbortrace.push_back (nlist);
      auto phy = DynamicCast<WaveNetDevice> (m_devices.Get (i))->GetPhy (0);
      //  std::cout<<"phy at node"<<i<< "found"<< phy <<" state = "<< phy->GetState() << std::endl;

      utility->InitialDataCollectionUtility (DynamicCast<WaveNetDevice> (m_devices.Get (i)),
                                             Wutility, m_jammerPos);
      //  std::cout<<"Initial DataCollection done"<< std::endl;
      m_datatrace.push_back (utility);
    }
  // std::cout<< "datatrace size = "<< m_datatrace.size()<< " m_devices = "<< m_devices.GetN()<< std::endl;
}
void
DataCollection::ScenarioSetup (uint32_t nodeNum, double JamProb, std::string mobilitytracefilename)
{
  m_nodeNum = nodeNum;
  m_JamProb = JamProb;
  m_mobilitytracefile = mobilitytracefilename;
  CreateWaveNodes ();
  //  std::cout<< "Number of nodes = "<< m_nodeNum<< " Number of Devices = "<< m_devices.GetN()<< std::endl;

  SetupApplication ();

  DatatraceSetup ();

  Simulator::Stop (Seconds (150.0));
  Simulator::Run ();
  Simulator::Destroy ();
};

void
DataCollection::DatatracePrintOut (std::string experimentname)
{
  for (uint32_t i = num_jamNode; i < m_devices.GetN (); i++)
    {
      std::string tracefile_state = "./GUSTtracefiles/" + experimentname + "/node_" +
                                    std::to_string (i) + "_statetrace.txt"; //state trace of a node
      std::string tracefile = "./GUSTtracefiles/" + experimentname + "/node_" + std::to_string (i) +
                              "_traceall.txt"; //ls lc le.. trace of a node
      m_datatrace[i - num_jamNode]->PrintOutStateObserveeachCW (tracefile_state);
      m_datatrace[i - num_jamNode]->PrintOut (tracefile);
    }
}

/*-------------------part2----------------------*/

Ptr<ListPositionAllocator>
DataCollection::PositionSetup (uint8_t scenariooption)
{
  double d[m_nodeNum];
  Ptr<ListPositionAllocator> positionAlloc = CreateObject<ListPositionAllocator> ();
  if (scenariooption ==
      0) //validation scenario, all nodes are within transmission range of each other
    {
      d[0] = 251.0;
      d[1] = 210; //150.0;
      d[2] = 220; //20.0;
      d[3] = 230; //100.23;
      d[4] = 240; //126.19;
      d[5] = 260; //158.86;
      d[6] = 200;
      d[7] = 200;
      d[8] = 251.78;
      d[9] = 251.78;
      for (uint32_t i = 0; i < 10; i++)
        {
          positionAlloc->Add (Vector (d[i], 0.0, 0.0));
          // std::cout << "d = " << d[i] << std::endl;
        }
    }
  else if (scenariooption == 1) // platoon scenario
    // DONE: Set the position of n first jam node
    {
      // d[0] = 1000.0;
      // positionAlloc->Add (Vector (d[0], 0.0, 0.0));
      SetJamPos ();
      NS_LOG_UNCOND ("Finish setting up jam positions." << std::endl);
      for (uint32_t i = 0; i < num_jamNode; i++)
        {
          positionAlloc->Add (m_jammerPosList[i]);
        }
      // d[1] = 150.0;
      d[num_jamNode] = 150.0;
      for (uint32_t i = num_jamNode; i < m_nodeNum; i++)
        {
          positionAlloc->Add (Vector (d[i], 1.0, 0.0));
          d[i + 1] = d[i] - 5;
        }
    }
  else
    {
      num_jamNode = 1;
      d[0] = 300.0;
      positionAlloc->Add (Vector (d[0], 0.0, 0.0));
      d[1] = 250.0; // Cluster1: lane 1
      ClusterTopoBuild (d, 1, 5);
      d[6] = d[1]; //Cluster 1: lane 2
      ClusterTopoBuild (d, 6, 10);
      d[11] = d[1] - 200; //Cluster 2: lane 1
      ClusterTopoBuild (d, 11, 15);
      d[16] = d[11]; // Cluster 2: lane 2
      ClusterTopoBuild (d, 16, 20);
      for (uint32_t i = 1; i < m_nodeNum; i++)
        {
          if ((i > 0 && i <= 5) || (i > 10 && i <= 15)) // lane 1
            {
              positionAlloc->Add (Vector (d[i], 1.0, 0.0));
            }
          else
            {
              positionAlloc->Add (Vector (d[i], 1.0, 0.0));
            }
        }
      m_jammerPosList.clear ();
      m_jammerPosList.push_back (Vector (d[0], 0.0, 0.0)); // DONE: Change this to a list of vector
    }

  return positionAlloc;
};

void
DataCollection::ClusterTopoBuild (double *d, uint32_t startelement, uint32_t endelement)
{
  Ptr<ExponentialRandomVariable> D;
  D = CreateObject<ExponentialRandomVariable> ();
  D->SetAttribute ("Mean", DoubleValue (5));
  for (uint32_t i = startelement; i < endelement; i++)
    {
      double temp = D->GetValue ();
      if (temp < 5)
        {
          temp = temp + 5;
        }
      d[i + 1] = d[i] - temp;
    }
};
void
DataCollection::CreateWaveNodes (uint8_t scenariooption)
{
  m_nodes.Create (m_nodeNum);

  MobilityHelper mobility;
  mobility.SetPositionAllocator (PositionSetup (scenariooption));
  mobility.SetMobilityModel ("ns3::ConstantVelocityMobilityModel");
  mobility.Install (m_nodes);

  PhyMacSetup ();

  Ptr<ExponentialRandomVariable> D;
  D = CreateObject<ExponentialRandomVariable> ();
  D->SetAttribute ("Mean", DoubleValue (19));
  D->SetAttribute ("Bound", DoubleValue (22));

  for (uint32_t k = 0; k < m_nodes.GetN (); k++)
    {
      Ptr<ConstantVelocityMobilityModel> model =
          m_nodes.Get (k)->GetObject<ConstantVelocityMobilityModel> ();
      if (scenariooption == 0)
        {
          model->SetVelocity (Vector (0.0, 0.0, 0.0));
        }
      else if (scenariooption == 1)
        {
          // if (k > 0)
          if (k >= num_jamNode)
            {
              model->SetVelocity (Vector (30.0, 0.0, 0.0));
            }
        }
      else
        {
          double temp = D->GetValue ();
          if ((k > 0 && k <= 5) || (k > 10 && k <= 15)) // lane 1
            {
              model->SetVelocity (Vector (temp, 0.0, 0.0));
            }
          else // lane 2
            {
              model->SetVelocity (Vector (temp, 0.0, 0.0));
            }
        }
    }
};

void
DataCollection::ScenarioSetup (uint32_t nodeNum, double JamProb, uint8_t scenariooption)
{
  m_nodeNum = nodeNum;
  m_JamProb = JamProb;

  CreateWaveNodes (scenariooption);
  //  std::cout<< "Number of nodes = "<< m_nodeNum<< " Number of Devices = "<< m_devices.GetN()<< std::endl;

  SetupApplication ();

  DatatraceSetup ();

  Simulator::Stop (Seconds (150.0));
  Simulator::Run ();
  Simulator::Destroy ();
}

/*-------------------Add gym env----------------------*/

void
DataCollection::DatatraceSetup (std::vector<Ptr<ns3::MyGymEnv>> &envVector)
{
  // DONE: Change this to first n node to be jammer
  std::vector<Ptr<WirelessModuleUtility>> WutilityList;
  NS_LOG_UNCOND ("envVector size: " << envVector.size () << std::endl);
  for (uint32_t i = 0; i < num_jamNode; i++)
    {
      Ptr<Node> jammer = m_nodes.Get (i);
      WutilityList.push_back (jammer->GetObject<WirelessModuleUtility> ());
      NS_LOG_UNCOND ("Wutility: " << WutilityList[i] << ", size: " << sizeof (*WutilityList[i])
                                  << std::endl);
    }
  // Ptr<Node> jammer = m_nodes.Get (0); //node 0 is alway the jammer
  // Ptr<WirelessModuleUtility> Wutility = jammer->GetObject<WirelessModuleUtility> ();
  for (uint32_t i = num_jamNode; i < m_devices.GetN (); i++)
    {
      Ptr<DataCollectionModuleUtility> utility = CreateObject<DataCollectionModuleUtility> ();
      // utility->TraceConnectWithoutContext ("Test", MakeCallback (&ns3::MyGymEnv::TestTrace));
      Ptr<ns3::MyGymEnv> env;
      if (i - num_jamNode < envVector.size ())
        {
          env = envVector[i - num_jamNode];
          NS_LOG_UNCOND ("Setting up interface for node: " << i << std::endl);
          utility->TraceConnectWithoutContext ("LatestDatum",
                                               MakeBoundCallback (&ns3::MyGymEnv::DatumTrace, env));
        }
      NeighborList nlist;
      m_neighbortrace.push_back (nlist);
      auto phy = DynamicCast<WaveNetDevice> (m_devices.Get (i))->GetPhy (0);
      //  std::cout<<"phy at node"<<i<< "found"<< phy <<" state = "<< phy->GetState() << std::endl;

      utility->InitialDataCollectionUtility (DynamicCast<WaveNetDevice> (m_devices.Get (i)),
                                             WutilityList, m_jammerPosList);
      NS_LOG_UNCOND ("Initial DataCollection done for node " << i << std::endl);
      m_datatrace.push_back (utility);
    }
  // std::cout<< "datatrace size = "<< m_datatrace.size()<< " m_devices = "<< m_devices.GetN()<< std::endl;
}

void
DataCollection::ScenarioSetup (uint32_t nodeNum, double JamProb, uint8_t scenariooption,
                               std::vector<Ptr<ns3::MyGymEnv>> &envVector,
                               std::vector<Ptr<OpenGymInterface>> &openGymInterfaceVector)
{
  m_nodeNum = nodeNum;
  m_JamProb = JamProb;

  CreateWaveNodes (scenariooption);
  //  std::cout<< "Number of nodes = "<< m_nodeNum<< " Number of Devices = "<< m_devices.GetN()<< std::endl;

  SetupApplication ();

  DatatraceSetup (envVector);
  NS_LOG_UNCOND ("Finish Datatrace Setup" << std::endl);

  Simulator::Stop (Seconds (150.0));
  // Simulator::Stop (Seconds (300.0));
  NS_LOG_UNCOND ("Running simulation for 150s" << std::endl);
  Simulator::Run ();
  NS_LOG_UNCOND ("Simulation run successfully" << std::endl);

  for (auto const &i : openGymInterfaceVector)
    {
      i->NotifySimulationEnd ();
    }
  Simulator::Destroy ();
  NS_LOG_UNCOND ("Simulation destroyed" << std::endl);
};

void
DataCollection::SetJamPos (void)
{
  m_jammerPosList.push_back (Vector (1000, 0.0, 0.0));
  m_jammerPosList.push_back (Vector (2000, 0.0, 0.0));
  // m_jammerPosList.push_back (Vector (3000, 0.0, 0.0));
  num_jamNode = m_jammerPosList.size ();
  NS_LOG_UNCOND ("Setting up simulation with " << num_jamNode << " jammers." << std::endl);
}

#endif