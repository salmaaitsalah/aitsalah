#ifndef NSL_WIFI_HELPER
#define NSL_WIFI_HELPER

#include "ns3/wifi-helper.h"
#include "ns3/trace-helper.h"
#include "ns3/nsl-wifi-channel.h"
#include "ns3/deprecated.h"

namespace ns3 {

/**
 * This class is identical to the YansWifiChannelHelper.
 */
class NslWifiChannelHelper
{
public:
  /**
   * Create a channel helper without any parameter set. The user must set
   * them all to be able to call Create later.
   */
  NslWifiChannelHelper ();

  /**
   * Create a channel helper in a default working state. By default, we create
   * a channel model with a propagation delay equal to a constant, the speed of
   * light, and a propagation loss based on a log distance model with a
   * reference loss of 46.6777 dB at reference distance of 1m.
   */
  static NslWifiChannelHelper Default (void);

  /**
   * \param name the name of the model to add
   * \param n0 the name of the attribute to set
   * \param v0 the value of the attribute to set
   * \param n1 the name of the attribute to set
   * \param v1 the value of the attribute to set
   * \param n2 the name of the attribute to set
   * \param v2 the value of the attribute to set
   * \param n3 the name of the attribute to set
   * \param v3 the value of the attribute to set
   * \param n4 the name of the attribute to set
   * \param v4 the value of the attribute to set
   * \param n5 the name of the attribute to set
   * \param v5 the value of the attribute to set
   * \param n6 the name of the attribute to set
   * \param v6 the value of the attribute to set
   * \param n7 the name of the attribute to set
   * \param v7 the value of the attribute to set
   *
   * Add a propagation loss model to the set of currently-configured loss
   * models. This method is additive to allow you to construct complex
   * propagation loss models such as a log distance + jakes model, etc.
   */
  void AddPropagationLoss (std::string name,
      std::string n0 = "", const AttributeValue &v0 = EmptyAttributeValue (),
      std::string n1 = "", const AttributeValue &v1 = EmptyAttributeValue (),
      std::string n2 = "", const AttributeValue &v2 = EmptyAttributeValue (),
      std::string n3 = "", const AttributeValue &v3 = EmptyAttributeValue (),
      std::string n4 = "", const AttributeValue &v4 = EmptyAttributeValue (),
      std::string n5 = "", const AttributeValue &v5 = EmptyAttributeValue (),
      std::string n6 = "", const AttributeValue &v6 = EmptyAttributeValue (),
      std::string n7 = "", const AttributeValue &v7 = EmptyAttributeValue ());
  /**
   * \param name the name of the model to set
   * \param n0 the name of the attribute to set
   * \param v0 the value of the attribute to set
   * \param n1 the name of the attribute to set
   * \param v1 the value of the attribute to set
   * \param n2 the name of the attribute to set
   * \param v2 the value of the attribute to set
   * \param n3 the name of the attribute to set
   * \param v3 the value of the attribute to set
   * \param n4 the name of the attribute to set
   * \param v4 the value of the attribute to set
   * \param n5 the name of the attribute to set
   * \param v5 the value of the attribute to set
   * \param n6 the name of the attribute to set
   * \param v6 the value of the attribute to set
   * \param n7 the name of the attribute to set
   * \param v7 the value of the attribute to set
   *
   * Configure a propagation delay for this channel.
   */
  void SetPropagationDelay (std::string name,
      std::string n0 = "", const AttributeValue &v0 = EmptyAttributeValue (),
      std::string n1 = "", const AttributeValue &v1 = EmptyAttributeValue (),
      std::string n2 = "", const AttributeValue &v2 = EmptyAttributeValue (),
      std::string n3 = "", const AttributeValue &v3 = EmptyAttributeValue (),
      std::string n4 = "", const AttributeValue &v4 = EmptyAttributeValue (),
      std::string n5 = "", const AttributeValue &v5 = EmptyAttributeValue (),
      std::string n6 = "", const AttributeValue &v6 = EmptyAttributeValue (),
      std::string n7 = "", const AttributeValue &v7 = EmptyAttributeValue ());

  /**
   * \returns a new channel
   *
   * Create a channel based on the configuration parameters set previously.
   */
  Ptr<NslWifiChannel> Create (void) const;

private:
  std::vector<ObjectFactory> m_propagationLoss;
  ObjectFactory m_propagationDelay;
};

//----------------------------------------------------------------------------//

/**
 * \brief Make it easy to create and manage NslPhy objects. This class is
 * identical to the YansWifiPhyHelper
 */
class JammerWifiPhyHelper : public WifiPhyHelper
{
public:
  /**
   * Create a phy helper without any parameter set. The user must set
   * them all to be able to call Install later.
   */
  JammerWifiPhyHelper ();
/**
   * Create a PHY helper in a default working state.
   * \returns a default YansWifiPhyHelper
   */
  static JammerWifiPhyHelper Default (void);
   /**
   * \param channel the channel to associate to this helper
   *
   * Every PHY created by a call to Install is associated to this channel.
   */
  void SetChannel (Ptr<NslWifiChannel> channel);
  /**
   * \param channelName The name of the channel to associate to this helper
   *
   * Every PHY created by a call to Install is associated to this channel.
   */
  void SetChannel (std::string channelName);
private:
  /**
   * \param node the node on which we wish to create a wifi PHY
   * \param device the device within which this PHY will be created
   * \returns a newly-created PHY object.
   *
   * This method implements the pure virtual method defined in \ref ns3::WifiPhyHelper.
   */
  virtual Ptr<WifiPhy> Create (Ptr<Node> node, Ptr<NetDevice> device) const;

  


  Ptr<NslWifiChannel> m_channel;

};

} // namespace ns3

#endif /* NSL_WIFI_HELPER */
