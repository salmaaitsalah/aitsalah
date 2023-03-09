#ifndef DATACOLLECTION_MODULE_UTILITY_H
#define DATACOLLECTION_MODULE_UTILITY_H

#include "ns3/callback.h"
#include "ns3/object.h"
#include "ns3/nstime.h"
#include "ns3/wifi-phy-state-helper.h"
#include "ns3/wifi-phy.h"
#include "ns3/wave-net-device.h"
#include "wireless-module-utility.h"
#include "ns3/mobility-model.h"

namespace ns3 {
class MobilityModel;
class DataCollectionModuleUtility : public Object
{
public:
  /**
       * \brief Get the type ID.
       * \return the object TypeId
       */
  static TypeId GetTypeId (void);
  DataCollectionModuleUtility ();
  typedef struct state
  {
    Time s_start = Seconds (0); //time that a state start
    Time s_end = Seconds (0); //time that a state end
    WifiPhyState s; //enum wifiphystate(Tx,Rx,CCA_busy,...)
  } state;
  // typedef struct
  //     DATUM //data collected at each node (nodeid, #successful rx, #error rx, #tx (time slots), state of the medium, minRSS, maxRSS ) each CCHI
  // {
  //   uint32_t nodeid = 0; //node id
  //   uint32_t ls = 0; //number of successful rxok slots
  //   uint32_t lc = 0; //number failed rx slots
  //   uint32_t le = 0; //number of error rx slots (failed due to multi mpdu receiving fail)
  //   uint32_t ltx = 0; // number tx slots
  //   std::list<state> m_s; //state of this CCHI
  //   double minRxOkPowerW =
  //       0; // minimum RX power for PHY layer in Watts currently is snr in replacement
  //   double maxRxOkPowerW = 0; // maximum RX power for PHY layer in Watts
  //   uint16_t currentChannel = 0; // current channel number
  //   uint32_t contentionwindowid = 1; // cw sequencial number
  //   uint32_t m_numberofNeighbor = 0;
  //   bool m_jammed = 0;
  // } datum;
  class datum : public ns3::Object
  {
    //data collected at each node (nodeid, #successful rx, #error rx, #tx (time slots), state of the medium, minRSS, maxRSS ) each CCHI
  public:
    uint32_t nodeid = 0; //node id
    uint32_t ls = 0; //number of successful rxok slots
    uint32_t lc = 0; //number failed rx slots
    uint32_t le = 0; //number of error rx slots (failed due to multi mpdu receiving fail)
    uint32_t ltx = 0; // number tx slots
    std::list<state> m_s; //state of this CCHI
    double minRxOkPowerW =
        0; // minimum RX power for PHY layer in Watts currently is snr in replacement
    double maxRxOkPowerW = 0; // maximum RX power for PHY layer in Watts
    uint16_t currentChannel = 0; // current channel number
    uint32_t contentionwindowid = 1; // cw sequencial number
    uint32_t m_numberofNeighbor = 0;
    bool m_jammed = 0;

    bool
    operator!= (datum other)
    {
      return this->contentionwindowid != other.contentionwindowid;
    }
  };
  Ptr<WaveNetDevice> m_netdevice; //netdevice of the node where this utiltiy is installed

  // DONE: Change this to a list of Ptr
  Ptr<WirelessModuleUtility>
      m_Wutility; // pointer to wirelessmoduleutility object that is defined in jamming module
  std::vector<Ptr<WirelessModuleUtility>> m_WutilityList;

  datum m_datum; // the current datum
  TracedValue<int32_t> test_value = 0;
  std::list<datum> m_dataset;
  TracedValue<datum> latest_datum;

  Vector jamposition; // DONE: Change this to be a list of vector
  std::vector<Vector> jampositionList;

  void
  SetNetDevice (Ptr<WaveNetDevice> device); //connect the utility to the netdevice of the simulation
  // DONE: Change this to receive list of w_utility
  void SetWirelessModuleUtility (Ptr<WirelessModuleUtility> w_utility);
  void SetWirelessModuleUtility (std::vector<Ptr<WirelessModuleUtility>> w_utilityList);

  // DONE: Change this to receive list of w_utility and std::vector<Vector> jpos
  bool InitialDataCollectionUtility (
      Ptr<WaveNetDevice> device, Ptr<WirelessModuleUtility> w_utility,
      Vector jpos); //SetNetDevice, setreceivecallback to link this utility to phy and state

  bool InitialDataCollectionUtility (
      Ptr<WaveNetDevice> device, std::vector<Ptr<WirelessModuleUtility>> w_utilityList,
      std::vector<Vector>
          jposList); //SetNetDevice, setreceivecallback to link this utility to phy and state

  void UpdateRxPowerofDatum (double snr);
  void ResetAfterSwitching (void);
  void UpdateChannelNumber (void);
  bool CheckChannelSwitching (state statelogger);
  void UpdateNeighborList (uint32_t number);
  // Trace functions
  void TraceFunction_RxOk (Ptr<const Packet>, double, WifiMode, WifiPreamble); //m_rxOkCallback
  void TraceFunction_RxDrop (Ptr<const Packet> p, WifiPhyRxfailureReason reason);
  void TraceFunction_RxError (Ptr<const Packet>, double);
  void TraceFunction_Tx (Ptr<const Packet> p);
  void TraceFunction_StateLogger (Time start, Time duration, WifiPhyState state);
  void TraceFunction_Jammer (Ptr<WifiPsdu> psdu, double &powerW, int utilitySendMode);

  //print out
  void PrintOutStateObserveeachCW (
      std::string
          logfile); // Medium observation in each CW, be called at the end of each cw when switching from CCHI to SCHI
  void PrintOut (
      std::string
          logfile); // log file of observations of all cw by a node, be called at the end of the simulation
};
} // namespace ns3
#endif
