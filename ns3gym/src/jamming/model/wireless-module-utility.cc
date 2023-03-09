#include "wireless-module-utility.h"
#include "ns3/packet.h"
#include "ns3/wifi-mac-header.h"

NS_LOG_COMPONENT_DEFINE ("WirelessModuleUtility");

namespace ns3 {

NS_OBJECT_ENSURE_REGISTERED (WirelessModuleUtility);

TypeId
WirelessModuleUtility::GetTypeId (void)
{
  static TypeId tid = TypeId ("ns3::WirelessModuleUtility")
    .SetParent<Object> ()
    .AddConstructor<WirelessModuleUtility> ()
    .AddTraceSource("SendPacket",
                    "trace callback when a jamming packet is sent",
                    MakeTraceSourceAccessor(&WirelessModuleUtility::m_SendPacketTraceCallback),
                    "ns3::WirelessModuleUtility::m_SendPacketTraceCallback")
    ;
  return tid;
}

WirelessModuleUtility::WirelessModuleUtility (void)
{

  m_rssMeasurementCallback.Nullify ();
  m_sendPacketCallback.Nullify ();
  m_startRxCallback.Nullify();
  m_channelSwitchCallback.Nullify ();
  m_victim = 1;
}
WirelessModuleUtility::~WirelessModuleUtility (void)
{
}

void
WirelessModuleUtility::SetRssMeasurementCallback (UtilityRssCallback RssCallback)
{
  NS_LOG_FUNCTION (this);
  m_rssMeasurementCallback = RssCallback;
}

void
WirelessModuleUtility::SetChannelSwitchCallback (UtilityChannelSwitchCallback channelSwitchCallback)
{
  NS_LOG_FUNCTION (this);
  m_channelSwitchCallback = channelSwitchCallback;
}

void
WirelessModuleUtility::SetSendPacketCallback (UtilitySendPacketCallback sendPacketCallback)
{
  NS_LOG_FUNCTION (this);
  m_sendPacketCallback = sendPacketCallback;
}

void
WirelessModuleUtility::SetStartRxCallback (UtilityRxCallback startRxCallback)
{
  NS_LOG_FUNCTION (this);
  m_startRxCallback = startRxCallback;
}

void
WirelessModuleUtility::SetPhyLayerInfo (PhyLayerInfo info)
{
  NS_LOG_FUNCTION (this);
  m_phyLayerInfo.channelSwitchDelay = info.channelSwitchDelay;
  m_phyLayerInfo.currentChannel = info.currentChannel;
  m_phyLayerInfo.maxTxPowerW = info.maxTxPowerW;
  m_phyLayerInfo.minTxPowerW = info.minTxPowerW;
  m_phyLayerInfo.numOfChannels = info.numOfChannels;
  m_phyLayerInfo.phyRate = info.phyRate;
  m_phyLayerInfo.RxGainDb = info.RxGainDb;
  m_phyLayerInfo.TxGainDb = info.TxGainDb;

}

WirelessModuleUtility::PhyLayerInfo
WirelessModuleUtility::GetPhyLayerInfo (void) const
{
  NS_LOG_FUNCTION (this);
  return m_phyLayerInfo;
}

bool
WirelessModuleUtility::StartRxHandler (Ptr<WifiPpdu> ppdu, double startRssW)
{
  NS_LOG_FUNCTION (this << *ppdu << startRssW);
  // notify jammer or jamming mitigation
  if (!m_startRxCallback.IsNull ())
    {
      //std::cout<< "WirelessModuleUtility::StartRxhandler debug 1: m_startRxCallBack"<< m_startRxCallback (ppdu, startRssW)<< std::endl;
      return m_startRxCallback (ppdu, startRssW);
    }
  else
    {
      NS_LOG_DEBUG ("WirelessModuleUtility:StartRxHandler is not installed!");
      return true;
    }
}
/*
void
WirelessModuleUtility::EndRxHandler (Ptr<WifiPpdu> ppdu,
                                     double averageRssW,
                                     const bool isSuccessfullyReceived)
{
  NS_LOG_FUNCTION (this << ppdu << averageRssW << isSuccessfullyReceived);
  NS_LOG_DEBUG ("WirelessModuleUtility:Handling received packet from PHY!");

  // Update the RSS since the value will change when the packet ends.
  //UpdateRss();
  
 // AnalyzeAndRecordIncomingPacket (packet, isSuccessfullyReceived);

  //m_avgPktRssW = averageRssW;

  // notify jammer or mitigation module
  if (m_endRxCallback.IsNull ())
    {
      NS_LOG_DEBUG ("WirelessModuleUtility:Brain is not installed!");
    }
  else
    {
      if (isSuccessfullyReceived)
        {
          m_endRxCallback (ppdu, averageRssW);
        }
      else
        {
          m_endRxCallback (NULL, averageRssW); // pass NULL if packet is corrupted
        }
    }
}
*/
double
WirelessModuleUtility::SendJammingSignal (double power, Time duration)
{
  NS_LOG_FUNCTION (this << power << duration);
//std::cout<< "WirelessModuleUtility::SendJammingSignal debug 1 jamming duration = "<< duration << std::endl;
  // Check that the power is within allowed range of PHY layer
  if (power > m_phyLayerInfo.maxTxPowerW)
    {
      NS_LOG_ERROR ("WirelessModuleUtility:Power of "<< power <<
                    " W is not supported by PHY layer, max power = " <<
                    m_phyLayerInfo.maxTxPowerW << ", scaling to max power!");
      power = m_phyLayerInfo.maxTxPowerW;
    }
  else if (power < m_phyLayerInfo.minTxPowerW)
    {
      NS_LOG_ERROR ("WirelessModuleUtility:Power of "<< power <<
                    " W is not supported by PHY layer, min power = " <<
                    m_phyLayerInfo.minTxPowerW << ", scaling to min power!");
      power = m_phyLayerInfo.minTxPowerW;
    }

  /*
   * Convert the desired signal length into a packet of corresponding size for
   * sending through PHY layer.
   */
  uint32_t numBytes = duration.GetSeconds() * m_phyLayerInfo.phyRate / 8 ;
  //std::cout<< "WirelessModuleUtility::SendJammingSignal debug 2 numbyte = "<< numBytes << std::endl;
  if (m_sendPacketCallback.IsNull ())
    {
      NS_FATAL_ERROR ("WirelessModuleUtility:Send packet callback is NOT set!");
    }
  // send jamming signal
  WifiMacHeader machdr;
  machdr.SetType(WIFI_MAC_MGT_BEACON);
  //std::cout<< "WirelessModuleUtility::SendJammingSignal debug 3 MAC hdr size = "<< machdr.GetSize() << std::endl;
  Ptr<Packet> packet = Create<Packet>(numBytes - machdr.GetSize());
 // std::cout<< "WirelessModuleUtility::SendJammingSignal debug 4 jamming packet size = "<< packet->GetSize() << std::endl;
  auto psdu = Create<WifiPsdu> (packet,machdr);
  m_sendPacketCallback (psdu, power, SEND_AS_JAMMER);
  m_SendPacketTraceCallback(psdu, power, SEND_AS_JAMMER);
 
  return power;
}

}