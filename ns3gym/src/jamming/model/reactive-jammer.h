#ifndef REACTIVE_JAMMER_H
#define REACTIVE_JAMMER_H

#include "jammer.h"
#include "ns3/nstime.h"
#include "ns3/event-id.h"

namespace ns3 {

/**
 * Reactive Jammer.
 */
class ReactiveJammer : public Jammer
{
public:
  /**
   * Available reaction strategies for reactive jammer.
   */
  enum ReactionStrategy {
    ENERGY_AWARE = 0,	// Uses energy fraction as probability of jamming, not used yet
    FIXED_PROBABILITY = 1	// Uses a fixed probability of jamming
  };
  
  static TypeId GetTypeId (void);
  ReactiveJammer ();
  virtual ~ReactiveJammer ();

  /**
   * \brief Sets pointer to WirelessModuleUtility installed on node..
   *
   * \param utility Pointer to WirelessModuleUtility.
   */
  virtual void SetUtility (Ptr<WirelessModuleUtility> utility);

  // setter & getters of attributes
  void SetTxPower (double power);
  double GetTxPower (void) const;
  void SetJammingDuration (Time duration);
  Time GetJammingDuration (void) const;
  void SetRxTxSwitchingDelay (Time interval);
  Time GetRxTxSwitchingDelay (void) const;
  void SetReactionStrategy(ReactionStrategy strategy);
  uint32_t GetReactionStrategy(void) const;
  void SetFixedProbability(double probability);
  double GetFixedProbability (void) const;
  void SetRxTimeout (Time rxTimeout);
  Time GetRxTimeout (void) const;
  void SetReactToMitigation (const bool flag);
  bool GetReactToMitigation (void) const;


private:
  void DoDispose (void);

  /**
   * Stops jammer.
   */
  virtual void DoStopJammer (void);

  /**
   * Sends out jamming burst at random interval.
   */
  virtual void DoJamming (void);

  /**
   * \brief Handles start RX event.
   *
   * \param packet Pointer to incoming packet.
   * \param startRss Start RSS of packet.
   * \return False. Reactive jammer will *always* ignore incoming packets.
   */
  virtual bool DoStartRxHandler (Ptr<WifiPpdu> ppdu, double startRss);

  /**
   * \brief Handles incoming packet.
   *
   * \param packet Pointer to incoming packet.
   * \param averageRss Average RSS of packet.
   * \returns False. For reactive jammer, it will discard incoming packet.
   */
 // virtual bool DoEndRxHandler (Ptr<Packet> packet, double averageRss);

  /**
   * \brief Notifies jammer of end of sending jamming signal
   *
   * \param packet Pointer to dummy packet that was sent
   * \param txPower Transmit power of packet.
   *
   * For reactive jammer, this method is empty.
   */
  virtual void DoEndTxHandler (Ptr<Packet> packet, double txPower);

  /**
   * \param packet Target packet.
   * \returns True if current packet is to be jammed.
   * 
   * This function decides (probabilistic decision) if the current packet is to
   * be jammed based on the ReactionStrategy selected.
   */
  bool IsPacketToBeJammed (Ptr<const WifiPsdu> psdu) const;
  
  /**
   * \brief Reacts to packet by sending jamming signal.
   *
   * This function sends the jamming signal.
   */
  void ReactToPacket (void);

  /**
   * Handles RX timeout event by hopping onto next channel.
   */
  void RxTimeoutHandler (void);

private:
  Ptr<WirelessModuleUtility> m_utility;

  Time m_rxTxSwitchingDelay;  // Delay to switch from Rx to Tx
  double m_txPower;           // TX power
  Time m_jammingDuration;     // jamming duration
  EventId m_jammingEvent;     // jamming event
  ReactionStrategy m_reactionStrategy; // Reaction strategy used by the jammer.
  double m_fixedProbability;	// Used for FIXED_PROBABILITY reaction strategy
  Ptr<UniformRandomVariable> m_random;	  // Used for making probabilistic decisions for reacting to a packet
  Time m_rxTimeout;           // RX timeout interval
  EventId m_rxTimeoutEvent;   // RX timeout event
  bool m_reactToMitigation;   // true if jammer is reacting to mitigation

};

} // namespace ns3

#endif /* REACTIVE_JAMMER_H */
