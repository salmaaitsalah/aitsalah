#ifndef JAMMERWIFIPHY_H
#define JAMMERWIFIPHY_H

#include "ns3/yans-wifi-phy.h"
#include "ns3/wifi-ppdu.h"
#include "ns3/interference-helper.h"
#include "ns3/node.h"
#include "nsl-wifi-channel.h"

#include "wireless-module-utility.h"

namespace ns3 {
class NslWifiChannel;
class WifiPpdu;



class JammerWifiPhy : public YansWifiPhy
{
public:
    static TypeId GetTypeId (void);
    JammerWifiPhy();
    virtual ~JammerWifiPhy();

    virtual void StartReceivePreamble (Ptr<WifiPpdu> ppdu, double rxPowerW);
    double MeasureRss (void);
    void SetCurrentWifiTxVector (WifiTxVector txVector);
    void SetNode (Ptr<Node> nodePtr);
    void UtilitySendPacket(Ptr<WifiPsdu> psdu, double &powerW, int utilitySendMode);
    void UpdatePhyLayerInfo (void);
    void SendPacket(Ptr<WifiPsdu> psdu, WifiTxVector txvector, double power);


  //  void EndReceive(Ptr<Event> event);
    /*
     * Driver functions.
     */
    void DoStart (void);
private:
    /**
     * Resets driver. Called at DoDispose.
     */
    void ResetDriver (void);
    /**
     * Initializes driver. Setting pointers to utility and energy model.
     */
    void InitDriver (void);

    /**
     * \brief Driver function invoked at start of TX.
     *
     * \param packet Pointer to packet being sent.
     * \param txPower TX power.
     *
     * This function is called at SendPacket, for interfacing with the energy and
     * utility modules.
     */
   // void DriverStartTx (Ptr<const WifiPpdu> ppdu, double txPower);

    /**
     * \brief Driver functions invoked at end of TX, scheduled by DriverStartTx.
     *
     * \param packet Pointer to packet being sent.
     * \param txPower TX power used for transmission.
     */
    void DriverEndTx (Ptr<const Packet> packet, double txPower);

    /**
     * \brief Driver function invoked at start of RX.
     *
     * \param packet Pointer to packet being received.
     * \param startRssW RSS reading at start of the packet, in Watts.
     * \returns True if the packet is to be received, false if we are to skip the
     * packet (eg. reactive jammer).
     */
    bool DriverStartRx (Ptr<WifiPpdu> ppdu, double startRssW);

    /**
     * \brief Driver function invoked at end of RX.
     *
     * \param packet Pointer to packet received.
     * \param averageRssW Average RSS for the received packet, in Watts.
     * \param isSuccessfullyReceived True if packet is successfully received.
     */
 //   void DriverEndRx (Ptr<Packet> packet, double averageRssW,
 //                     const bool isSuccessfullyReceived);
    bool m_isDriverInitialized; // flag indicating if driver is initialized
    Ptr<Node> m_node;           // pointer to the node where the PHY is installed
    Ptr<WirelessModuleUtility> m_utility; // pointer to utility object

    WifiTxVector m_currentWifiTxVector;
    WirelessModuleUtility::PhyLayerInfo m_phyLayerInfo; // PHY layer info
    Ptr<NslWifiChannel> m_channel;
};
}

#endif // JAMMERWIFIPHY_H
