#include "ns3/wifi-ppdu.h"
#include "ns3/wifi-psdu.h"
#include "ns3/wifi-utils.h"
//#include "ns3/simulator.h"
#include "jammer-wifi-phy.h"

namespace ns3 {

NS_LOG_COMPONENT_DEFINE ("JammerWifiPhy");

NS_OBJECT_ENSURE_REGISTERED (JammerWifiPhy);

TypeId
JammerWifiPhy::GetTypeId (void)
{
    static TypeId tid = TypeId ("ns3::JammerWifiPhy")
      .SetParent<YansWifiPhy> ()
      .SetGroupName ("Jamming")
      .AddConstructor<JammerWifiPhy> ()
    ;
    return tid;
}

JammerWifiPhy::JammerWifiPhy()
{
    NS_LOG_FUNCTION (this);
}

JammerWifiPhy::~JammerWifiPhy()
{
    NS_LOG_FUNCTION (this);
}

void 
JammerWifiPhy::SetCurrentWifiTxVector (WifiTxVector txVector)
{
  m_currentWifiTxVector = txVector;
}

void
JammerWifiPhy::StartReceivePreamble (Ptr<WifiPpdu> ppdu, double rxPowerW)
{
    SetCurrentWifiTxVector (ppdu->GetTxVector());
    UpdatePhyLayerInfo();
    DriverStartRx(ppdu, MeasureRss());
   // Simulator::Schedule(MicroSeconds(12),&JammerWifiPhy::DriverStartRx,this,ppdu,MeasureRss);  //delay for sensing before start jamming
   // WifiPhy::StartReceivePreamble(ppdu,rxPowerW);
    SetCurrentWifiTxVector (ppdu->GetTxVector());

}

double
JammerWifiPhy::MeasureRss (void)
{
  NS_LOG_FUNCTION (this);
  return WifiPhy::m_interference.CurrentNodeRss (m_currentWifiTxVector);
}

bool
JammerWifiPhy::DriverStartRx (Ptr<WifiPpdu> ppdu, double startRssW)
{
  NS_LOG_FUNCTION (this << *ppdu << startRssW);

  bool isPacketToBeReceived = true;

  // notify utility for start of RX
  if (m_utility != NULL)
    {
      if (m_state->IsStateRx ())
      {
        m_utility->m_victim =+ 1;
      }
      else
      {
        m_utility->m_victim = 1;
      }
      isPacketToBeReceived =  m_utility->StartRxHandler (ppdu, startRssW);
    }
  else
    {
      NS_LOG_DEBUG ("NslWifiPhy:Utility module is *not* installed on Node #" << m_node->GetId());
    }

  return isPacketToBeReceived;
}

void
JammerWifiPhy::SetNode (Ptr<Node> nodePtr)
{
  NS_LOG_FUNCTION (this << nodePtr);
  m_node = nodePtr;
}

void
JammerWifiPhy::DoStart (void)
{
  NS_LOG_FUNCTION (this);
  InitDriver ();  // initialize driver at beginning of simulation
}

void
JammerWifiPhy::ResetDriver (void)
{
  NS_LOG_FUNCTION (this);
  m_isDriverInitialized = false;
  m_utility = NULL;
}

void
JammerWifiPhy::InitDriver (void)
{
  NS_LOG_FUNCTION (this);
  if (!m_isDriverInitialized)
    {
      NS_LOG_DEBUG ("NslWifiPhy:Driver being initialized at Node #" << m_node->GetId ());
      // setting default wifi mode
      
      m_utility = m_node->GetObject<WirelessModuleUtility> ();
      if (m_utility != NULL)
        {
          m_utility->SetRssMeasurementCallback (MakeCallback (&JammerWifiPhy::MeasureRss, this));
          m_utility->SetSendPacketCallback (MakeCallback (&JammerWifiPhy::UtilitySendPacket, this));
          m_utility->SetChannelSwitchCallback (MakeCallback (&WifiPhy::SetChannelNumber, this));
         // UpdatePhyLayerInfo ();
        }
      m_isDriverInitialized = true;
    }
  else
    {
      NS_LOG_DEBUG ("NslWifiPhy:Driver already initialized at Node #" << m_node->GetId ());
    }
  // show some debug messages
  if (m_utility == NULL)
    {
      NS_LOG_DEBUG ("NslWifiPhy:Utility module is *not* installed on Node #" << m_node->GetId ());
    }
}

void
JammerWifiPhy::UpdatePhyLayerInfo (void)
{
  NS_LOG_FUNCTION (this);
  m_phyLayerInfo.currentChannel = WifiPhy::GetChannelNumber();
  m_phyLayerInfo.maxTxPowerW = DbmToW (WifiPhy::GetTxPowerEnd());
  m_phyLayerInfo.minTxPowerW = DbmToW (WifiPhy::GetTxPowerStart());
  m_phyLayerInfo.TxGainDb = WifiPhy::GetTxGain();
  m_phyLayerInfo.RxGainDb = WifiPhy::GetRxGain();
  m_phyLayerInfo.numOfChannels = 11;  // XXX assuming US standard

  uint16_t channelwidth = m_currentWifiTxVector.GetChannelWidth();
  WifiMode mode = m_currentWifiTxVector.GetMode();

  m_phyLayerInfo.phyRate = mode.GetDataRate (channelwidth);
  m_phyLayerInfo.channelSwitchDelay = WifiPhy::GetChannelSwitchDelay();
  // notify utility
  if (m_utility != NULL)
    {
      m_utility->SetPhyLayerInfo (m_phyLayerInfo);
    }
  else
    {
      NS_LOG_DEBUG ("JammerWifiPhy:Utility is *not* installed on Node #" <<
                    m_node->GetId ());
    }
}

void
JammerWifiPhy::UtilitySendPacket(Ptr<WifiPsdu> psdu, double &powerW, int utilitySendMode)
{
  NS_LOG_FUNCTION (this << psdu << powerW << utilitySendMode);

  // Convert power in Watts to a power level
  uint8_t powerLevel;
  powerLevel = (uint8_t)(WifiPhy::GetNTxPower() * (WToDbm(powerW) - WifiPhy::GetTxPowerStart()) /
               (WifiPhy::GetTxPowerEnd() - WifiPhy::GetTxPowerStart()));

  if (powerLevel >= 0 && powerLevel < WifiPhy::GetNTxPower())
    {
      NS_LOG_DEBUG ("NslWifiPhy:Inside send packet callback at node #" <<
                    m_node->GetId() << ". Sending packet.");
      switch (utilitySendMode)
        {
        case WirelessModuleUtility::SEND_AS_JAMMER:
          NS_LOG_DEBUG ("JammerWifiPhy: Sending packet as jammer.");
          m_currentWifiTxVector.SetPreambleType(WIFI_PREAMBLE_LONG);
          if (!m_state->IsStateTx () && !m_state->IsStateSwitching ())
          {
          WifiPhy::Send(psdu, m_currentWifiTxVector);
          }
          break;
        case WirelessModuleUtility::SEND_AS_HONEST:
          {

            NS_LOG_DEBUG ("JammerlWifiPhy: Sending packet as honest node.");
            WifiPhy::Send (psdu, m_currentWifiTxVector);
          }
          break;
        case WirelessModuleUtility::SEND_AS_OTHERS:
          NS_FATAL_ERROR ("JammerWifiPhy:Undefined utility send packet mode!");
          break;
        default:
          break;
        }
      // update the actual TX power
      powerW = DbmToW (WifiPhy::GetTxPowerStart());
      powerW += powerLevel * DbmToW ((WifiPhy::GetTxPowerEnd() - WifiPhy::GetTxPowerStart()) / WifiPhy::GetNTxPower());
    }
  else
    {
      NS_LOG_DEBUG ("JammerWifiPhy: Node # "<< m_node->GetId () <<
                    "Error in send packet callback. Incorrect power level.");
      // set sent power to 0 to indicate error
      powerW = 0;
    }
}

void 
JammerWifiPhy::SendPacket(Ptr<WifiPsdu> psdu, WifiTxVector txvector, double power)
{
  NS_ASSERT (!m_state->IsStateTx () && !m_state->IsStateSwitching ());
  Time txDuration = CalculateTxDuration(psdu->GetSize(),txvector,WIFI_PHY_BAND_5GHZ);
if (m_state->IsStateRx ())
    {
      m_endRxEvent.Cancel ();
      m_interference.NotifyRxEnd ();
    }
  double txPowerDbm = GetPowerDbm (power) + GetTxGain();
  NotifyTxBegin (psdu,txPowerDbm);
  
  m_state->SwitchToTx (txDuration, psdu->GetPacket(), power, txvector);
 
 Ptr<WifiPpdu> ppdu = Create<WifiPpdu>(psdu,txvector,txDuration,WIFI_PHY_BAND_5GHZ);
  m_channel->Send (this, ppdu,txPowerDbm);

  /*
   * Driver interface.
   */
  SetCurrentWifiTxVector (txvector);
 // DriverStartTx (ppdu, DbmToW (txPowerDbm));
}

}
