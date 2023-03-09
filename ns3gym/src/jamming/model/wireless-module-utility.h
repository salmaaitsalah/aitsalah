#ifndef WIRELESS_MODULE_UTILITY_H
#define WIRELESS_MODULE_UTILITY_H

#include "ns3/callback.h"
#include "ns3/traced-callback.h"
#include "ns3/object.h"
#include "ns3/nstime.h"
#include "ns3/wifi-ppdu.h"
#include "ns3/wifi-psdu.h"


namespace ns3 {
class WirelessModuleUtility : public Object
{
public:
  typedef struct PhyLayerInfo
  {
    double minTxPowerW;   // minimum TX power for PHY layer in Watts
    double maxTxPowerW;   // minimum TX power for PHY layer in Watts
    double TxGainDb;      // Tx gain, in dB
    double RxGainDb;      // Rx gain, in dB
    uint32_t phyRate;     // PHY rate in bits per second
    uint16_t numOfChannels;   // number of channels
    uint16_t currentChannel;  // current channel number
    Time channelSwitchDelay;  // channel switch delay
  } PhyLayerInfo;

/**
   * Different modes for PHY layer send callback.
   */
  enum PacketSendMode
  {
    SEND_AS_JAMMER = 0,
    SEND_AS_HONEST,
    SEND_AS_OTHERS
  };
/**
   * Callback type for RSS calculation in PHY.
   */
  typedef Callback<double> UtilityRssCallback;
  /**
   * Callback type for sending packet in PHY.
   */
  typedef Callback<void, Ptr<WifiPsdu>, double&, int> UtilitySendPacketCallback;
  TracedCallback<Ptr<WifiPsdu>, double&, int> m_SendPacketTraceCallback;

  /**
   * Callback for channel switch in PHY.
   */
  typedef Callback<void, uint8_t> UtilityChannelSwitchCallback;

/**
   * Callback for start/end of TX.
   */
  typedef Callback<void, Ptr<WifiPpdu>> UtilityTxCallback;

  /**
   * Callback for handling start/end of RX.
   */
  typedef Callback<bool, Ptr<WifiPpdu>, double> UtilityRxCallback;
  //m_victim to count number of transmissions in a given time slot that jammer may jammed
  uint8_t m_victim = 1;


  void SetRssMeasurementCallback (UtilityRssCallback RssCallback);
  void SetChannelSwitchCallback (UtilityChannelSwitchCallback channelSwitchCallback);
  void SetSendPacketCallback (UtilitySendPacketCallback sendPacketCallback);
  void SetStartRxCallback (UtilityRxCallback startRxCallback);
  
  void SetPhyLayerInfo (PhyLayerInfo info);
  PhyLayerInfo GetPhyLayerInfo (void) const;

    /**
   * \brief Handle a start of packet reception event.
   *
   * \param packet Pointer to the packet to be received.
   * \param startRss RSS at the start of the packet.
   * \returns True if the incoming packet is to be received. False if the packet
   * is to be dropped.
   *
   * Implementation of this function is based on YansWifiPhy class, it may not
   * be directly applicable to other wireless protocols. For reactive jammers,
   * it stops receiving the rest of the packet as soon as the preambles are
   * received. This function invokes the StartRxHandler callback in reactive
   * jammer to stop receiving current packet and start sending jamming signals.
   */
  bool StartRxHandler (Ptr<WifiPpdu> ppdu, double startRss);
  /**
   * \brief Handle an end of packet reception notification.
   *
   * \param packet Pointer to packet that has been received.
   * \param averageRss Average RSS over the reception of the packet.
   * \param isSuccessfullyReceived True if packets was received successfully.
   *
   * This function forwards the received packet to appropriate callbacks. It
   * is called inside by PHY layer driver at EndRx.
   */
  //void EndRxHandler (Ptr<WifiPpdu> ppdu, double averageRss,
   //                  const bool isSuccessfullyReceived);
    /**
   * \brief Used by jammers to send out a jamming signal of a given power level
   * and duration.
   *
   * \param power double indicating the power of the jamming signal to be sent
   * \param duration Duration of the jamming burst
   * \returns TX power (in Watts) the signal is actually sent with.
   *
   * This function sends jamming signal of specific power via the PHY layer. If
   * the sending power is not supported by the PHY layer. The signal power will
   * be scaled to the nearest supported value.
   */
  double SendJammingSignal (double power, Time duration);
  
public:

static TypeId GetTypeId (void);
  WirelessModuleUtility ();
  virtual ~WirelessModuleUtility ();
private:
PhyLayerInfo m_phyLayerInfo;
/**
   * Callback for measure current RSS (in watts). Done by PHY layer driver.
   * Returns -1 if no valid RSS calculation is available yet.
   *
   * The PHY layer driver for wifi is required to keep a copy of the latest
   * WifiMode it's currently operating on, for the interference helper to
   * calculate RSS. Implementation of callbacks is specific to the PHY layer
   * protocol. However the callback's format is generic and applicable for
   * different wireless protocols (PHY classes).
   */
  UtilityRssCallback m_rssMeasurementCallback;
  /**
   * Callback for sending a packet out through the PHY layer. 
   * 
   * Implementation of callbacks is specific to the PHY layer protocol. However
   * the callback's format is generic and applicable for different wireless
   * protocols (PHY classes).
   */
  UtilitySendPacketCallback m_sendPacketCallback;
  /**
   * Callback for switching channels in PHY.
   *
   * Implementation of callbacks is specific to the PHY. However the callback's
   * format is generic and applicable for different wireless protocols (PHY
   * classes). Note that this callback should not be set if channel switch is
   * not supported by the PHY.
   */
  UtilityChannelSwitchCallback m_channelSwitchCallback;
   /**
   * Callback to handle start of RX, used by jammers.
   */
  UtilityRxCallback m_startRxCallback;
  /**
   * Callback for packet handler in jammer or jamming mitigation.
   */
 // UtilityRxCallback m_endRxCallback;
// WifiMacHeader m_machdr;
};

}
#endif