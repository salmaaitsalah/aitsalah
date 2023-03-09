/* -*- Mode:C++; c-file-style:"gnu"; indent-tabs-mode:nil; -*- */

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
#include "ns3/wave-net-device.h"
#include "ns3/wave-mac-helper.h"
#include "ns3/wave-helper.h"
//#include "ns3/jammer-helper.h"

#include "ns3/ns2-mobility-helper.h"

using namespace ns3;

class JammingAttackSimulation
{
  public:
  void ScenarioSetup(uint32_t NodeNum, double JamProb); //Setup victims, jammer nodes, applications, channel switching
  bool Receive (Ptr<NetDevice> dev, Ptr<const Packet> pkt, uint16_t mode, const Address &sender);


  private:

  void CreateWaveNodes (); // create victims nodes and jammer node: node 0
  void SetupApplication(void);
  Ptr<ListPositionAllocator> PositionSetup(std::string tracefilename);
  void SetupMobility(uint8_t mobilitymode);

  NodeContainer m_nodes;
  NetDeviceContainer m_devices;
  uint32_t m_nodeNum;
  double m_JamProb;
  std::string m_mobilitytracefile;
  uint8_t m_mobilitymode = 0 ; //= 1 if ns2 trace is used, 0 if listPositionAllocator is used
};

bool
JammingAttackSimulation::Receive (Ptr<NetDevice> dev, Ptr<const Packet> pkt, uint16_t mode, const Address &sender)
{
  SeqTsHeader seqTs;
  pkt->PeekHeader (seqTs);
  std::cout << "receive a packet: " << std::endl
            << "  sequence = " << seqTs.GetSeq () << "," << std::endl
            << "  sendTime = " << seqTs.GetTs ().GetSeconds () << "s," << std::endl
            << "  recvTime = " << Now ().GetSeconds () << "s," << std::endl
            << "  protocol = 0x" << std::hex << mode << std::dec  << std::endl;
  return true;
}

void
JammingAttackSimulation::CreateWaveNodes()
{
  m_nodes.Create(m_nodeNum);
  if (m_mobilitymode == 1)
  {
    Ns2MobilityHelper mobility = Ns2MobilityHelper(m_mobilitytracefile);
    mobility.Install();
  }
  else
  {
  MobilityHelper mobility;
  mobility.SetPositionAllocator(PositionSetup(m_mobilitytracefile));
  mobility.SetMobilityModel("ConstantAccelerationMobilityModel");
  mobility.Install(m_nodes);
  }
  
  NslWifiChannelHelper channelhelper = NslWifiChannelHelper::Default();
  Ptr<NslWifiChannel> channel = channelhelper.Create();
  QosWaveMacHelper waveMac = QosWaveMacHelper::Default ();
  WaveHelper waveHelper = WaveHelper::Default ();

  for (uint32_t k = 0; k< m_devices.GetN(); k ++)
  {
    if (k==0) // Setup jammer node 0
    {
        
        JammerWifiPhyHelper jamPhy = JammerWifiPhyHelper::Default();     
        jamPhy.SetChannel(channel);
        m_devices = waveHelper.Install(jamPhy,waveMac,m_nodes.Get(k));
        JammerHelper jamhelper;
        jamhelper.SetJammerType("ns3::ReactiveJammer");
        jamhelper.Set("ReactiveJammerFixedProbability",DoubleValue(m_JamProb));
        jamhelper.Install(m_nodes.Get(k));

    }
    else //Setup other node
    {
      YansWavePhyHelper wavePhy =  YansWavePhyHelper::Default ();
      wavePhy.SetChannel (channel);
      wavePhy.SetPcapDataLinkType (YansWifiPhyHelper::DLT_IEEE802_11);      
      m_devices = waveHelper.Install(wavePhy,waveMac,m_nodes.Get(k));
    }
    
  }  

  const SchInfo schInfo = SchInfo (CCH, true, EXTENDED_ALTERNATING);
  
  for (uint32_t k = 0; k< m_devices.GetN(); k ++)
  {
//Set up channel switching alternatively and receive notification
    Ptr<WaveNetDevice> devicei = DynamicCast<WaveNetDevice>(m_devices.Get(k));
    devicei->StartSch(schInfo); 
    devicei->SetReceiveCallback(MakeCallback(&JammingAttackSimulation::Receive,this));
  }  

};


void
JammingAttackSimulation::SetupApplication (void)
{
  Ptr<Packet> wsaPacket = Create<Packet> (100);
  Mac48Address dest = Mac48Address::GetBroadcast ();
  const VsaInfo vsaInfo = VsaInfo (dest, OrganizationIdentifier (), 0, wsaPacket, CCH, 50, VSA_TRANSMIT_IN_CCHI);//50 frames/5s = 1 frame/100ms
    for (uint32_t k = 0; k< m_devices.GetN(); k ++)
  {

    Ptr<WaveNetDevice> devicei = DynamicCast<WaveNetDevice>(m_devices.Get(k));

    if (k!=0) // node 0 is the jammer
    {
       // Beacon =wsa packet exchange, normal nodes exchange periodically vsa
      //devicei->StartVsa(vsaInfo);
      Simulator::Schedule(Seconds(5+k*0.001), &WaveNetDevice::StartVsa, devicei, vsaInfo);
    }   
  }  
};

void
JammingAttackSimulation::ScenarioSetup(uint32_t nodeNum, double JamProb)
{
  m_nodeNum = nodeNum;
  m_JamProb = JamProb;
  CreateWaveNodes();

  SetupApplication();
  
  Simulator::Stop (Seconds (10.0));
  Simulator::Run ();
  Simulator::Destroy ();
};

int 
main (int argc, char *argv[])
{
  uint32_t nodeNum=1; // number of node that includes 1 jammer node 0
  double JamProb=0;

  CommandLine cmd;
  cmd.AddValue ("N", "Input number of nodes", nodeNum);
  cmd.AddValue ("p", "Probability of reactive Jamming attack", JamProb);
  cmd.Parse (argc,argv);
  LogComponentEnable ("NslWifiChannel",LOG_FUNCTION);

  JammingAttackSimulation sim;
  sim.ScenarioSetup(nodeNum,JamProb);

  return 0;
}


