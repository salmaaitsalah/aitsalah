#include "datacollection-module-utility.h"
#include "ns3/simulator.h"
#include "ns3/wifi-phy.h"
#include "ns3/node.h"
#include <fstream>
#include <iostream>

using namespace std;

NS_LOG_COMPONENT_DEFINE ("DataCollectionModuleUtility");

namespace ns3 {

NS_OBJECT_ENSURE_REGISTERED (DataCollectionModuleUtility);
TypeId
DataCollectionModuleUtility::GetTypeId (void)
{
  static TypeId tid =
      TypeId ("ns3::DataCollectionModuleUtility")
          .SetParent<Object> ()
          .AddConstructor<DataCollectionModuleUtility> ()
          .AddTraceSource ("Test", "A test integer",
                           MakeTraceSourceAccessor (&DataCollectionModuleUtility::test_value),
                           "ns3::TraceValueCallBack::Int32")
          .AddTraceSource ("LatestDatum", "The datum in the back of m_dataset",
                           MakeTraceSourceAccessor (&DataCollectionModuleUtility::latest_datum),
                           "ns3::TraceValueCallBack:Datum");
  return tid;
}

DataCollectionModuleUtility::DataCollectionModuleUtility ()
{
  jamposition = Vector (0, 0, 0);
}

//connect the utility to the netdevice of the simulation
void
DataCollectionModuleUtility::SetNetDevice (Ptr<WaveNetDevice> device)
{
  m_netdevice = device;
}

void
DataCollectionModuleUtility::SetWirelessModuleUtility (Ptr<WirelessModuleUtility> w_utility)
{
  m_Wutility = w_utility;
}

void
DataCollectionModuleUtility::SetWirelessModuleUtility (
    std::vector<Ptr<WirelessModuleUtility>> w_utilityList)
{
  for (uint32_t i = 0; i < w_utilityList.size (); i++)
    m_WutilityList.push_back (w_utilityList[i]);
}

void
DataCollectionModuleUtility::ResetAfterSwitching (void)
{
  NS_LOG_DEBUG ("DataCollectionModuleUtility::ResetAfterSwitching at" << Simulator::Now ());
  m_dataset.push_back (m_datum);
  test_value = m_dataset.size ();
  latest_datum = m_dataset.back ();
  // NS_LOG_UNCOND ("Dataset size: " << m_dataset.size () << std::endl);
  m_datum.ls = 0; //number of successful rxok slots
  m_datum.lc = 0; //number failed rx slots
  m_datum.le = 0; //number of error rx slots (failed due to multi mpdu receiving fail)
  m_datum.ltx = 0; // number tx slots
  m_datum.m_s.clear (); //state of this CCHI
  m_datum.minRxOkPowerW =
      0; // minimum RX power for PHY layer in Watts currently is snr in replacement
  m_datum.maxRxOkPowerW = 0; // maximum RX power for PHY layer in Watts
  auto phy = m_netdevice->GetPhy (0);
  NS_LOG_DEBUG ("DataCollectionModuleUtility:: ResetAfterSwitching");
  Simulator::Schedule (phy->GetChannelSwitchDelay (),
                       &DataCollectionModuleUtility::UpdateChannelNumber, this);
  //  m_datum.currentChannel = phy->GetChannelNumber();  // current channel number
  m_datum.contentionwindowid += 1;
  m_datum.m_jammed = 0; //label the CW if it is jammed or not
}
void
DataCollectionModuleUtility::UpdateChannelNumber (void)
{
  auto phy = m_netdevice->GetPhy (0);
  m_datum.currentChannel = phy->GetChannelNumber ();
}

bool
DataCollectionModuleUtility::InitialDataCollectionUtility (Ptr<WaveNetDevice> device,
                                                           Ptr<WirelessModuleUtility> w_utility,
                                                           Vector jpos)
{
  NS_LOG_DEBUG ("DataCollectionModuleUtility initial at node" << device->GetNode ()->GetId ());

  SetNetDevice (device);
  NS_LOG_DEBUG ("DataCollectionModuleUtility SetNetDevice done, wifinetdevice found "
                << m_netdevice);
  SetWirelessModuleUtility (w_utility);

  // NS_LOG_DEBUG("DataCollectionModuleUtility SetWirelessmodule done");

  m_Wutility->TraceConnectWithoutContext (
      "SendPacket", MakeCallback (&DataCollectionModuleUtility::TraceFunction_Jammer, this));

  m_datum.nodeid = device->GetNode ()->GetId ();

  // NS_LOG_DEBUG ("DataCollectionModuleUtility m_Wutility found" << m_Wutility << " at node "
  //                                                              << m_datum.nodeid);
  // NS_LOG_DEBUG("DataCollectionModuleUtility node found" << m_datum.nodeid);
  auto phy = m_netdevice->GetPhy (0);
  phy->TraceConnectWithoutContext (
      "PhyRxDrop", MakeCallback (&DataCollectionModuleUtility::TraceFunction_RxDrop, this));
  phy->TraceConnectWithoutContext (
      "PhyTxEnd", MakeCallback (&DataCollectionModuleUtility::TraceFunction_Tx, this));
  NS_LOG_DEBUG ("DataCollectionModuleUtility phy found" << phy << "at node " << m_datum.nodeid);
  Ptr<WifiPhyStateHelper> state = phy->GetState ();
  NS_LOG_DEBUG ("DataCollectionModuleUtility state found" << state);
  bool b = state->TraceConnectWithoutContext (
      "State", MakeCallback (&DataCollectionModuleUtility::TraceFunction_StateLogger, this));
  NS_LOG_DEBUG ("trace source state is found " << b);
  b = state->TraceConnectWithoutContext (
      "RxOk", MakeCallback (&DataCollectionModuleUtility::TraceFunction_RxOk, this));
  NS_LOG_DEBUG ("trace source RxOk is found " << b);
  b = state->TraceConnectWithoutContext (
      "RxError", MakeCallback (&DataCollectionModuleUtility::TraceFunction_RxError, this));
  NS_LOG_DEBUG ("trace source RxError is found " << b);
  jamposition = jpos;
  return 1;
}

// DONE: Change this to receive list of w_utility and std::vector<Vector> jpos
bool
DataCollectionModuleUtility::InitialDataCollectionUtility (
    Ptr<WaveNetDevice> device, std::vector<Ptr<WirelessModuleUtility>> w_utilityList,
    std::vector<Vector> jposList)
{
  NS_LOG_DEBUG ("DataCollectionModuleUtility initial at node" << device->GetNode ()->GetId ());

  SetNetDevice (device);
  NS_LOG_DEBUG ("DataCollectionModuleUtility SetNetDevice done, wifinetdevice found "
                << m_netdevice);

  SetWirelessModuleUtility (w_utilityList);

  // NS_LOG_DEBUG("DataCollectionModuleUtility SetWirelessmodule done");

  m_datum.nodeid = device->GetNode ()->GetId ();
  // DONE: Loop through m_Wutility to trace
  for (uint32_t i = 0; i < m_WutilityList.size (); i++)
    {
      Ptr<WirelessModuleUtility> wutility = m_WutilityList[i];

      m_WutilityList[i]->TraceConnectWithoutContext (
          "SendPacket", MakeCallback (&DataCollectionModuleUtility::TraceFunction_Jammer, this));
    }

  // NS_LOG_DEBUG("DataCollectionModuleUtility node found" << m_datum.nodeid);
  auto phy = m_netdevice->GetPhy (0);
  phy->TraceConnectWithoutContext (
      "PhyRxDrop", MakeCallback (&DataCollectionModuleUtility::TraceFunction_RxDrop, this));
  phy->TraceConnectWithoutContext (
      "PhyTxEnd", MakeCallback (&DataCollectionModuleUtility::TraceFunction_Tx, this));
  NS_LOG_DEBUG ("DataCollectionModuleUtility phy found" << phy << "at node " << m_datum.nodeid);
  Ptr<WifiPhyStateHelper> state = phy->GetState ();
  NS_LOG_DEBUG ("DataCollectionModuleUtility state found" << state);
  bool b = state->TraceConnectWithoutContext (
      "State", MakeCallback (&DataCollectionModuleUtility::TraceFunction_StateLogger, this));
  NS_LOG_DEBUG ("trace source state is found " << b);
  b = state->TraceConnectWithoutContext (
      "RxOk", MakeCallback (&DataCollectionModuleUtility::TraceFunction_RxOk, this));
  NS_LOG_DEBUG ("trace source RxOk is found " << b);
  b = state->TraceConnectWithoutContext (
      "RxError", MakeCallback (&DataCollectionModuleUtility::TraceFunction_RxError, this));
  NS_LOG_DEBUG ("trace source RxError is found " << b);
  jampositionList = jposList;
  return 1;
}
void
DataCollectionModuleUtility::UpdateRxPowerofDatum (double snr)
{
  if (m_datum.minRxOkPowerW > snr)
    {
      m_datum.minRxOkPowerW = snr;
    }
  if (m_datum.maxRxOkPowerW < snr)
    {
      m_datum.maxRxOkPowerW = snr;
    }
}

bool
DataCollectionModuleUtility::CheckChannelSwitching (state statelogger)
{
  // NS_LOG_DEBUG ("DataCollectionModuleUtility::CheckChannelSwitching state =" << statelogger.s);
  if (statelogger.s_start == Simulator::Now () && statelogger.s == WifiPhyState::SWITCHING)
    {
      ResetAfterSwitching ();
      return 1;
    }
  else
    {
      return 0;
    }
}
// Trace functions
void
DataCollectionModuleUtility::TraceFunction_RxOk (Ptr<const Packet> pkt, double snr, WifiMode mode,
                                                 WifiPreamble preamble) //m_rxOkCallback
{
  NS_LOG_DEBUG ("RxOk at node: " << m_datum.nodeid << std::endl);
  m_datum.ls += 1;
  UpdateRxPowerofDatum (snr);
}

void
DataCollectionModuleUtility::TraceFunction_RxDrop (Ptr<const Packet> p,
                                                   WifiPhyRxfailureReason reason)
{
  m_datum.lc += 1;
  //log out failure reasons: but later
  // NS_LOG_DEBUG("failed reason: "<< reason);
  NS_LOG_DEBUG ("failed reason: " << std::endl);
}

void
DataCollectionModuleUtility::TraceFunction_RxError (Ptr<const Packet> pkt, double snr)
{
  NS_LOG_DEBUG ("RxError packet size = " << pkt->GetSize ());
  m_datum.le += 1;
}
void
DataCollectionModuleUtility::TraceFunction_Tx (Ptr<const Packet> p)
{
  NS_LOG_DEBUG ("node " << m_datum.nodeid << " tx");
  m_datum.ltx += 1;
}

void
DataCollectionModuleUtility::TraceFunction_StateLogger (Time start, Time duration, WifiPhyState s)
{
  // NS_LOG_DEBUG ("DataCollectionModuleUtility::Trace_StateLogger m_dataset.size = "
  //               << m_dataset.size () << " m_s.size = " << m_datum.m_s.size ());
  state statelogger;
  statelogger.s_start = start;
  statelogger.s_end = duration;
  statelogger.s = s;
  m_datum.m_s.push_back (statelogger);
  CheckChannelSwitching (statelogger);
}
void
DataCollectionModuleUtility::TraceFunction_Jammer (Ptr<WifiPsdu> psdu, double &powerW,
                                                   int utilitySendMode)
{
  // DONE: Comment or fix this
  NS_LOG_DEBUG ("DataCollectionModuleUtility::TraceFunction_Jammer jammer utility = "
                << m_Wutility << " at node " << m_datum.nodeid);
  Ptr<MobilityModel> mobility = m_netdevice->GetNode ()->GetObject<MobilityModel> ();
  Vector m_pos = mobility->GetPosition ();
  // DONE: Change this to loop through jampositions and through m_Wutility
  for (uint32_t i = 0; i < m_WutilityList.size (); i++)
    {
      Ptr<WirelessModuleUtility> wutility = m_WutilityList[i];
      for (uint32_t j = 0; j < jampositionList.size (); j++)
        {
          Vector jampos = jampositionList[j];
          if ((wutility->m_victim == 1) &&
              (CalculateDistance (m_pos, jampos) <
               250)) // fix the maximum impacted range of jammer is 250m
            {
              m_datum.m_jammed = 1;
            }
        }
    }
  // if ((m_Wutility->m_victim == 1) && (CalculateDistance (m_pos, jamposition) <
  //                                     250)) // fix the maximum impacted range of jammer is 250m
  //   {
  //     m_datum.m_jammed = 1;
  //   }
}

void
DataCollectionModuleUtility::UpdateNeighborList (uint32_t neighbornum)
{
  NS_LOG_DEBUG ("Updating NeighborList to " << neighbornum << " at node " << m_datum.nodeid);
  m_datum.m_numberofNeighbor = neighbornum;
}

//print out
void
DataCollectionModuleUtility::PrintOutStateObserveeachCW (std::string logfile)
{
  NS_LOG_DEBUG ("DataCollectionModuleUtility::PrintOutStateObserveeachCW sizeof dataset = "
                << m_dataset.size ());
  ofstream log;
  log.open (logfile);
  log << "State Observation from node " << m_netdevice->GetNode ()->GetId ()
      << " at different cw \n";
  for (std::list<datum>::const_iterator i = m_dataset.begin (); i != m_dataset.end (); i++)
    {
      log << "TimeStart \t Duration \t state \t channel \t cw \n";
      for (std::list<state>::const_iterator j = (i->m_s).begin (); j != (i->m_s).end (); ++j)
        {
          log << j->s_start << "\t" << j->s_end << "\t" << j->s << "\t" << i->currentChannel << "\t"
              << i->contentionwindowid << "\n";
        }
    }
  log.close ();
}
void
DataCollectionModuleUtility::PrintOut (std::string logfile)
{
  NS_LOG_DEBUG ("DataCollectionModuleUtility::PrintOut sizeof dataset = " << m_dataset.size ());
  ofstream log;
  log.open (logfile);
  log << "Observation from node " << m_netdevice->GetNode ()->GetId () << " : \n";
  log << "nodeid \t ls \t lc \t le \t ltx \t minRxPower(snr) \t maxRxPower(snr) \t channelNumber "
         "\t cwid \t label(jammed or not)\t number of neighbors \n";
  for (std::list<datum>::const_iterator i = m_dataset.begin (); i != m_dataset.end (); i++)
    {
      log << m_netdevice->GetNode ()->GetId () << "\t" << i->ls << "\t" << i->lc << "\t" << i->le
          << "\t" << i->ltx << "\t" << i->minRxOkPowerW << "\t" << i->maxRxOkPowerW << "\t"
          << i->currentChannel << "\t" << i->contentionwindowid << "\t" << i->m_jammed << "\t"
          << i->m_numberofNeighbor << "\n";
    }
  log << m_netdevice->GetNode ()->GetId () << "\t" << m_datum.ls << "\t" << m_datum.lc << "\t"
      << m_datum.le << "\t" << m_datum.ltx << "\t" << m_datum.minRxOkPowerW << "\t"
      << m_datum.maxRxOkPowerW << "\t" << m_datum.currentChannel << "\t"
      << m_datum.contentionwindowid << "\t" << m_datum.m_jammed << "\t"
      << m_datum.m_numberofNeighbor << "\n";
  log.close ();
}

} // namespace ns3
